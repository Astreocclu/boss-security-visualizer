# AI Services Developer Guide

## Adding New AI Service Providers

This guide explains how to extend the AI services architecture by adding new AI service providers.

## Creating a New Provider

### Step 1: Implement the Provider Class

Create a new provider class that extends `BaseAIProvider`:

```python
from api.ai_services.providers.base_provider import BaseAIProvider
from api.ai_services.interfaces import AIServiceType, AIServiceConfig

class MyAIProvider(BaseAIProvider):
    def __init__(self):
        super().__init__(
            provider_name='my_ai_provider',
            supported_services=[
                AIServiceType.IMAGE_GENERATION,
                AIServiceType.COMPUTER_VISION
            ]
        )
    
    def create_service(self, service_type: AIServiceType, config: AIServiceConfig):
        if service_type == AIServiceType.IMAGE_GENERATION:
            return MyImageGenerationService(config)
        elif service_type == AIServiceType.COMPUTER_VISION:
            return MyVisionService(config)
        return None
```

### Step 2: Implement Service Classes

#### Image Generation Service

```python
from api.ai_services.interfaces import AIImageGenerationService, AIServiceResult
from PIL import Image
import requests

class MyImageGenerationService(AIImageGenerationService):
    def _validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("API key is required")
    
    def generate_screen_visualization(
        self,
        original_image: Image.Image,
        screen_type: str,
        detection_areas: List[Tuple[int, int, int, int]] = None,
        style_preferences: Dict[str, Any] = None
    ) -> AIServiceResult:
        try:
            # Implement your AI service API call here
            response = self._call_ai_api(original_image, screen_type, detection_areas)
            
            return AIServiceResult(
                success=True,
                status=ProcessingStatus.COMPLETED,
                message="Successfully generated visualization",
                metadata={'generated_image_data': response.image_data}
            )
        except Exception as e:
            return AIServiceResult(
                success=False,
                status=ProcessingStatus.FAILED,
                error_details=str(e)
            )
    
    def enhance_image_quality(self, image: Image.Image, enhancement_type: str = "general") -> AIServiceResult:
        # Implement image enhancement logic
        pass
    
    def get_service_status(self) -> Dict[str, Any]:
        # Return service health status
        return {'status': 'operational'}
    
    def _call_ai_api(self, image, screen_type, areas):
        # Implement actual API call to your AI service
        pass
```

#### Vision Service

```python
from api.ai_services.interfaces import AIVisionService, WindowDetectionResult

class MyVisionService(AIVisionService):
    def _validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("API key is required")
    
    def detect_windows_and_doors(
        self,
        image: Image.Image,
        confidence_threshold: float = 0.7
    ) -> WindowDetectionResult:
        try:
            # Implement window/door detection
            detections = self._detect_objects(image)
            
            return WindowDetectionResult(
                success=True,
                status=ProcessingStatus.COMPLETED,
                detected_windows=detections['windows'],
                bounding_boxes=detections['boxes'],
                confidence_scores=detections['scores']
            )
        except Exception as e:
            return WindowDetectionResult(
                success=False,
                status=ProcessingStatus.FAILED,
                error_details=str(e)
            )
    
    def analyze_screen_pattern(self, image: Image.Image, screen_area=None) -> ScreenAnalysisResult:
        # Implement screen pattern analysis
        pass
    
    def assess_image_quality(self, image: Image.Image, reference_image=None) -> QualityAssessmentResult:
        # Implement quality assessment
        pass
    
    def get_service_status(self) -> Dict[str, Any]:
        return {'status': 'operational'}
```

### Step 3: Register the Provider

Add registration code to initialize your provider:

```python
# In api/ai_enhanced_processor.py or a dedicated initialization module
from api.ai_services import ai_service_registry
from .providers.my_ai_provider import MyAIProvider

def initialize_my_provider():
    provider = MyAIProvider()
    ai_service_registry.register_provider('my_ai_provider', provider)
```

### Step 4: Add Configuration Support

Update the configuration manager to support your provider:

```python
# In api/ai_services/config.py
def _load_from_environment(self):
    # Add your provider's environment variable loading
    my_ai_key = os.getenv('MY_AI_API_KEY')
    if my_ai_key:
        config = AIServiceConfig(
            service_name='my_ai_provider',
            service_type=AIServiceType.IMAGE_GENERATION,
            api_key=my_ai_key,
            api_endpoint=os.getenv('MY_AI_ENDPOINT', 'https://api.myai.com/v1'),
            max_requests_per_minute=int(os.getenv('MY_AI_MAX_REQUESTS', '60')),
            timeout_seconds=int(os.getenv('MY_AI_TIMEOUT', '30'))
        )
        self._configs['my_ai_provider'] = config
```

## Testing Your Provider

### Unit Tests

Create comprehensive unit tests for your provider:

```python
import unittest
from api.ai_services.interfaces import AIServiceConfig, AIServiceType
from .my_ai_provider import MyAIProvider

class MyAIProviderTest(unittest.TestCase):
    def setUp(self):
        self.provider = MyAIProvider()
        self.config = AIServiceConfig(
            service_name='my_ai_provider',
            service_type=AIServiceType.IMAGE_GENERATION,
            api_key='test_key'
        )
    
    def test_create_image_generation_service(self):
        service = self.provider.create_service(AIServiceType.IMAGE_GENERATION, self.config)
        self.assertIsNotNone(service)
    
    def test_provider_info(self):
        info = self.provider.get_provider_info()
        self.assertEqual(info['name'], 'my_ai_provider')
        self.assertIn('supported_services', info)
```

### Integration Tests

Test your provider with the AI-enhanced processor:

```python
def test_with_ai_processor(self):
    # Register your provider
    ai_service_registry.register_provider('my_ai_provider', MyAIProvider())
    
    # Create processor with your provider
    processor = AIEnhancedImageProcessor(
        preferred_providers={'generation': 'my_ai_provider'}
    )
    
    # Test processing
    result = processor.process_image(test_request)
    self.assertGreater(len(result), 0)
```

## Best Practices

### Error Handling

Always implement comprehensive error handling:

```python
def generate_screen_visualization(self, ...):
    try:
        # Your implementation
        pass
    except requests.RequestException as e:
        return AIServiceResult(
            success=False,
            status=ProcessingStatus.FAILED,
            error_details=f"Network error: {str(e)}"
        )
    except ValueError as e:
        return AIServiceResult(
            success=False,
            status=ProcessingStatus.FAILED,
            error_details=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        return AIServiceResult(
            success=False,
            status=ProcessingStatus.FAILED,
            error_details=f"Unexpected error: {str(e)}"
        )
```

### Rate Limiting

Implement proper rate limiting:

```python
import time
from collections import defaultdict

class MyImageGenerationService(AIImageGenerationService):
    def __init__(self, config):
        super().__init__(config)
        self._request_times = defaultdict(list)
    
    def _check_rate_limit(self):
        current_time = time.time()
        service_key = self.config.service_name
        
        # Remove old requests (older than 1 minute)
        self._request_times[service_key] = [
            t for t in self._request_times[service_key]
            if current_time - t < 60
        ]
        
        # Check if we're within rate limit
        if len(self._request_times[service_key]) >= self.config.max_requests_per_minute:
            raise Exception("Rate limit exceeded")
        
        # Record this request
        self._request_times[service_key].append(current_time)
```

### Logging

Add comprehensive logging:

```python
import logging

logger = logging.getLogger(__name__)

def generate_screen_visualization(self, ...):
    logger.info(f"Starting visualization generation with {self.config.service_name}")
    start_time = time.time()
    
    try:
        result = self._call_ai_api(...)
        duration = time.time() - start_time
        logger.info(f"Visualization generated successfully in {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Visualization generation failed after {duration:.2f}s: {str(e)}")
        raise
```

### Configuration Validation

Validate configuration thoroughly:

```python
def _validate_config(self) -> None:
    if not self.config.api_key:
        raise ValueError("API key is required")
    
    if not self.config.api_endpoint:
        raise ValueError("API endpoint is required")
    
    if self.config.max_requests_per_minute <= 0:
        raise ValueError("Max requests per minute must be positive")
    
    # Test API connectivity
    try:
        response = requests.get(f"{self.config.api_endpoint}/health", timeout=5)
        if response.status_code != 200:
            raise ValueError("API endpoint is not accessible")
    except requests.RequestException:
        raise ValueError("Cannot connect to API endpoint")
```

## Deployment Considerations

### Environment Variables

Document required environment variables:

```bash
# My AI Provider Configuration
MY_AI_API_KEY=your_api_key_here
MY_AI_ENDPOINT=https://api.myai.com/v1
MY_AI_MAX_REQUESTS=60
MY_AI_TIMEOUT=30
MY_AI_MODEL=latest
```

### Docker Configuration

Update Docker configuration if needed:

```dockerfile
# Add any additional dependencies
RUN pip install my-ai-sdk

# Set environment variables
ENV MY_AI_ENDPOINT=https://api.myai.com/v1
ENV MY_AI_MAX_REQUESTS=60
```

### Monitoring

Implement health checks and monitoring:

```python
def get_service_status(self) -> Dict[str, Any]:
    try:
        # Test API connectivity
        response = requests.get(f"{self.config.api_endpoint}/health", timeout=5)
        
        return {
            'service_name': self.config.service_name,
            'status': 'operational' if response.status_code == 200 else 'degraded',
            'response_time': response.elapsed.total_seconds(),
            'last_check': time.time()
        }
    except Exception as e:
        return {
            'service_name': self.config.service_name,
            'status': 'unavailable',
            'error': str(e),
            'last_check': time.time()
        }
```

## Example: OpenAI Provider Implementation

Here's a complete example of implementing an OpenAI provider:

```python
import openai
from api.ai_services.providers.base_provider import BaseAIProvider
from api.ai_services.interfaces import *

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        super().__init__(
            provider_name='openai',
            supported_services=[AIServiceType.IMAGE_GENERATION, AIServiceType.COMPUTER_VISION]
        )
    
    def create_service(self, service_type: AIServiceType, config: AIServiceConfig):
        if service_type == AIServiceType.IMAGE_GENERATION:
            return OpenAIImageGenerationService(config)
        elif service_type == AIServiceType.COMPUTER_VISION:
            return OpenAIVisionService(config)
        return None

class OpenAIImageGenerationService(AIImageGenerationService):
    def _validate_config(self):
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
        openai.api_key = self.config.api_key
    
    def generate_screen_visualization(self, original_image, screen_type, detection_areas=None, style_preferences=None):
        try:
            # Convert image to base64
            image_data = self._image_to_base64(original_image)
            
            # Create prompt for screen visualization
            prompt = f"Add realistic {screen_type} screens to the windows and doors in this house image"
            
            # Call DALL-E API
            response = openai.Image.create_edit(
                image=image_data,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            return AIServiceResult(
                success=True,
                status=ProcessingStatus.COMPLETED,
                message="Successfully generated visualization",
                metadata={'generated_image_url': response['data'][0]['url']}
            )
        except Exception as e:
            return AIServiceResult(
                success=False,
                status=ProcessingStatus.FAILED,
                error_details=str(e)
            )
```

This guide provides a comprehensive framework for extending the AI services architecture with new providers while maintaining consistency and reliability.
