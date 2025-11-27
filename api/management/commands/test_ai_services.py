"""
Django management command to test and initialize AI services
Usage: python manage.py test_ai_services
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Test and initialize AI services for the homescreen project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix any issues found',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Testing AI Services Integration')
        )
        self.stdout.write('=' * 60)

        # Load environment variables
        load_dotenv()

        # Test 1: Check environment variables
        self.test_environment_variables()

        # Test 2: Test AI service configuration
        self.test_ai_configuration()

        # Test 3: Test provider registration
        self.test_provider_registration()

        # Test 4: Test service creation
        self.test_service_creation()

        # Test 5: Test OpenAI API directly
        self.test_openai_api()

        self.stdout.write(
            self.style.SUCCESS('\n✅ AI Services test completed!')
        )

    def test_environment_variables(self):
        """Test environment variable configuration"""
        self.stdout.write('\n🔧 Testing Environment Variables...')
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.stdout.write(
                self.style.SUCCESS(f'✅ OpenAI API Key found: {openai_key[:20]}...')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ OpenAI API Key not found in environment')
            )

        # Check other environment variables
        env_vars = ['OPENAI_MODEL', 'OPENAI_API_ENDPOINT', 'OPENAI_MAX_REQUESTS']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                self.stdout.write(f'✅ {var}: {value}')
            else:
                self.stdout.write(f'⚠️  {var}: Not set (using defaults)')

    def test_ai_configuration(self):
        """Test AI service configuration loading"""
        self.stdout.write('\n🔧 Testing AI Configuration...')
        
        try:
            from api.ai_services.config import ai_config_manager
            
            # Load configurations
            ai_config_manager.load_configs()
            
            # Test OpenAI config
            openai_config = ai_config_manager.get_config('openai')
            if openai_config:
                self.stdout.write(
                    self.style.SUCCESS('✅ OpenAI configuration loaded successfully')
                )
                self.stdout.write(f'   - Service: {openai_config.service_name}')
                self.stdout.write(f'   - Model: {openai_config.model_name}')
                self.stdout.write(f'   - Endpoint: {openai_config.api_endpoint}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ OpenAI configuration not loaded')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Configuration error: {str(e)}')
            )

    def test_provider_registration(self):
        """Test AI provider registration"""
        self.stdout.write('\n🔧 Testing Provider Registration...')
        
        try:
            from api.ai_services.registry import ai_service_registry
            from api.ai_services.providers.openai_provider import OpenAIProvider
            from api.ai_services.providers.mock_provider import MockAIProvider
            from api.ai_services.config import ai_config_manager
            
            # Register Mock Provider
            mock_provider = MockAIProvider()
            mock_success = ai_service_registry.register_provider('mock_ai', mock_provider)
            
            if mock_success:
                self.stdout.write(self.style.SUCCESS('✅ Mock provider registered'))
            else:
                self.stdout.write(self.style.ERROR('❌ Mock provider registration failed'))
            
            # Register OpenAI Provider
            openai_config = ai_config_manager.get_config('openai')
            if openai_config and openai_config.api_key:
                openai_provider = OpenAIProvider()
                openai_success = ai_service_registry.register_provider('openai', openai_provider)
                
                if openai_success:
                    self.stdout.write(self.style.SUCCESS('✅ OpenAI provider registered'))
                else:
                    self.stdout.write(self.style.ERROR('❌ OpenAI provider registration failed'))
            else:
                self.stdout.write(self.style.WARNING('⚠️  OpenAI provider not registered (no API key)'))
            
            # Show available providers
            available_providers = ai_service_registry.get_available_providers()
            self.stdout.write(f'📋 Available providers: {available_providers}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Provider registration error: {str(e)}')
            )

    def test_service_creation(self):
        """Test AI service creation"""
        self.stdout.write('\n🔧 Testing Service Creation...')
        
        try:
            from api.ai_services.factory import AIServiceFactory
            
            # Test OpenAI Image Generation Service
            image_service = AIServiceFactory.create_image_generation_service('openai')
            if image_service:
                self.stdout.write(self.style.SUCCESS('✅ OpenAI Image Generation Service created'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to create OpenAI Image Generation Service'))
            
            # Test OpenAI Vision Service
            vision_service = AIServiceFactory.create_vision_service('openai')
            if vision_service:
                self.stdout.write(self.style.SUCCESS('✅ OpenAI Vision Service created'))
                
                # Test if problematic method exists
                if hasattr(vision_service, '_create_detection_prompt'):
                    self.stdout.write('✅ Vision service has _create_detection_prompt method')
                else:
                    self.stdout.write(self.style.ERROR('❌ Vision service missing _create_detection_prompt method'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to create OpenAI Vision Service'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Service creation error: {str(e)}')
            )

    def test_openai_api(self):
        """Test OpenAI API directly"""
        self.stdout.write('\n🔧 Testing OpenAI API...')
        
        try:
            import requests
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.stdout.write(self.style.ERROR('❌ No API key for testing'))
                return
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test API connectivity
            response = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ OpenAI API is accessible'))
                
                # Test text completion
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Say 'AI services working!'"}],
                    "max_tokens": 10
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message = result['choices'][0]['message']['content']
                    self.stdout.write(self.style.SUCCESS(f'✅ OpenAI response: {message}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ OpenAI API error: {response.status_code}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ OpenAI API not accessible: {response.status_code}'))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ OpenAI API test error: {str(e)}')
            )
