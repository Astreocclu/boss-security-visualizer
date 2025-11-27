# AI Services Documentation

## Overview

The Homescreen Visualization application now includes a comprehensive, service-agnostic AI framework for intelligent screen visualization. This system provides a flexible architecture that can work with multiple AI providers while maintaining consistent interfaces and fallback mechanisms.

## Architecture

### Core Components

1. **Service Interfaces** (`api/ai_services/interfaces.py`)
   - Abstract base classes defining the contract for AI services
   - Data structures for service results and configurations
   - Enum definitions for service types and processing status

2. **Service Registry** (`api/ai_services/registry.py`)
   - Centralized registry for managing AI service providers
   - Dynamic service discovery and provider capabilities
   - Health monitoring and status tracking

3. **Service Factory** (`api/ai_services/factory.py`)
   - Factory pattern for creating service instances
   - Provider selection based on requirements
   - Configuration validation and management

4. **Configuration Manager** (`api/ai_services/config.py`)
   - Flexible configuration system supporting multiple sources
   - Environment variable and file-based configuration
   - Provider-specific settings management

5. **Provider Implementations** (`api/ai_services/providers/`)
   - Base provider class with common functionality
   - Mock provider for testing and development
   - Extensible architecture for adding new providers

## Service Types

### 1. Image Generation Services
- **Purpose**: Generate realistic screen visualizations on house images
- **Capabilities**:
  - Screen overlay generation with realistic patterns
  - Multiple variation generation
  - Image quality enhancement
  - Style customization

### 2. Computer Vision Services
- **Purpose**: Analyze images for intelligent screen application
- **Capabilities**:
  - Window and door detection
  - Screen pattern analysis
  - Image quality assessment
  - Lighting condition analysis

### 3. Image Enhancement Services
- **Purpose**: Improve the quality and realism of generated images
- **Capabilities**:
  - Brightness and contrast adjustment
  - Sharpness enhancement
  - Color correction
  - Noise reduction

## API Endpoints

### AI Service Management

#### Get AI Services Status
```
GET /api/ai-services/status/
```
Returns overall status of AI services including registry and factory information.

#### Get Available Providers
```
GET /api/ai-services/providers/
```
Returns detailed information about all registered AI service providers.

#### Get Service Health
```
GET /api/ai-services/health/
```
Returns health status for all registered providers.

### Example Response
```json
{
  "registry_status": {
    "total_providers": 1,
    "providers_by_service": {
      "image_generation": 1,
      "computer_vision": 1,
      "image_enhancement": 1
    }
  },
  "factory_status": {
    "factory_version": "1.0.0",
    "supported_service_types": ["image_generation", "computer_vision", "image_enhancement"],
    "total_available_services": 3
  }
}
```

## Usage Examples

### Backend Usage

#### Creating an AI Service
```python
from api.ai_services import AIServiceFactory, AIServiceType

# Create an image generation service
service = AIServiceFactory.create_image_generation_service(
    provider_name='mock_ai'
)

# Generate screen visualization
result = service.generate_screen_visualization(
    original_image=image,
    screen_type='security_mesh',
    detection_areas=[(10, 10, 100, 100)]
)
```

#### Using the AI-Enhanced Processor
```python
from api.ai_enhanced_processor import AIEnhancedImageProcessor

processor = AIEnhancedImageProcessor()
generated_images = processor.process_image(visualization_request)
```

### Frontend Usage

#### AI Service Status Component
```jsx
import AIServiceStatus from '../components/AI/AIServiceStatus';

function UploadPage() {
  const [selectedProvider, setSelectedProvider] = useState('mock_ai');
  
  return (
    <div>
      <AIServiceStatus onServiceSelect={setSelectedProvider} />
      {/* Rest of upload form */}
    </div>
  );
}
```

## Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=dall-e-3
OPENAI_MAX_REQUESTS=60

# Google Cloud Vision Configuration
GOOGLE_CLOUD_API_KEY=your_google_api_key
GOOGLE_MAX_REQUESTS=60

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Django Settings
```python
AI_SERVICES_CONFIG = {
    'openai': {
        'service_type': 'image_generation',
        'api_endpoint': 'https://api.openai.com/v1',
        'model_name': 'dall-e-3',
        'max_requests_per_minute': 60,
        'timeout_seconds': 30
    },
    'google_vision': {
        'service_type': 'computer_vision',
        'api_endpoint': 'https://vision.googleapis.com/v1',
        'max_requests_per_minute': 60,
        'timeout_seconds': 30
    }
}
```

## Adding New Providers

### 1. Create Provider Class
```python
from api.ai_services.providers.base_provider import BaseAIProvider
from api.ai_services.interfaces import AIServiceType

class CustomAIProvider(BaseAIProvider):
    def __init__(self):
        super().__init__(
            provider_name='custom_ai',
            supported_services=[AIServiceType.IMAGE_GENERATION]
        )
    
    def create_service(self, service_type, config):
        if service_type == AIServiceType.IMAGE_GENERATION:
            return CustomImageGenerationService(config)
        return None
```

### 2. Register Provider
```python
from api.ai_services import ai_service_registry

provider = CustomAIProvider()
ai_service_registry.register_provider('custom_ai', provider)
```

## Error Handling and Fallbacks

The system includes comprehensive error handling:

1. **Service Failures**: Automatic fallback to basic image processor
2. **Provider Unavailability**: Graceful degradation with mock services
3. **Configuration Errors**: Detailed error messages and validation
4. **Network Issues**: Retry mechanisms and timeout handling

## Testing

### Running AI Service Tests
```bash
python manage.py test api.tests.test_ai_services -v 2
```

### Test Coverage
- Service registry functionality
- Factory pattern implementation
- Mock provider services
- AI-enhanced processor integration
- Error handling and fallbacks

## Performance Considerations

1. **Caching**: Service instances are cached for reuse
2. **Rate Limiting**: Built-in rate limiting per provider
3. **Async Processing**: Background processing for long-running operations
4. **Resource Management**: Automatic cleanup of service resources

## Security

1. **API Key Management**: Secure storage of API credentials
2. **Input Validation**: Comprehensive validation of all inputs
3. **Error Sanitization**: Safe error messages without sensitive data
4. **Access Control**: Authentication required for AI service endpoints

## Monitoring and Logging

1. **Service Health**: Real-time health monitoring
2. **Performance Metrics**: Request timing and success rates
3. **Error Tracking**: Detailed error logging and reporting
4. **Usage Statistics**: Provider usage and cost tracking

## Future Enhancements

1. **Additional Providers**: OpenAI, Google Cloud, Anthropic integrations
2. **Advanced Features**: Continuous learning and A/B testing
3. **Performance Optimization**: Caching and request optimization
4. **Analytics**: Advanced usage analytics and reporting
