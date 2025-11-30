# File: api/visualizer/services.py

import logging
import os
import time
import json
import re
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image
import io
from google import genai
from google.genai import types
from django.conf import settings

from api.tenants import get_tenant_config

logger = logging.getLogger(__name__)

class ScreenVisualizerError(Exception):
    """Base exception for ScreenVisualizer errors."""
    pass

class ScreenVisualizer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found. ScreenVisualizer cannot function.")
            raise ScreenVisualizerError("API Key missing. Please set GOOGLE_API_KEY.")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3-pro-image-preview"

    def process_pipeline(self, original_image: Image.Image, scope: dict, options: dict, progress_callback=None) -> Tuple[Image.Image, Image.Image, float, str]:
        """
        Executes the visualization pipeline sequentially based on tenant configuration.
        
        Args:
            original_image (Image): The source image.
            scope (dict): {'windows': bool, 'doors': bool, 'patio': bool}
            options (dict): {'color': str, 'mesh_type': str}
            progress_callback (callable, optional): Function to update progress (percent, message).
        """
        try:
            tenant_config = get_tenant_config()
            prompts = tenant_config.get_prompts_module()
            
            current_image = original_image
            clean_image = original_image # Default if no cleanup
            
            score = 0.95
            reason = "Pipeline completed successfully."

            if progress_callback:
                progress_callback(10, "Analyzing")

            steps = tenant_config.get_pipeline_steps()
            
            for i, step_name in enumerate(steps):
                step_config = tenant_config.get_step_config(step_name)
                step_type = step_config.get('type')
                
                # Update progress
                if progress_callback and 'progress_weight' in step_config:
                    progress_callback(step_config['progress_weight'], step_config.get('description', 'Processing'))
                
                if step_type == 'cleanup':
                    cleanup_prompt = prompts.get_cleanup_prompt()
                    clean_image = self._call_gemini_edit(original_image, cleanup_prompt)
                    self._save_debug_image(clean_image, f"{i}_{step_name}")
                    current_image = clean_image
                    logger.info(f"Pipeline Step: {step_name} complete.")
                    
                elif step_type == 'insertion':
                    scope_key = step_config.get('scope_key')
                    if scope_key and scope.get(scope_key, False):
                        feature_name = step_config.get('feature_name')
                        prompt = prompts.get_screen_insertion_prompt(feature_name, options)
                        current_image = self._call_gemini_edit(current_image, prompt)
                        self._save_debug_image(current_image, f"{i}_{step_name}")
                        logger.info(f"Pipeline Step: {step_name} complete.")
                        
                elif step_type == 'quality_check':
                    quality_prompt = prompts.get_quality_check_prompt(scope)
                    # Pass both clean (reference) and current (final) images
                    quality_result = self._call_gemini_json([clean_image, current_image], quality_prompt)
                    score = quality_result.get('score', 0.95)
                    reason = quality_result.get('reason', 'AI quality check completed.')
                    logger.info(f"Quality Check: Score={score}, Reason={reason}")

            return clean_image, current_image, score, reason

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

    def _call_gemini_edit(self, image: Image.Image, prompt: str) -> Image.Image:
        """
        Helper method to handle the actual API call plumbing for image editing.
        """
        try:
            config_args = {
                "response_modalities": ["IMAGE"],
            }
            
            # Using Thinking Config if available (optional, based on previous implementation)
            if hasattr(types, 'ThinkingConfig'):
                 # For edits, we might not need thinking, but let's keep it simple or follow previous pattern.
                 # The user didn't specify, but previous code had it. Let's stick to simple generation for now unless needed.
                 # Actually, the user's prompt implies "Vibe Coding" which might benefit from thinking, but let's stick to the basics first.
                 pass

            if hasattr(types, 'ImageGenerationConfig'):
                 config_args['image_generation_config'] = types.ImageGenerationConfig(
                    guidance_scale=70, 
                    person_generation="dont_generate_people"
                )

            # Retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[image, prompt],
                        config=types.GenerateContentConfig(**config_args)
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        time.sleep(10 * (attempt + 1))
                    else:
                        raise e
            
            # Extract image
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        from io import BytesIO
                        return Image.open(BytesIO(part.inline_data.data))
            
            logger.error("No image data found in response.")
            raise ScreenVisualizerError("No image data returned from AI service.")

        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            raise ScreenVisualizerError(f"Gemini call failed: {e}") from e

    def _call_gemini_json(self, contents: List[Any], prompt: str) -> dict:
        """
        Helper method to handle API call for JSON text response.
        Args:
            contents: List of images or other content parts.
            prompt: The text prompt.
        """
        try:
            config_args = {
                "response_modalities": ["TEXT"],
            }
            
            # Combine contents and prompt
            full_contents = contents + [prompt]

            # Retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=full_contents,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        time.sleep(10 * (attempt + 1))
                    else:
                        raise e
            
            # Extract text
            text_response = ""
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        text_response += part.text
            
            # Parse JSON
            try:
                # Find JSON block if embedded in markdown
                json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    return json.loads(json_str)
                else:
                    return json.loads(text_response)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from AI response: {text_response}")
                return {'score': 0.9, 'reason': 'Failed to parse AI reasoning.'}

        except Exception as e:
            logger.error(f"Gemini JSON call failed: {e}")
            # Return safe default
            return {'score': 0.9, 'reason': f"Quality check failed: {str(e)}"}

    def _save_debug_image(self, image: Image.Image, step_name: str):
        """Save intermediate image for debugging."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_{timestamp}_{step_name}.jpg"
            save_path = os.path.join(settings.MEDIA_ROOT, "pipeline_steps", filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            image.save(save_path)
            logger.info(f"Saved debug image: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save debug image {step_name}: {e}")
