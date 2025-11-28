"""
Gemini AI Provider
------------------
Provider implementation for Google's Gemini AI services.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image

from ..interfaces import (
    AIServiceProvider,
    AIImageGenerationService,
    AIServiceType,
    AIServiceConfig,
    AIServiceResult,
    ProcessingStatus,
    WindowDetectionResult,
    ScreenAnalysisResult,
    QualityAssessmentResult
)
from api.visualizer.services import ScreenVisualizer, ScreenVisualizerError

logger = logging.getLogger(__name__)

class GeminiProvider(AIServiceProvider):
    """
    Provider for Google Gemini AI services.
    """

    def get_available_services(self) -> List[AIServiceType]:
        return [
            AIServiceType.IMAGE_GENERATION,
            AIServiceType.IMAGE_ENHANCEMENT
        ]

    def create_service(self, service_type: AIServiceType, config: AIServiceConfig):
        if service_type == AIServiceType.IMAGE_GENERATION:
            return GeminiImageGenerationService(config)
        elif service_type == AIServiceType.IMAGE_ENHANCEMENT:
            return GeminiImageGenerationService(config) # Enhancement handled by generation service
        else:
            raise ValueError(f"Unsupported service type: {service_type}")

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": "Google Gemini",
            "version": "1.0.0",
            "models": ["gemini-3-pro-image-preview", "gemini-2.0-flash-exp"]
        }

class GeminiImageGenerationService(AIImageGenerationService):
    """
    Image generation service using Gemini.
    """

    def __init__(self, config: AIServiceConfig):
        super().__init__(config)
        api_key = config.api_key or os.environ.get("GOOGLE_API_KEY")
        self.visualizer = ScreenVisualizer(api_key=api_key)

    def _validate_config(self) -> None:
        if not self.config.api_key and not os.environ.get("GOOGLE_API_KEY"):
            logger.warning("No API key provided for Gemini service")

    def generate_screen_visualization(
        self,
        original_image: Image.Image,
        screen_type: str,
        detection_areas: List[Tuple[int, int, int, int]] = None,
        style_preferences: Dict[str, Any] = None,
        progress_callback=None
    ) -> AIServiceResult:
        """
        Generate screen visualization using ScreenVisualizer pipeline.
        """
        try:
            # Extract style preferences
            opacity = None
            color = None
            mesh_type = "12x12" # Default
            
            if style_preferences:
                opacity = style_preferences.get('opacity')
                color = style_preferences.get('color')
                mesh_type = style_preferences.get('mesh_type', '12x12')
            
            # If opacity is not provided in style_preferences, try to infer or default
            if not opacity:
                # Default to 95 if not specified
                opacity = "95"

            # Construct options
            options = {
                'color': color or "Black",
                'mesh_type': mesh_type,
                'opacity': opacity
            }
            
            # Construct scope
            # If scope is in style_preferences, use it. Otherwise infer from screen_type.
            scope = style_preferences.get('scope', {})
            if not scope:
                # Infer from screen_type (legacy support)
                scope = {
                    'windows': 'window' in screen_type.lower(),
                    'doors': 'door' in screen_type.lower(),
                    'patio': 'patio' in screen_type.lower()
                }
                # If nothing matched, default to windows
                if not any(scope.values()):
                    scope['windows'] = True

            # Run the pipeline
            clean_image, result_image, quality_score, quality_reason = self.visualizer.process_pipeline(
                original_image, 
                scope=scope,
                options=options,
                progress_callback=progress_callback
            )
            
            # Convert back to bytes for the result
            import io
            output = io.BytesIO()
            result_image.save(output, format='JPEG', quality=85)
            image_data = output.getvalue()

            # Convert clean image to bytes
            clean_output = io.BytesIO()
            clean_image.save(clean_output, format='JPEG', quality=85)
            clean_image_data = clean_output.getvalue()
            
            return AIServiceResult(
                success=True,
                status=ProcessingStatus.COMPLETED,
                metadata={
                    "generated_image_data": image_data,
                    "clean_image_data": clean_image_data,
                    "quality_score": quality_score,
                    "quality_reason": quality_reason
                }
            )
            
        except ScreenVisualizerError as e:
            logger.error(f"ScreenVisualizer failed: {e}")
            return AIServiceResult(
                success=False,
                status=ProcessingStatus.FAILED,
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return AIServiceResult(
                success=False,
                status=ProcessingStatus.FAILED,
                message=f"Unexpected error: {str(e)}"
            )

    def enhance_image_quality(
        self,
        image: Image.Image,
        enhancement_type: str = "general"
    ) -> AIServiceResult:
        # TODO: Implement enhancement using Gemini
        return AIServiceResult(
            success=True,
            status=ProcessingStatus.COMPLETED,
            message="Enhancement not yet implemented for Gemini"
        )

    def get_service_status(self) -> Dict[str, Any]:
        return {"status": "active", "provider": "gemini"}

    def get_service_status(self) -> Dict[str, Any]:
        return {"status": "active", "provider": "gemini"}
