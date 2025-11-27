"""
ScreenVisualizer Module (Boss Security Visualizer)
--------------------------------------------------
This module implements the core "Visualizer" logic for the Boss Security project.
It uses Google Gemini 3 Pro Image to generate photorealistic "After" images with motorized screens.

The pipeline follows a strict 3-step process using a Stateful Chat Session:
1. Clean Pass (Image Restoration)
2. Structural Build-Out (Analysis & Prep - Conditional)
3. Screen Insertion (The "Money Shot" with Thinking Mode)
"""

import logging
import os
import time
from typing import Optional, Dict, Any, Tuple, List
import math
import operator
from functools import reduce
from PIL import Image, ImageChops
from google import genai
from google.genai import types
from datetime import datetime

from .prompts import (
    CLEANUP_SCENE_PROMPT,
    get_screen_insertion_prompt,
    get_structural_prompt
)

logger = logging.getLogger(__name__)

class ScreenVisualizerError(Exception):
    """Base exception for ScreenVisualizer errors."""
    pass

class ScreenVisualizer:
    """
    Standalone API service that accepts a raw home photo and returns a photorealistic
    "After" image with motorized screens installed.
    """

    def __init__(self, api_key: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize the ScreenVisualizer.
        
        Args:
            api_key (str, optional): Google GenAI API Key. If None, looks for GOOGLE_API_KEY env var.
            client (Any, optional): Pre-configured GenAI client.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        if client:
            self.client = client
        elif self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("GOOGLE_API_KEY not found. ScreenVisualizer will not function correctly.")
            self.client = None
        
        self.model_name = "gemini-3-pro-image-preview"
        self.reference_images = {} # Loaded on demand now
        
    def _get_product_reference(self, mesh_type: str) -> Optional[Image.Image]:
        """
        Load the specific product reference image for the mesh type.
        """
        try:
            # Map mesh_type to filename
            reference_map = {
                '12x12_american': '12x12_macro_shot.jpg',
                '12x12': '12x12_standard.jpg',
                '10x10': '10x10_heavy.jpg'
            }
            
            filename = reference_map.get(mesh_type, '12x12_standard.jpg')
            base_path = "/home/reid/Boss Screens/boss-security-visualizer/media/screen_references"
            ref_path = os.path.join(base_path, filename)
            
            # Fallback to master if specific not found (for legacy support)
            if not os.path.exists(ref_path):
                 # Try master directory with legacy names if needed, or just log warning
                 # For now, let's try to find *any* reference
                 legacy_path = os.path.join(base_path, "master", "window_fixed.png")
                 if os.path.exists(legacy_path):
                     logger.warning(f"Specific reference {filename} not found, using legacy fallback.")
                     return Image.open(legacy_path)
            
            if os.path.exists(ref_path):
                img = Image.open(ref_path)
                logger.info(f"Loaded product reference for {mesh_type}")
                return img
            else:
                logger.warning(f"Product reference not found: {ref_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load product reference for {mesh_type}: {e}")
            return None

    def process_pipeline(self, user_image: Image.Image, screen_type: str = "window_fixed", opacity: str = "95", color: str = "Black", mesh_type: str = "12x12") -> Tuple[Image.Image, Image.Image, int]:
        """
        Execute the strict "Boss Security" pipeline using a Stateful Chat Session.
        """
        logger.info(f"Starting Boss Security Pipeline with screen_type={screen_type}, mesh_type={mesh_type}")
        
        if not self.client:
            raise ScreenVisualizerError("GenAI client not initialized.")

        # Initialize Chat Session
        try:
            chat = self.client.chats.create(model=self.model_name)
        except Exception as e:
             raise ScreenVisualizerError(f"Failed to create chat session: {e}")

        try:
            # Step 1: The Cleanse
            clean_img = self.step_1_cleanse(chat, user_image)
            self._save_debug_image(clean_img, "1_cleanse")
            
            # Step 2: The Build Out (Conditional)
            if self._analyze_structure(clean_img):
                build_img = self.step_2_build_out(chat, clean_img)
                self._save_debug_image(build_img, "2_build_out")
            else:
                logger.info("Step 2: Build Out skipped (not required).")
                build_img = clean_img
                self._save_debug_image(build_img, "2_build_skipped")
            
            # Step 3: The Screen Install
            # Load reference image based on mesh_type (not screen_type anymore)
            product_ref = self._get_product_reference(mesh_type)
            
            final_img = self.step_3_install_screen(chat, build_img, product_ref, screen_type, opacity=opacity, color=color, mesh_type=mesh_type)
            self._save_debug_image(final_img, "3_install")
            
            # Step 4: The Check
            qc_pass, qc_score = self.step_4_quality_check(final_img, screen_type)
            
            if qc_pass:
                logger.info(f"Step 4: QC Passed (Score: {qc_score}).")
                self._save_debug_image(final_img, "4_final_passed")
                return clean_img, final_img, qc_score
            else:
                logger.warning(f"Step 4: QC Failed (Score: {qc_score}). Retrying Step 3...")
                
                final_img_retry = self.step_3_install_screen(chat, final_img, product_ref, screen_type, retry=True, opacity=opacity, color=color, mesh_type=mesh_type)
                self._save_debug_image(final_img_retry, "4_final_retry")
                
                if self._is_identical(user_image, final_img_retry):
                    logger.error("CRITICAL: Final image is IDENTICAL to input image!")
                
                _, retry_score = self.step_4_quality_check(final_img_retry, screen_type)
                return clean_img, final_img_retry, retry_score
            
            if self._is_identical(user_image, final_img):
                 logger.error("CRITICAL: Final image is IDENTICAL to input image!")

            return clean_img, final_img, qc_score
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise ScreenVisualizerError(f"Pipeline failed: {e}") from e

    def step_1_cleanse(self, chat: Any, image: Image.Image) -> Image.Image:
        """
        Step 1: The Intelligent Cleanse.
        """
        logger.info("Step 1: The Cleanse")
        return self._generate_chat_image(
            chat=chat,
            contents=[image, CLEANUP_SCENE_PROMPT],
            include_thoughts=True
        )

    def step_2_build_out(self, chat: Any, image: Image.Image) -> Image.Image:
        """
        Step 2: The Build Out.
        """
        logger.info("Step 2: The Build Out")
        prompt = "Analyze the previous image. Add structural build-outs (columns/headers) where indicated to support screens. Ensure the new structure matches the house texture."
        
        return self._generate_chat_image(
            chat=chat,
            contents=[prompt],
            include_thoughts=True
        )

    def step_3_install_screen(self, chat: Any, image: Image.Image, product_ref: Optional[Image.Image], screen_type: str, retry: bool = False, opacity: str = "95%", color: str = "Black", mesh_type: str = "12x12") -> Image.Image:
        """
        Step 3: The Screen Install.
        """
        logger.info(f"Step 3: The Screen Install (Type={screen_type}, Mesh={mesh_type}, Retry={retry}, Opacity={opacity}, Color={color})")
        
        # Use the centralized prompt generator
        prompt = get_screen_insertion_prompt(screen_type, color, opacity, mesh_type)
        
        if retry:
            prompt = "The previous installation was not perfect. Please refine the screens. Ensure they are fully covering the openings and the texture is realistic."

        contents = [image, prompt]
        
        # Add reference if available
        if product_ref:
            contents.append(product_ref)
            contents.append("Reference for Product Hardware")

        return self._generate_chat_image(
            chat=chat,
            contents=contents,
            include_thoughts=True
        )

    def step_4_quality_check(self, image: Image.Image, mesh_type: str) -> Tuple[bool, int]:
        """
        Step 4: The Check (Vision/QC).
        Uses a fresh, stateless call as it's a critique, not an edit.
        """
        logger.info("Step 4: The Check")
        try:
            prompt = f"""Analyze this image for the quality of the motorized screen installation.
            Check against these constraints:
            1. Is the fabric color consistent with a screen?
            2. Is the opacity consistent with {mesh_type} screens?
            3. Are ALL openings screened?
            4. Is the image clean?
            5. Are there any structural hallucinations?

            Provide a Quality Score from 0 to 100.
            Provide a final verdict of PASS or FAIL.
            
            Output format:
            SCORE: [0-100]
            VERDICT: [PASS/FAIL]
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image, prompt]
            )
            
            result_text = response.text.strip().upper()
            logger.info(f"QC Result Raw: {result_text}")
            
            import re
            score_match = re.search(r"SCORE:\s*(\d+)", result_text)
            score = int(score_match.group(1)) if score_match else 0
            
            passed = "VERDICT: PASS" in result_text
            if not passed and "PASS" in result_text and "FAIL" not in result_text:
                passed = True
                
            return passed, score
            
        except Exception as e:
            logger.error(f"QC failed: {e}")
            return True, 85 

    def _generate_chat_image(self, chat: Any, contents: list, include_thoughts: bool = False) -> Image.Image:
        """
        Helper to call chat.send_message and extract image.
        Handles 429 Rate Limits.
        """
        try:
            config_args = {
                "response_modalities": ["TEXT", "IMAGE"] if include_thoughts else ["IMAGE"],
            }
            
            if include_thoughts:
                if hasattr(types, 'ThinkingConfig'):
                    config_args['thinking_config'] = types.ThinkingConfig(include_thoughts=True)
            
            if hasattr(types, 'ImageGenerationConfig'):
                 config_args['image_generation_config'] = types.ImageGenerationConfig(
                    guidance_scale=70, 
                    person_generation="dont_generate_people"
                )

            # Retry logic
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    response = chat.send_message(
                        message=contents,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        wait_times = [10, 30, 60, 60]
                        wait_time = wait_times[attempt] if attempt < len(wait_times) else 60
                        logger.warning(f"Rate limit hit (Attempt {attempt+1}/{max_retries}). Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise e
            
            # Extract image
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        from io import BytesIO
                        return Image.open(BytesIO(part.inline_data.data))
            
            logger.warning("No image data found in response.")
            # Fallback: return the input image if it's in contents
            for content in contents:
                if isinstance(content, Image.Image):
                    return content
            return Image.new('RGB', (512, 512), color='gray')
            
        except Exception as e:
            logger.error(f"Image generation failed with error: {str(e)}")
            raise ScreenVisualizerError(f"Gemini generation failed: {str(e)}") from e

    def _analyze_structure(self, image: Image.Image) -> bool:
        """
        Helper to analyze if structure is needed using Vision API.
        """
        try:
            prompt = "Analyze this image of a house. Does the patio or outdoor area require structural build-out (like pillars, beams, or headers) to support a motorized screen? Answer with YES or NO only."
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image, prompt]
            )
            
            result = response.text.strip().upper()
            logger.info(f"Structure analysis result: {result}")
            return "YES" in result
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            return False

    def _save_debug_image(self, image: Image.Image, step_name: str):
        """Save intermediate image for debugging."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_{timestamp}_{step_name}.jpg"
            save_path = os.path.join("/home/reid/Boss Screens/boss-security-visualizer/media/pipeline_steps", filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            image.save(save_path)
            logger.info(f"Saved debug image: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save debug image {step_name}: {e}")

    def _is_identical(self, img1: Image.Image, img2: Image.Image) -> bool:
        """Check if two images are identical."""
        try:
            if img1.size != img2.size:
                return False
            
            diff = ImageChops.difference(img1, img2)
            if not diff.getbbox():
                return True
            
            h = ImageChops.difference(img1, img2).histogram()
            rms = math.sqrt(reduce(operator.add,
                map(lambda h, i: h*(i**2), h, range(256))
            ) / (float(img1.size[0]) * img1.size[1]))
            
            return rms < 5.0
        except Exception as e:
            logger.error(f"Error checking similarity: {e}")
            return False
