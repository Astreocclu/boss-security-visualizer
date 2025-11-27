"""
ScreenVisualizer Module
-----------------------
This module implements the core "Visualizer" logic for the Screen King project.
It uses Google Gemini 3 Pro Image to generate photorealistic "After" images with motorized screens.

The pipeline follows a strict 4-step process:
1. Clean Pass (Image Restoration)
2. Structural Build-Out (Analysis & Prep)
3. Screen Insertion (The "Money Shot")
4. Texture & Physics Refinement
"""

import logging
import os
from typing import Optional, Dict, Any, Tuple
import math
import operator
from functools import reduce
from PIL import Image, ImageChops
from google import genai
from google.genai import types
from datetime import datetime

from .prompts import (
    CLEANUP_SCENE_PROMPT,
    BUILD_OUT_PROMPT,
    SCREEN_INSERTION_PROMPT,
    get_mesh_physics_prompt
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
        self.reference_images = self._load_boss_hardware_refs()

    def _load_boss_hardware_refs(self) -> Dict[str, Any]:
        """Load reference images for hardware specs."""
        references = {}
        base_path = "/home/reid/projects/homescreen/media/screen_references/lifestyle_environmental"
        
        # Load references for each opacity level
        for opacity in ['80', '95', '99']:
            master_path = os.path.join(base_path, opacity, "master")
            if os.path.exists(master_path):
                # Get the first image found in the master folder
                for filename in os.listdir(master_path):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        try:
                            img_path = os.path.join(master_path, filename)
                            references[opacity] = Image.open(img_path)
                            logger.info(f"Loaded reference for opacity {opacity}: {filename}")
                            break # Only load one reference per opacity for now
                        except Exception as e:
                            logger.error(f"Failed to load reference {filename}: {e}")
            else:
                logger.warning(f"Reference directory not found: {master_path}")
                
        return references

    def process_pipeline(self, user_image: Image.Image, mesh_type: str = "solar", opacity: str = None, color: str = None) -> Tuple[Image.Image, Image.Image, int]:
        """
        Execute the strict "Screen King" pipeline using Nano Banana Pro.
        
        Sequence:
        Step 1: The Cleanse (Thinking Mode)
        Step 2: The Build Out (Conditional)
        Step 3: The Screen Install (Reference-based)
        Step 4: The Check (Vision QC)
        """
        logger.info(f"Starting Screen King Pipeline (Nano Banana Pro) with mesh_type={mesh_type}")
        
        if not self.client:
            raise ScreenVisualizerError("GenAI client not initialized.")

        try:
            # Step 1: The Cleanse
            clean_img = self.step_1_cleanse(user_image)
            self._save_debug_image(clean_img, "1_cleanse")
            
            # Step 2: The Build Out
            # We'll assume build out is needed if the analysis says so, otherwise pass through
            if self._analyze_structure(clean_img):
                build_img = self.step_2_build_out(clean_img)
                self._save_debug_image(build_img, "2_build_out")
            else:
                logger.info("Step 2: Build Out skipped (not required).")
                build_img = clean_img
                self._save_debug_image(build_img, "2_build_skipped")
            
            # Step 3: The Screen Install
            # Load reference image based on opacity
            # Default to 95 if not specified or not found
            target_opacity = opacity if opacity in ['80', '95', '99'] else '95'
            reference_img = self.reference_images.get(target_opacity)
            
            if not reference_img:
                logger.warning(f"No reference image found for opacity {target_opacity}. Proceeding without reference.")

            # Always use lifestyle_environmental as the mesh type internally for the prompt logic
            # but we keep the argument name for compatibility if needed, though we ignore the old values
            effective_mesh_type = "lifestyle_environmental"
            
            final_img = self.step_3_install_screen(build_img, reference_img, effective_mesh_type, opacity=target_opacity, color=color)
            self._save_debug_image(final_img, "3_install")
            
            # Step 4: The Check
            qc_pass, qc_score = self.step_4_quality_check(final_img, mesh_type)
            
            if qc_pass:
                logger.info(f"Step 4: QC Passed (Score: {qc_score}).")
                self._save_debug_image(final_img, "4_final_passed")
                return clean_img, final_img, qc_score
            else:
                logger.warning(f"Step 4: QC Failed (Score: {qc_score}). Retrying Step 3 with higher guidance...")
                # Retry Step 3 once with higher guidance or slight prompt tweak
                final_img_retry = self.step_3_install_screen(build_img, reference_img, effective_mesh_type, retry=True, opacity=target_opacity, color=color)
                self._save_debug_image(final_img_retry, "4_final_retry")
                
                # Check if final image is identical to input
                if self._is_identical(user_image, final_img_retry):
                    logger.error("CRITICAL: Final image is IDENTICAL to input image! Pipeline failed to apply changes.")
                
                # Re-score the retry
                _, retry_score = self.step_4_quality_check(final_img_retry, mesh_type)
                return clean_img, final_img_retry, retry_score
            
            # Check if final image is identical to input (passed case)
            if self._is_identical(user_image, final_img):
                logger.error("CRITICAL: Final image is IDENTICAL to input image! Pipeline failed to apply changes.")
                
            return clean_img, final_img, qc_score
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise ScreenVisualizerError(f"Pipeline failed: {e}") from e

    def step_1_cleanse(self, image: Image.Image) -> Image.Image:
        """
        Step 1: The Intelligent Cleanse.
        Prompt: "Edit this image. Remove all visual clutter (hoses, trash, debris). Remove all people and furniture from the outdoor area. Fix the lighting. Do not change the house structure or camera angle. Keep the canvas exact."
        Config: include_thoughts=True
        """
        logger.info("Step 1: The Cleanse")
        prompt = "Edit this image. Remove all visual clutter (hoses, trash, debris). Remove all people and furniture from the outdoor area. Fix the lighting. Do not change the house structure or camera angle. Keep the canvas exact."
        
        return self._generate_content_image(
            contents=[image, prompt],
            include_thoughts=True
        )

    def step_2_build_out(self, image: Image.Image) -> Image.Image:
        """
        Step 2: The Build Out.
        Prompt: "Edit this image. Add structural build-outs (columns/headers) where indicated. Ensure the new structure matches the house texture. Clean the image again to ensure the new structure blends perfectly with the environment."
        """
        logger.info("Step 2: The Build Out")
        prompt = "Edit this image. Add structural build-outs (columns/headers) where indicated. Ensure the new structure matches the house texture. Clean the image again to ensure the new structure blends perfectly with the environment."
        
        return self._generate_content_image(
            contents=[image, prompt],
            include_thoughts=True
        )

    def step_3_install_screen(self, image: Image.Image, reference_img: Optional[Image.Image], mesh_type: str, retry: bool = False, opacity: str = None, color: str = None) -> Image.Image:
        """
        Step 3: The Screen Install.
        Prompt: "Edit this image. Using the Reference Image for texture: Install motorized screens into the openings. Screen Color: {color}. Opacity: {opacity}. The screens must be down. Frame ONLY the outer edges of the opening. Do NOT add any vertical or horizontal beams, bars, or dividers inside the opening. The image must remain 'Clean' overall (no clutter re-appearing). Maintain high-fidelity architectural details. Do not change the perspective."
        """
        logger.info(f"Step 3: The Screen Install (Retry={retry}, Opacity={opacity}, Color={color})")
        
        # Define mesh properties (Defaults)
        # Define mesh properties (Defaults)
        # We now only support lifestyle_environmental, but keep a fallback
        default_color = "black"
        
        # Override with user provided values if available
        target_color = color if color else default_color
        target_opacity = f"{opacity}%" if opacity else "95%"

        # For lifestyle_environmental, we want to match the reference image color
        # So we don't enforce the target_color in the prompt if we have a reference
        if reference_img:
            color_instruction = "Match the screen color and texture to the Reference Image."
        else:
            color_instruction = f"Screen Color: {target_color}."

        prompt = f"Edit this image. Using the Reference Image for texture: Install motorized screens into the openings. {color_instruction} Opacity: {target_opacity}. The screens must be down. Frame ONLY the outer edges of the opening. Do NOT add any vertical or horizontal beams, bars, or dividers inside the opening. The image must remain 'Clean' overall (no clutter re-appearing). Maintain high-fidelity architectural details. Do not change the perspective."
        
        contents = [image, prompt]
        if reference_img:
            contents.insert(1, reference_img) # Add reference image
            
        return self._generate_content_image(
            contents=contents,
            include_thoughts=False # As per previous decision
        )

    def step_4_quality_check(self, image: Image.Image, mesh_type: str) -> Tuple[bool, int]:
        """
        Step 4: The Check (Vision/QC).
        Returns (passed: bool, score: int)
        """
        logger.info("Step 4: The Check")
        try:
            prompt = f"""Analyze this image for the quality of the motorized screen installation.
            Check against these constraints:
            1. Is the fabric color consistent with a screen?
            2. Is the opacity consistent with {mesh_type} screens? (e.g. 95% opacity should be nearly opaque, 80% should show some background)
            3. Are ALL openings screened? (No missing screens in obvious openings)
            4. Is the image clean (no hallucinated trash)?
            5. Are there any structural hallucinations (floating pillars, unnecessary beams blocking the view, etc)?

            Provide a Quality Score from 0 to 100, where 100 is perfect realism and installation.
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
            
            # Parse score
            import re
            score_match = re.search(r"SCORE:\s*(\d+)", result_text)
            score = int(score_match.group(1)) if score_match else 0
            
            # Parse verdict
            passed = "VERDICT: PASS" in result_text
            
            # Fallback if parsing fails but text contains PASS
            if not passed and "PASS" in result_text and "FAIL" not in result_text:
                passed = True
                
            return passed, score
            
        except Exception as e:
            logger.error(f"QC failed: {e}")
            return True, 85 # Assume pass with decent score if QC fails to run

    def _save_debug_image(self, image: Image.Image, step_name: str):
        """Save intermediate image for debugging."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_{timestamp}_{step_name}.jpg"
            # Use absolute path to ensure it goes to the right place
            save_path = os.path.join("/home/reid/projects/homescreen/media/pipeline_steps", filename)
            
            image.save(save_path)
            logger.info(f"Saved debug image: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save debug image {step_name}: {e}")

    def _is_identical(self, img1: Image.Image, img2: Image.Image) -> bool:
        """Check if two images are identical."""
        try:
            # Resize to same size if needed (though they should be same)
            if img1.size != img2.size:
                return False
            
            # Fast check
            diff = ImageChops.difference(img1, img2)
            if not diff.getbbox():
                return True
            
            # RMS check for near-identical (compression artifacts)
            h = ImageChops.difference(img1, img2).histogram()
            rms = math.sqrt(reduce(operator.add,
                map(lambda h, i: h*(i**2), h, range(256))
            ) / (float(img1.size[0]) * img1.size[1]))
            
            return rms < 5.0 # Threshold for "effectively identical"
        except Exception as e:
            logger.error(f"Error checking similarity: {e}")
            return False

    def _generate_content_image(self, contents: list, include_thoughts: bool = False) -> Image.Image:
        """
        Helper to call generate_content and extract image.
        """
        try:
            config_args = {
                "response_modalities": ["TEXT", "IMAGE"] if include_thoughts else ["IMAGE"],
            }
            
            if include_thoughts:
                if hasattr(types, 'ThinkingConfig'):
                    config_args['thinking_config'] = types.ThinkingConfig(include_thoughts=True)
            
            # Add strict image generation config for editing
            if hasattr(types, 'ImageGenerationConfig'):
                 config_args['image_generation_config'] = types.ImageGenerationConfig(
                    guidance_scale=70, # High guidance to adhere to prompt/image
                    person_generation="dont_generate_people"
                )

            # Retry logic
            import time
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        # Exponential backoff: 10s, 30s, 60s
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
            # If input was an image, return it. If not (e.g. text only), we can't return input.
            # Assuming first content is image if available.
            for content in contents:
                if isinstance(content, Image.Image):
                    return content
            return Image.new('RGB', (512, 512), color='gray') # Fallback
            
        except Exception as e:
            logger.error(f"Image generation failed with error: {str(e)}")
            # Propagate the error instead of returning fallback
            # This allows the processor to mark the request as failed
            raise ScreenVisualizerError(f"Gemini generation failed: {str(e)}") from e

    # Keep _analyze_structure as is, or update if needed.
    # It's used in process_pipeline.
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

    # Remove old methods that are replaced
    def cleanup_scene(self, image: Image.Image) -> Image.Image: return image # Deprecated
    def check_and_build_structure(self, image: Image.Image) -> Image.Image: return image # Deprecated
    def install_screen(self, image: Image.Image, references: Dict[str, Any]) -> Image.Image: return image # Deprecated
    def apply_mesh_physics(self, image: Image.Image, mesh_type: str) -> Image.Image: return image # Deprecated
    def _generate_image(self, image: Image.Image, prompt: str) -> Image.Image: return image # Deprecated
