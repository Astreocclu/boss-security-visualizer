"""
AI-Enhanced Image Processor for Homescreen Visualization

This processor uses the Google Gemini AI service to generate realistic
screen visualizations via the ScreenVisualizer pipeline.
"""

import logging
import os
import io
from typing import List, Dict, Any
from PIL import Image
from django.core.files.base import ContentFile

from .ai_services import (
    AIServiceFactory,
    AIServiceType,
    ai_service_registry,
    AIServiceConfig
)
from .ai_services.providers.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class AIEnhancedImageProcessor:
    """
    Enhanced image processor that uses Gemini AI for intelligent screen visualization.
    """

    def __init__(self, preferred_providers: Dict[str, str] = None):
        """
        Initialize the AI-enhanced processor.
        """
        self.output_formats = ['JPEG']
        self.quality = 85
        
        # Initialize AI services
        self._initialize_ai_services()

        logger.info("AI-Enhanced Image Processor initialized")

    def _initialize_ai_services(self):
        """Initialize AI service providers and registry."""
        try:
            # Register Gemini provider
            self._register_gemini_provider()
            logger.info("AI services initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI services: {str(e)}")

    def _register_gemini_provider(self):
        """Register Gemini provider."""
        try:
            # Check for API key in env
            api_key = os.environ.get("GOOGLE_API_KEY")
            
            if api_key:
                gemini_provider = GeminiProvider()
                ai_service_registry.register_provider('gemini', gemini_provider)
                logger.info("Gemini provider registered successfully")
            else:
                logger.error("GOOGLE_API_KEY not found. Gemini provider cannot be registered.")
        except Exception as e:
            logger.error(f"Error registering Gemini provider: {str(e)}")

    def process_image(self, visualization_request):
        """
        Process an image using Gemini AI visualization.

        Args:
            visualization_request: VisualizationRequest instance

        Returns:
            list: List of generated image instances
        """
        try:
            # Mark request as processing
            visualization_request.mark_as_processing()
            visualization_request.update_progress(10, "Initializing Gemini AI...")

            # Load the original image
            original_image = Image.open(visualization_request.original_image.path)
            screen_type = visualization_request.screen_type

            # Get image generation service (Gemini)
            generation_service = AIServiceFactory.create_image_generation_service(
                provider_name='gemini'
            )

            if not generation_service:
                raise ValueError("Gemini service not available. Check API key.")

            # Generate visualization
            # The ScreenVisualizer pipeline handles Cleanse -> Build -> Install -> Check
            visualization_request.update_progress(30, "Running Screen King Pipeline (Cleanse -> Build -> Install -> Check)...")
            
            # We generate one high-quality variation
            variation_name = f"{screen_type.name.lower()}_standard"
            
            # Extract style preferences
            style_preferences = {
                "opacity": visualization_request.opacity,
                "color": visualization_request.color
            }

            result = generation_service.generate_screen_visualization(
                original_image,
                screen_type.name,
                detection_areas=None, # Handled by Gemini
                style_preferences=style_preferences
            )

            saved_images = []
            if result.success:
                visualization_request.update_progress(90, "Saving results...")
                
                # Save the result
                image_data = result.metadata.get('generated_image_data')
                clean_image_data = result.metadata.get('clean_image_data')
                
                if clean_image_data:
                    # Save clean image to the request
                    clean_filename = f"clean_{visualization_request.id}.jpg"
                    visualization_request.clean_image.save(
                        clean_filename,
                        ContentFile(clean_image_data),
                        save=True
                    )

                if image_data:
                    saved_images = self._save_generated_image(
                        image_data, 
                        variation_name, 
                        visualization_request,
                        metadata=result.metadata
                    )
                    
                visualization_request.mark_as_complete()
                logger.info(f"Successfully processed request {visualization_request.id}")
            else:
                raise ValueError(f"Gemini generation failed: {result.message}")

            return saved_images

        except Exception as e:
            error_msg = f"Error in AI processing: {str(e)}"
            logger.error(error_msg)
            visualization_request.mark_as_failed(error_msg)
            return []

    def _save_generated_image(
        self,
        image_data: bytes,
        variation: str,
        request,
        metadata: Dict[str, Any] = None
    ) -> List:
        """
        Save generated image and create GeneratedImage record.
        """
        from .models import GeneratedImage

        try:
            # Create filename
            filename = f"ai_generated_{request.id}_{variation}.jpg"

            # Create GeneratedImage record
            generated_image = GeneratedImage(request=request)
            if metadata:
                # Filter out binary data from metadata
                clean_metadata = {k: v for k, v in metadata.items() if k != 'generated_image_data'}
                generated_image.metadata = clean_metadata
                
            generated_image.generated_image.save(
                filename,
                ContentFile(image_data),
                save=True
            )

            logger.info(f"Saved generated image: {filename}")
            return [generated_image]

        except Exception as e:
            logger.error(f"Error saving generated image: {str(e)}")
            return []
