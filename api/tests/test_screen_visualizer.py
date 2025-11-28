"""
Tests for ScreenVisualizer
"""

import unittest
from unittest.mock import MagicMock, patch, ANY
from PIL import Image
import os
import sys
from django.conf import settings

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure Django settings if not already configured
if not settings.configured:
    settings.configure(
        MEDIA_ROOT='/tmp/media',
        DEBUG=True
    )

from api.visualizer.services import ScreenVisualizer, ScreenVisualizerError
from api.visualizer.prompts import get_quality_check_prompt

class TestScreenVisualizer(unittest.TestCase):

    def setUp(self):
        self.api_key = "fake_key"
        self.mock_client = MagicMock()
        with patch('google.genai.Client', return_value=self.mock_client):
            self.visualizer = ScreenVisualizer(api_key=self.api_key)
        self.mock_image = Image.new('RGB', (100, 100), color='white')

    def test_initialization_with_key(self):
        with patch('google.genai.Client') as mock_genai:
            visualizer = ScreenVisualizer(api_key="test_key")
            mock_genai.assert_called_with(api_key="test_key")
            self.assertEqual(visualizer.api_key, "test_key")

    def test_pipeline_success(self):
        # Mock the internal methods to avoid API calls
        self.visualizer._call_gemini_edit = MagicMock(return_value=self.mock_image)
        self.visualizer._call_gemini_json = MagicMock(return_value={'score': 0.95, 'reason': 'Test reason'})
        self.visualizer._save_debug_image = MagicMock()

        scope = {'windows': True, 'doors': False, 'patio': False}
        options = {'color': 'Black', 'mesh_type': '12x12'}
        
        clean_img, final_img, score, reason = self.visualizer.process_pipeline(self.mock_image, scope=scope, options=options)

        # Should be called once for cleanup + once for windows = 2 times
        self.assertEqual(self.visualizer._call_gemini_edit.call_count, 2)
        # Should be called once for quality check
        self.visualizer._call_gemini_json.assert_called_once()
        
        # Verify it was called with a list of 2 images (clean + final)
        call_args = self.visualizer._call_gemini_json.call_args
        self.assertIsInstance(call_args[0][0], list)
        self.assertEqual(len(call_args[0][0]), 2)
        
        self.assertEqual(final_img, self.mock_image)
        self.assertEqual(score, 0.95)
        self.assertEqual(reason, 'Test reason')

    def test_gatekeeper_patio(self):
        # Test that patio prompt is sent when patio is selected
        self.visualizer._call_gemini_edit = MagicMock(return_value=self.mock_image)
        self.visualizer._call_gemini_json = MagicMock(return_value={'score': 0.95, 'reason': 'Test reason'})
        self.visualizer._save_debug_image = MagicMock()

        scope = {'windows': False, 'doors': False, 'patio': True}
        options = {'color': 'Black', 'mesh_type': '12x12'}
        
        self.visualizer.process_pipeline(self.mock_image, scope=scope, options=options)
        
        # Should be called once for cleanup + once for patio = 2 times
        self.assertEqual(self.visualizer._call_gemini_edit.call_count, 2)
        
        # Verify second call is patio
        call_args = self.visualizer._call_gemini_edit.call_args_list[1]
        self.assertTrue("patio" in call_args[0][1])

    def test_gatekeeper_all(self):
        # Test that all steps are executed when all selected
        self.visualizer._call_gemini_edit = MagicMock(return_value=self.mock_image)
        self.visualizer._call_gemini_json = MagicMock(return_value={'score': 0.95, 'reason': 'Test reason'})
        self.visualizer._save_debug_image = MagicMock()

        scope = {'windows': True, 'doors': True, 'patio': True}
        options = {'color': 'Black', 'mesh_type': '12x12'}
        
        self.visualizer.process_pipeline(self.mock_image, scope=scope, options=options)
        
        # Should be called 1 (cleanup) + 3 (features) = 4 times
        # Should be called 1 (cleanup) + 3 (features) = 4 times
        self.assertEqual(self.visualizer._call_gemini_edit.call_count, 4)

if __name__ == '__main__':
    unittest.main()
