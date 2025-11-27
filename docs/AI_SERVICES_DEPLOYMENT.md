# AI Services Deployment Guide

## Overview

This guide covers the deployment and configuration of the AI services framework for the Homescreen Visualization application. The system is designed to be service-agnostic and can work with multiple AI providers.

## Prerequisites

- Python 3.8+
- Django 4.2+
- Required Python packages (see requirements.txt)
- API keys for desired AI providers (optional for development)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Migration

```bash
python manage.py migrate
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# Basic Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost

# AI Service Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=dall-e-3
OPENAI_MAX_REQUESTS=60
OPENAI_TIMEOUT=30

GOOGLE_CLOUD_API_KEY=your_google_api_key
GOOGLE_MAX_REQUESTS=60
GOOGLE_TIMEOUT=30

ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_MAX_REQUESTS=60
ANTHROPIC_TIMEOUT=30
```

## Configuration Options

### 1. Environment Variables (Recommended)

The system automatically loads configuration from environment variables:

```bash
# Provider-specific settings
{PROVIDER}_API_KEY=your_api_key
{PROVIDER}_API_ENDPOINT=https://api.provider.com/v1
{PROVIDER}_MODEL=model_name
{PROVIDER}_MAX_REQUESTS=60
{PROVIDER}_TIMEOUT=30
```

### 2. Django Settings

Add to your `settings.py`:

```python
AI_SERVICES_CONFIG = {
    'openai': {
        'service_type': 'image_generation',
        'api_endpoint': 'https://api.openai.com/v1',
        'model_name': 'dall-e-3',
        'max_requests_per_minute': 60,
        'timeout_seconds': 30,
        'additional_params': {
            'quality': 'hd',
            'style': 'natural'
        }
    },
    'google_vision': {
        'service_type': 'computer_vision',
        'api_endpoint': 'https://vision.googleapis.com/v1',
        'max_requests_per_minute': 60,
        'timeout_seconds': 30
    },
    'anthropic': {
        'service_type': 'computer_vision',
        'api_endpoint': 'https://api.anthropic.com/v1',
        'model_name': 'claude-3-sonnet-20240229',
        'max_requests_per_minute': 60,
        'timeout_seconds': 30
    }
}

# Optional: Specify configuration file path
AI_SERVICES_CONFIG_FILE = '/path/to/ai_services_config.json'
```

### 3. Configuration File

Create `ai_services_config.json`:

```json
{
  "openai": {
    "service_type": "image_generation",
    "api_endpoint": "https://api.openai.com/v1",
    "model_name": "dall-e-3",
    "max_requests_per_minute": 60,
    "timeout_seconds": 30,
    "additional_params": {
      "quality": "hd",
      "style": "natural"
    }
  },
  "google_vision": {
    "service_type": "computer_vision",
    "api_endpoint": "https://vision.googleapis.com/v1",
    "max_requests_per_minute": 60,
    "timeout_seconds": 30
  }
}
```

## Development Deployment

### 1. Using Mock Services (No API Keys Required)

The system includes mock AI services for development and testing:

```bash
# Start development server
python manage.py runserver

# The mock provider is automatically registered
# No additional configuration needed
```

### 2. Testing AI Services

```bash
# Run AI service tests
python manage.py test api.tests.test_ai_services

# Test specific components
python manage.py test api.tests.test_ai_services.AIServiceRegistryTest
```

### 3. Frontend Development

```bash
cd frontend
npm install
npm start
```

The frontend will automatically connect to the AI service endpoints.

## Production Deployment

### 1. Docker Deployment

```dockerfile
# Use the provided Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=homescreen_project.settings
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "homescreen_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_CLOUD_API_KEY=${GOOGLE_CLOUD_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./media:/app/media
      - ./static:/app/static
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=homescreen
      - POSTGRES_USER=homescreen
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 3. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: homescreen-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: homescreen
  template:
    metadata:
      labels:
        app: homescreen
    spec:
      containers:
      - name: homescreen
        image: homescreen:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: homescreen-secrets
              key: secret-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-service-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## Monitoring and Health Checks

### 1. Health Check Endpoints

```bash
# Check AI services status
curl http://localhost:8000/api/ai-services/status/

# Check provider health
curl http://localhost:8000/api/ai-services/health/

# Check available providers
curl http://localhost:8000/api/ai-services/providers/
```

### 2. Logging Configuration

Add to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'ai_services.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api.ai_services': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'api.ai_enhanced_processor': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 3. Monitoring with Prometheus

```python
# Add to requirements.txt
django-prometheus

# Add to settings.py
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

## Security Considerations

### 1. API Key Management

- Store API keys in environment variables or secure vaults
- Never commit API keys to version control
- Use different keys for development and production
- Implement key rotation policies

### 2. Network Security

- Use HTTPS in production
- Implement proper CORS settings
- Use VPN or private networks for AI service communication
- Monitor API usage and implement rate limiting

### 3. Data Privacy

- Ensure compliance with data protection regulations
- Implement proper data retention policies
- Use secure image storage and processing
- Log access and usage for audit purposes

## Troubleshooting

### Common Issues

1. **AI Services Not Available**
   ```bash
   # Check service status
   python manage.py shell
   >>> from api.ai_services import ai_service_registry
   >>> print(ai_service_registry.get_registry_status())
   ```

2. **Configuration Issues**
   ```bash
   # Validate configuration
   python manage.py shell
   >>> from api.ai_services import ai_config_manager
   >>> print(ai_config_manager.get_manager_status())
   ```

3. **Provider Connection Issues**
   ```bash
   # Test provider health
   curl http://localhost:8000/api/ai-services/health/
   ```

### Performance Optimization

1. **Caching**: Implement Redis caching for service results
2. **Load Balancing**: Use multiple instances for high traffic
3. **Database Optimization**: Optimize queries and use connection pooling
4. **CDN**: Use CDN for static assets and generated images

## Backup and Recovery

1. **Database Backups**: Regular automated backups
2. **Media Files**: Backup generated images and uploads
3. **Configuration**: Version control all configuration files
4. **API Keys**: Secure backup of API credentials

## Scaling Considerations

1. **Horizontal Scaling**: Multiple application instances
2. **Database Scaling**: Read replicas and sharding
3. **AI Service Limits**: Monitor and manage API rate limits
4. **Storage Scaling**: Distributed file storage for images
