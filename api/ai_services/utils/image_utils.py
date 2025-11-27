"""
Image utility functions for AI services.
Extracted from openai_provider.py for better code organization.
"""

import hashlib
import io
import logging
from typing import Tuple, Optional
from PIL import Image

logger = logging.getLogger(__name__)


def get_image_hash(image: Image.Image) -> str:
    """
    Generate MD5 hash for image content.
    
    Args:
        image: PIL Image object
        
    Returns:
        str: MD5 hash of image content
    """
    try:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return hashlib.md5(img_byte_arr).hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate image hash: {str(e)}")
        return "unknown_hash"


def generate_cache_key(image_hash: str, prompt: str, model: str) -> str:
    """
    Generate cache key for request deduplication.
    
    Args:
        image_hash: MD5 hash of source image
        prompt: Generation prompt
        model: AI model name
        
    Returns:
        str: MD5 hash cache key
    """
    try:
        cache_string = f"{image_hash}_{prompt}_{model}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate cache key: {str(e)}")
        return "unknown_key"


def optimize_image_for_api(image: Image.Image, max_dimension: int = 1024) -> Tuple[Image.Image, bool]:
    """
    Optimize image for API efficiency while maintaining quality.
    
    Args:
        image: Source image to optimize
        max_dimension: Maximum width or height
        
    Returns:
        Tuple of (optimized_image, was_resized)
    """
    try:
        original_size = image.size
        
        # Check if resizing is needed
        if original_size[0] <= max_dimension and original_size[1] <= max_dimension:
            return image, False
        
        # Calculate new size maintaining aspect ratio
        ratio = min(max_dimension / original_size[0], max_dimension / original_size[1])
        new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
        
        # Resize with high-quality resampling
        optimized_image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        logger.info(f"Image optimized: {original_size} -> {new_size}")
        return optimized_image, True
        
    except Exception as e:
        logger.error(f"Image optimization failed: {str(e)}")
        return image, False


def validate_image(image: Image.Image) -> bool:
    """
    Validate image for processing.
    
    Args:
        image: PIL Image to validate
        
    Returns:
        bool: True if image is valid for processing
    """
    try:
        if not isinstance(image, Image.Image):
            return False
        
        # Check image size
        width, height = image.size
        if width < 100 or height < 100:
            logger.warning(f"Image too small: {width}x{height}")
            return False
        
        if width > 4096 or height > 4096:
            logger.warning(f"Image too large: {width}x{height}")
            return False
        
        # Check image mode
        if image.mode not in ['RGB', 'RGBA', 'L']:
            logger.warning(f"Unsupported image mode: {image.mode}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        return False


def convert_image_to_base64(image: Image.Image, format: str = 'JPEG', quality: int = 95) -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image: PIL Image to convert
        format: Output format (JPEG, PNG)
        quality: JPEG quality (1-100)
        
    Returns:
        str: Base64 encoded image
    """
    try:
        # Convert RGBA to RGB for JPEG
        if format.upper() == 'JPEG' and image.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        save_kwargs = {'format': format}
        if format.upper() == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        
        image.save(img_byte_arr, **save_kwargs)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Encode to base64
        import base64
        return base64.b64encode(img_byte_arr).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Image to base64 conversion failed: {str(e)}")
        raise


def estimate_processing_time(image_size: Tuple[int, int], prompt_length: int) -> float:
    """
    Estimate processing time based on request complexity.
    
    Args:
        image_size: Image dimensions (width, height)
        prompt_length: Length of prompt in characters
        
    Returns:
        float: Estimated processing time in seconds
    """
    try:
        # Base time estimates
        base_time = 15.0  # Base processing time in seconds
        
        # Image size factor
        pixel_count = image_size[0] * image_size[1]
        if pixel_count > 1024 * 1024:
            base_time *= 1.5
        elif pixel_count > 512 * 512:
            base_time *= 1.2
        
        # Prompt complexity factor
        if prompt_length > 500:
            base_time *= 1.3
        elif prompt_length > 200:
            base_time *= 1.1
        
        return base_time
        
    except Exception as e:
        logger.error(f"Processing time estimation failed: {str(e)}")
        return 30.0  # Default estimate


def calculate_image_quality_score(image: Image.Image) -> float:
    """
    Calculate basic image quality score based on technical metrics.
    
    Args:
        image: PIL Image to assess
        
    Returns:
        float: Quality score (0.0-1.0)
    """
    try:
        import numpy as np
        from PIL import ImageStat, ImageFilter
        
        # Convert to grayscale for analysis
        gray_image = image.convert('L')
        
        # Calculate sharpness (edge detection)
        edges = gray_image.filter(ImageFilter.FIND_EDGES)
        edge_array = np.array(edges)
        sharpness = np.var(edge_array) / 10000
        
        # Calculate contrast
        stat = ImageStat.Stat(gray_image)
        contrast = stat.stddev[0] / 128
        
        # Calculate brightness distribution
        brightness_mean = stat.mean[0] / 255
        brightness_std = stat.stddev[0] / 255
        
        # Color analysis for RGB images
        if image.mode in ['RGB', 'RGBA']:
            color_stat = ImageStat.Stat(image)
            if len(color_stat.mean) >= 3:
                r_mean, g_mean, b_mean = color_stat.mean[:3]
                color_balance = 1.0 - (abs(r_mean - g_mean) + abs(g_mean - b_mean) + abs(r_mean - b_mean)) / (3 * 255)
            else:
                color_balance = 0.8
        else:
            color_balance = 0.8
        
        # Combine metrics into overall quality score
        technical_score = (min(1.0, sharpness) + min(1.0, contrast) + max(0.0, color_balance)) / 3
        
        # Resolution score
        width, height = image.size
        resolution_score = 1.0 if width * height > 800000 else 0.8 if width * height > 300000 else 0.6
        
        # Composition score (aspect ratio)
        aspect_ratio = width / height
        composition_score = 1.0 if 1.2 <= aspect_ratio <= 2.0 else 0.8
        
        # Overall quality
        overall_quality = (technical_score * 0.5 + composition_score * 0.25 + resolution_score * 0.25)
        
        return min(1.0, max(0.0, overall_quality))
        
    except Exception as e:
        logger.error(f"Quality score calculation failed: {str(e)}")
        return 0.5  # Default neutral score
