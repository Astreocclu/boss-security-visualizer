"""
AI Service Providers Package

This package contains implementations of AI service providers that can be
used with the homescreen visualization system. Each provider implements
the standard interfaces defined in the parent package.

Available Providers:
- MockProvider: For testing and development
- OpenAIProvider: OpenAI GPT-4 Vision and DALL-E integration
- GoogleProvider: Google Cloud Vision API integration
- AnthropicProvider: Anthropic Claude Vision integration
"""

from .base_provider import BaseAIProvider
from .gemini_provider import GeminiProvider

__all__ = [
    'BaseAIProvider',
    'GeminiProvider'
]
