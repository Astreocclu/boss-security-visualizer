"""
Tests for ScreenVisualizer
"""

import unittest
from unittest.mock import MagicMock, patch, ANY
from PIL import Image
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.ai_services.screen_visualizer import ScreenVisualizer, ScreenVisualizerError

class TestScreenVisualizer(unittest.TestCase):

    def setUp(self):
        self.api_key = "fake_key"
        self.mock_client = MagicMock()
        self.visualizer = ScreenVisualizer(api_key=self.api_key, client=self.mock_client)
        self.mock_image = Image.new('RGB', (100, 100), color='white')

    def test_initialization_with_key(self):
        with patch('google.genai.Client') as mock_genai:
            visualizer = ScreenVisualizer(api_key="test_key")
            mock_genai.assert_called_with(api_key="test_key")
            self.assertEqual(visualizer.api_key, "test_key")

    def test_initialization_with_client(self):
        client = MagicMock()
        visualizer = ScreenVisualizer(client=client)
        self.assertEqual(visualizer.client, client)

    def test_pipeline_steps(self):
        # Mock the internal methods to avoid API calls
        self.visualizer.step_1_cleanse = MagicMock(return_value=self.mock_image)
        self.visualizer._analyze_structure = MagicMock(return_value=True) # Force build out
        self.visualizer.step_2_build_out = MagicMock(return_value=self.mock_image)
        self.visualizer.step_3_install_screen = MagicMock(return_value=self.mock_image)
        self.visualizer.step_4_quality_check = MagicMock(return_value=(True, 95))

        result_img, result_score = self.visualizer.process_pipeline(self.mock_image, mesh_type="solar")

        self.visualizer.step_1_cleanse.assert_called_once()
        self.visualizer._analyze_structure.assert_called_once()
        self.visualizer.step_2_build_out.assert_called_once()
        self.visualizer.step_3_install_screen.assert_called_once()
        self.visualizer.step_4_quality_check.assert_called_once()
        self.assertEqual(result_img, self.mock_image)
        self.assertEqual(result_score, 95)

    def test_mesh_type_logic(self):
        # Test that mesh type is passed correctly
        self.visualizer.step_1_cleanse = MagicMock(return_value=self.mock_image)
        self.visualizer._analyze_structure = MagicMock(return_value=False) # Skip build out
        self.visualizer.step_3_install_screen = MagicMock(return_value=self.mock_image)
        self.visualizer.step_4_quality_check = MagicMock(return_value=(True, 90))

        self.visualizer.process_pipeline(self.mock_image, mesh_type="privacy", opacity="95", color="Black")
        
        # Check if step 3 was called with correct args
        # Note: effective_mesh_type is hardcoded to "lifestyle_environmental" inside process_pipeline now
        self.visualizer.step_3_install_screen.assert_called_with(
            self.mock_image, 
            ANY, # reference_img
            "lifestyle_environmental", 
            opacity="95", 
            color="Black"
        )

    def test_error_handling(self):
        # Test that ScreenVisualizerError is raised
        self.visualizer.client = None
        with self.assertRaises(ScreenVisualizerError):
            self.visualizer.process_pipeline(self.mock_image)

if __name__ == '__main__':
    unittest.main()
