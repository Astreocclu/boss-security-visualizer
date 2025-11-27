"""
AI Services Utilities Package

This package contains utility functions and classes extracted from the main
AI service providers for better code organization and maintainability.

Modules:
- image_utils: Image processing and optimization utilities
- prompt_utils: Prompt engineering and optimization utilities  
- performance_utils: Performance monitoring and caching utilities
"""

from .image_utils import (
    get_image_hash,
    generate_cache_key,
    optimize_image_for_api,
    validate_image,
    convert_image_to_base64,
    estimate_processing_time,
    calculate_image_quality_score
)

from .prompt_utils import (
    optimize_prompt_for_api,
    improve_prompt_based_on_quality,
    create_maximum_quality_prompt,
    create_reference_enhanced_prompt,
    get_material_specifications,
    create_chatgpt_quality_prompt
)

from .performance_utils import (
    PerformanceTracker,
    calculate_request_cost,
    optimize_api_call_efficiency,
    estimate_processing_time,
    CacheManager
)

__all__ = [
    # Image utilities
    'get_image_hash',
    'generate_cache_key', 
    'optimize_image_for_api',
    'validate_image',
    'convert_image_to_base64',
    'calculate_image_quality_score',
    
    # Prompt utilities
    'optimize_prompt_for_api',
    'improve_prompt_based_on_quality',
    'create_maximum_quality_prompt',
    'create_reference_enhanced_prompt',
    'get_material_specifications',
    'create_chatgpt_quality_prompt',
    
    # Performance utilities
    'PerformanceTracker',
    'calculate_request_cost',
    'optimize_api_call_efficiency',
    'estimate_processing_time',
    'CacheManager'
]
