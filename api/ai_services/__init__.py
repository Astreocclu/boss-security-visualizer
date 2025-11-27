"""
AI Services Package for Homescreen Visualization

This package provides a service-agnostic abstraction layer for AI image generation
and computer vision services. It supports multiple AI providers and can be easily
extended to work with new services.

Key Components:
- Base interfaces for AI services
- Service registry and factory pattern
- Configuration management
- Provider-specific implementations
"""

from .interfaces import (
    AIImageGenerationService,
    AIVisionService,
    AIServiceConfig,
    AIServiceResult,
    WindowDetectionResult,
    ScreenAnalysisResult,
    QualityAssessmentResult,
    AIServiceType,
    ProcessingStatus,
    AIServiceProvider
)

from .registry import AIServiceRegistry, ai_service_registry
from .factory import AIServiceFactory
from .config import AIServiceConfigManager, ai_config_manager

__all__ = [
    'AIImageGenerationService',
    'AIVisionService',
    'AIServiceConfig',
    'AIServiceResult',
    'WindowDetectionResult',
    'ScreenAnalysisResult',
    'QualityAssessmentResult',
    'AIServiceType',
    'ProcessingStatus',
    'AIServiceProvider',
    'AIServiceRegistry',
    'AIServiceFactory',
    'AIServiceConfigManager',
    'ai_service_registry',
    'ai_config_manager'
]
