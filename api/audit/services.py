import logging
import os
import json
import re
from typing import Optional, Dict, Any
from PIL import Image
from google import genai
from google.genai import types
from django.conf import settings

from .prompts import get_audit_prompt
from .models import AuditReport

logger = logging.getLogger(__name__)

class AuditServiceError(Exception):
    """Base exception for AuditService errors."""
    pass

class AuditService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found. AuditService cannot function.")
            raise AuditServiceError("API Key missing. Please set GOOGLE_API_KEY.")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash"  # Fast vision model for security analysis

    def perform_audit(self, visualization_request) -> AuditReport:
        """
        Performs a security audit on the original image of the request.
        """
        try:
            # Check if audit already exists
            if hasattr(visualization_request, 'audit_report'):
                return visualization_request.audit_report

            original_image_path = visualization_request.original_image.path
            if not os.path.exists(original_image_path):
                raise AuditServiceError(f"Image file not found: {original_image_path}")

            with Image.open(original_image_path) as img:
                # Resize if too large to save tokens/time, though 1.5 Pro handles large images well.
                # Let's keep original for detail.
                
                prompt = get_audit_prompt()
                result_json = self._call_gemini_json(img, prompt)
                
                # Create AuditReport
                audit_report = AuditReport.objects.create(
                    request=visualization_request,
                    has_ground_level_access=result_json.get('has_ground_level_access', False),
                    has_concealment=result_json.get('has_concealment', False),
                    has_glass_proximity=result_json.get('has_glass_proximity', False),
                    has_hardware_weakness=result_json.get('has_hardware_weakness', False),
                    vulnerabilities=result_json.get('vulnerabilities', []),
                    analysis_summary=result_json.get('analysis_summary', "Analysis completed.")
                )
                
                return audit_report

        except Exception as e:
            logger.error(f"Audit failed: {e}")
            raise AuditServiceError(f"Audit failed: {e}") from e

    def _call_gemini_json(self, image: Image.Image, prompt: str) -> dict:
        """
        Helper method to handle API call for JSON text response.
        """
        try:
            config_args = {
                "response_modalities": ["TEXT"],
            }
            
            # Combine image and prompt
            contents = [image, prompt]

            # Retry logic
            max_retries = 3
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
                        import time
                        time.sleep(2 * (attempt + 1))
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
                # Fallback structure
                return {
                    'has_ground_level_access': False,
                    'analysis_summary': f"Could not parse AI response. Raw: {text_response[:100]}..."
                }

        except Exception as e:
            logger.error(f"Gemini JSON call failed: {e}")
            raise AuditServiceError(f"Gemini JSON call failed: {e}")
