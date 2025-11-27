"""
Tests for AI services functionality.

This module tests the AI service abstraction layer, providers, and integration
with the homescreen visualization system.
"""

import unittest
from unittest.mock import Mock, patch
from PIL import Image
import io
import tempfile
import os

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import VisualizationRequest, ScreenType
from ..ai_services import (
    AIServiceRegistry,
    AIServiceFactory,
    AIServiceType,
    AIServiceConfig,
    ai_service_registry
)
from ..ai_services.providers.mock_provider import MockAIProvider
from ..ai_enhanced_processor import AIEnhancedImageProcessor


class AIServiceRegistryTest(TestCase):
    """Test the AI service registry functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear registry for clean tests
        ai_service_registry.clear_registry()
    
    def tearDown(self):
        """Clean up after tests."""
        ai_service_registry.clear_registry()
    
    def test_register_provider(self):
        """Test registering an AI service provider."""
        provider = MockAIProvider()
        result = ai_service_registry.register_provider('test_provider', provider)
        
        self.assertTrue(result)
        self.assertIn('test_provider', ai_service_registry.get_all_providers())
    
    def test_get_providers_for_service(self):
        """Test getting providers for a specific service type."""
        provider = MockAIProvider()
        ai_service_registry.register_provider('test_provider', provider)
        
        image_gen_providers = ai_service_registry.get_providers_for_service(AIServiceType.IMAGE_GENERATION)
        vision_providers = ai_service_registry.get_providers_for_service(AIServiceType.COMPUTER_VISION)
        
        self.assertIn('test_provider', image_gen_providers)
        self.assertIn('test_provider', vision_providers)
    
    def test_unregister_provider(self):
        """Test unregistering a provider."""
        provider = MockAIProvider()
        ai_service_registry.register_provider('test_provider', provider)
        
        # Verify it's registered
        self.assertIn('test_provider', ai_service_registry.get_all_providers())
        
        # Unregister
        result = ai_service_registry.unregister_provider('test_provider')
        self.assertTrue(result)
        self.assertNotIn('test_provider', ai_service_registry.get_all_providers())
    
    def test_get_registry_status(self):
        """Test getting registry status."""
        provider = MockAIProvider()
        ai_service_registry.register_provider('test_provider', provider)
        
        status = ai_service_registry.get_registry_status()
        
        self.assertEqual(status['total_providers'], 1)
        self.assertIn('providers_by_service', status)
        self.assertIn('provider_status', status)


class AIServiceFactoryTest(TestCase):
    """Test the AI service factory functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        ai_service_registry.clear_registry()
        self.provider = MockAIProvider()
        ai_service_registry.register_provider('mock_ai', self.provider)
    
    def tearDown(self):
        """Clean up after tests."""
        ai_service_registry.clear_registry()
    
    def test_create_image_generation_service(self):
        """Test creating an image generation service."""
        service = AIServiceFactory.create_image_generation_service(provider_name='mock_ai')
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.service_name, 'mock_ai')
    
    def test_create_vision_service(self):
        """Test creating a vision service."""
        service = AIServiceFactory.create_vision_service(provider_name='mock_ai')
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.service_name, 'mock_ai')
    
    def test_create_service_by_type(self):
        """Test creating services by type."""
        image_service = AIServiceFactory.create_service_by_type(AIServiceType.IMAGE_GENERATION, 'mock_ai')
        vision_service = AIServiceFactory.create_service_by_type(AIServiceType.COMPUTER_VISION, 'mock_ai')
        
        self.assertIsNotNone(image_service)
        self.assertIsNotNone(vision_service)
    
    def test_get_available_providers(self):
        """Test getting available providers for a service type."""
        providers = AIServiceFactory.get_available_providers(AIServiceType.IMAGE_GENERATION)
        
        self.assertIn('mock_ai', providers)
        self.assertIn('available_services', providers['mock_ai'])


class MockAIProviderTest(TestCase):
    """Test the mock AI provider implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = MockAIProvider()
        self.config = AIServiceConfig(
            service_name='mock_ai',
            service_type=AIServiceType.IMAGE_GENERATION
        )
    
    def test_provider_info(self):
        """Test getting provider information."""
        info = self.provider.get_provider_info()
        
        self.assertEqual(info['name'], 'mock_ai')
        self.assertIn('supported_services', info)
        self.assertIn('status', info)
    
    def test_create_image_generation_service(self):
        """Test creating an image generation service."""
        service = self.provider.create_service(AIServiceType.IMAGE_GENERATION, self.config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.service_name, 'mock_ai')
    
    def test_create_vision_service(self):
        """Test creating a vision service."""
        vision_config = AIServiceConfig(
            service_name='mock_ai',
            service_type=AIServiceType.COMPUTER_VISION
        )
        service = self.provider.create_service(AIServiceType.COMPUTER_VISION, vision_config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.config.service_name, 'mock_ai')
    
    def test_service_health(self):
        """Test getting service health information."""
        health = self.provider.get_service_health()
        
        self.assertIn('provider_name', health)
        self.assertIn('status', health)
        self.assertEqual(health['provider_name'], 'mock_ai')


class MockImageGenerationServiceTest(TestCase):
    """Test the mock image generation service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AIServiceConfig(
            service_name='mock_ai',
            service_type=AIServiceType.IMAGE_GENERATION
        )
        self.provider = MockAIProvider()
        self.service = self.provider.create_service(AIServiceType.IMAGE_GENERATION, self.config)
        
        # Create a test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
    
    def test_generate_screen_visualization(self):
        """Test generating a screen visualization."""
        result = self.service.generate_screen_visualization(
            self.test_image,
            'security_mesh',
            detection_areas=[(10, 10, 50, 50)]
        )
        
        self.assertTrue(result.success)
        self.assertIn('generated_image_data', result.metadata)
        self.assertGreater(result.processing_time_seconds, 0)
    
    def test_enhance_image_quality(self):
        """Test enhancing image quality."""
        result = self.service.enhance_image_quality(self.test_image, 'general')
        
        self.assertTrue(result.success)
        self.assertIn('enhanced_image_data', result.metadata)
        self.assertGreater(result.processing_time_seconds, 0)
    
    def test_get_service_status(self):
        """Test getting service status."""
        status = self.service.get_service_status()
        
        self.assertIn('service_name', status)
        self.assertIn('status', status)


class MockVisionServiceTest(TestCase):
    """Test the mock vision service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AIServiceConfig(
            service_name='mock_ai',
            service_type=AIServiceType.COMPUTER_VISION
        )
        self.provider = MockAIProvider()
        self.service = self.provider.create_service(AIServiceType.COMPUTER_VISION, self.config)
        
        # Create a test image
        self.test_image = Image.new('RGB', (200, 200), color='blue')
    
    def test_detect_windows_and_doors(self):
        """Test window and door detection."""
        result = self.service.detect_windows_and_doors(self.test_image, confidence_threshold=0.7)
        
        self.assertTrue(result.success)
        self.assertGreater(len(result.detected_windows), 0)
        self.assertGreater(len(result.bounding_boxes), 0)
        self.assertGreater(len(result.confidence_scores), 0)
    
    def test_analyze_screen_pattern(self):
        """Test screen pattern analysis."""
        result = self.service.analyze_screen_pattern(self.test_image)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.screen_type)
        self.assertIsNotNone(result.mesh_pattern)
        self.assertIsInstance(result.opacity_level, float)
    
    def test_assess_image_quality(self):
        """Test image quality assessment."""
        result = self.service.assess_image_quality(self.test_image)
        
        self.assertTrue(result.success)
        self.assertIsInstance(result.overall_score, float)
        self.assertIsInstance(result.realism_score, float)
        self.assertIsInstance(result.technical_quality, float)
        self.assertIsInstance(result.aesthetic_score, float)


class AIEnhancedProcessorTest(TestCase):
    """Test the AI-enhanced image processor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test user and screen type
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.screen_type = ScreenType.objects.create(name='Security Mesh', description='Test screen type')
        
        # Create test image file
        self.test_image = Image.new('RGB', (300, 300), color='green')
        self.image_file = io.BytesIO()
        self.test_image.save(self.image_file, format='JPEG')
        self.image_file.seek(0)
        
        # Create uploaded file
        self.uploaded_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=self.image_file.getvalue(),
            content_type='image/jpeg'
        )
        
        # Create visualization request
        self.request = VisualizationRequest.objects.create(
            user=self.user,
            original_image=self.uploaded_file,
            screen_type=self.screen_type,
            status='pending'
        )
        
        # Initialize processor
        self.processor = AIEnhancedImageProcessor()
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.preferred_providers, {})
    
    def test_get_processor_status(self):
        """Test getting processor status."""
        status = self.processor.get_processor_status()
        
        self.assertEqual(status['processor_type'], 'ai_enhanced')
        self.assertIn('ai_services_status', status)
        self.assertIn('available_services', status)
    
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_process_image(self, mock_sleep):
        """Test processing an image with AI enhancement."""
        # This test may take a while due to the mock processing delays
        # We mock time.sleep to speed it up
        mock_sleep.return_value = None
        
        result = self.processor.process_image(self.request)
        
        # Check that processing completed
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'complete')
        
        # Check that images were generated
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
