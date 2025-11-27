"""
Comprehensive Test Suite for ScreenVisualizer Module
----------------------------------------------------
Tests:
1. ScreenVisualizer (Unit)
2. GeminiProvider (Integration/Unit)
3. End-to-End Flow (Mocked)
"""

import unittest
from unittest.mock import MagicMock, patch, ANY
from PIL import Image
import os
import sys
import io

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.ai_services.screen_visualizer import ScreenVisualizer, ScreenVisualizerError
from api.ai_services.providers.gemini_provider import GeminiImageGenerationService, GeminiProvider
from api.ai_services.interfaces import AIServiceConfig, AIServiceType, ProcessingStatus
from api.ai_services.prompts import CLEANUP_SCENE_PROMPT

class TestScreenVisualizerUnit(unittest.TestCase):
    """Unit tests for ScreenVisualizer logic."""

    def setUp(self):
        self.mock_client = MagicMock()
        self.visualizer = ScreenVisualizer(client=self.mock_client)
        self.mock_image = Image.new('RGB', (100, 100), color='white')

    def test_pipeline_execution_order(self):
        """Verify the 4-step pipeline executes in correct order."""
        # Mock internal steps
        self.visualizer.cleanup_scene = MagicMock(return_value=self.mock_image)
        self.visualizer.check_and_build_structure = MagicMock(return_value=self.mock_image)
        self.visualizer.install_screen = MagicMock(return_value=self.mock_image)
        self.visualizer.apply_mesh_physics = MagicMock(return_value=self.mock_image)

        self.visualizer.process_pipeline(self.mock_image, mesh_type="solar")

        # Verify order
        self.visualizer.cleanup_scene.assert_called_once()
        self.visualizer.check_and_build_structure.assert_called_once()
        self.visualizer.install_screen.assert_called_once()
        self.visualizer.apply_mesh_physics.assert_called_once()

    def test_cleanup_scene_uses_correct_prompt(self):
        """Verify cleanup scene uses the correct prompt."""
        # Mock _generate_image to avoid API call
        self.visualizer._generate_image = MagicMock(return_value=self.mock_image)
        
        self.visualizer.cleanup_scene(self.mock_image)
        
        self.visualizer._generate_image.assert_called_with(self.mock_image, CLEANUP_SCENE_PROMPT)

    def test_error_propagation(self):
        """Verify errors are propagated as ScreenVisualizerError."""
        self.visualizer.cleanup_scene = MagicMock(side_effect=Exception("API Error"))
        
        with self.assertRaises(ScreenVisualizerError) as cm:
            self.visualizer.process_pipeline(self.mock_image)
        
        self.assertIn("Pipeline failed", str(cm.exception))

class TestGeminiProviderIntegration(unittest.TestCase):
    """Tests for GeminiProvider wrapper."""

    def setUp(self):
        self.config = AIServiceConfig(
            service_name="gemini",
            service_type=AIServiceType.IMAGE_GENERATION,
            api_key="test_key"
        )
        self.service = GeminiImageGenerationService(self.config)
        self.mock_image = Image.new('RGB', (100, 100), color='white')

    def test_generate_screen_visualization_success(self):
        """Verify successful generation returns correct result structure."""
        # Mock the visualizer inside the service
        self.service.visualizer.process_pipeline = MagicMock(return_value=self.mock_image)

        result = self.service.generate_screen_visualization(
            self.mock_image,
            screen_type="solar_screen"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.status, ProcessingStatus.COMPLETED)
        self.assertIn("generated_image_data", result.metadata)
        self.service.visualizer.process_pipeline.assert_called_once()

    def test_generate_screen_visualization_failure(self):
        """Verify failure handling."""
        self.service.visualizer.process_pipeline = MagicMock(side_effect=ScreenVisualizerError("Fail"))

        result = self.service.generate_screen_visualization(
            self.mock_image,
            screen_type="solar_screen"
        )

        self.assertFalse(result.success)
        self.assertEqual(result.status, ProcessingStatus.FAILED)
        self.assertEqual(result.message, "Fail")

class TestEndToEndFlow(unittest.TestCase):
    """Simulate the full flow from Processor to Provider."""

    @patch('api.ai_enhanced_processor.AIServiceFactory')
    def test_processor_delegation(self, mock_factory):
        """Verify AIEnhancedImageProcessor delegates to Gemini service."""
        from api.ai_enhanced_processor import AIEnhancedImageProcessor
        
        # Setup mocks
        mock_generation_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.metadata = {'generated_image_data': b'fake_data'}
        mock_generation_service.generate_screen_visualization.return_value = mock_result
        
        mock_factory.create_image_generation_service.return_value = mock_generation_service
        
        # Initialize processor
        processor = AIEnhancedImageProcessor(preferred_providers={'generation': 'gemini'})
        
        # Create dummy request objects
        mock_request = MagicMock()
        mock_request.screen_type.name = "solar_screen"
        mock_request.original_image.path = "dummy_path"
        
        # Mock Image.open to avoid file system access
        with patch('PIL.Image.open', return_value=Image.new('RGB', (100, 100))):
            # Mock internal methods to isolate generation step
            processor._detect_windows_and_doors = MagicMock(return_value={})
            processor._analyze_image_characteristics = MagicMock(return_value={})
            processor._assess_and_enhance_quality = MagicMock(return_value=[])
            processor._save_generated_images = MagicMock(return_value=[])
            
            # Run process
            processor.process_image(mock_request)
            
            # Verify generation service was called
            mock_generation_service.generate_screen_visualization.assert_called()

if __name__ == '__main__':
    unittest.main()
