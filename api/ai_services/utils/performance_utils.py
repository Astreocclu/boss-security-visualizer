"""
Performance monitoring and optimization utilities for AI services.
Extracted from openai_provider.py for better code organization.
"""

import logging
import time
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Track and analyze performance metrics for AI services."""
    
    def __init__(self):
        self.usage_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cost': 0.0,
            'total_processing_time': 0.0,
            'average_quality': 0.0
        }
        self.performance_monitoring_enabled = True
    
    def track_request_performance(self, processing_time: float, cost: float, 
                                quality_score: float, cache_hit: bool = False) -> None:
        """
        Track performance metrics for monitoring and optimization.
        
        Args:
            processing_time: Request processing time in seconds
            cost: Request cost in USD
            quality_score: Quality assessment score
            cache_hit: Whether request was served from cache
        """
        if not self.performance_monitoring_enabled:
            return
        
        try:
            self.usage_stats['total_requests'] += 1
            self.usage_stats['total_processing_time'] += processing_time
            self.usage_stats['total_cost'] += cost
            
            if cache_hit:
                self.usage_stats['cache_hits'] += 1
            else:
                self.usage_stats['cache_misses'] += 1
            
            # Update average quality (running average)
            current_avg = self.usage_stats['average_quality']
            total_requests = self.usage_stats['total_requests']
            self.usage_stats['average_quality'] = ((current_avg * (total_requests - 1)) + quality_score) / total_requests
            
            # Log performance metrics periodically
            if self.usage_stats['total_requests'] % 10 == 0:
                self._log_performance_summary()
                
        except Exception as e:
            logger.error(f"Performance tracking failed: {str(e)}")
    
    def _log_performance_summary(self) -> None:
        """Log performance summary for monitoring."""
        try:
            stats = self.usage_stats
            cache_hit_rate = (stats['cache_hits'] / stats['total_requests']) * 100 if stats['total_requests'] > 0 else 0
            avg_processing_time = stats['total_processing_time'] / stats['total_requests'] if stats['total_requests'] > 0 else 0
            
            logger.info(f"Performance Summary - Requests: {stats['total_requests']}, "
                       f"Cache Hit Rate: {cache_hit_rate:.1f}%, "
                       f"Avg Processing Time: {avg_processing_time:.2f}s, "
                       f"Total Cost: ${stats['total_cost']:.4f}, "
                       f"Avg Quality: {stats['average_quality']:.3f}")
                       
        except Exception as e:
            logger.error(f"Performance summary logging failed: {str(e)}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Returns:
            Dict with comprehensive performance metrics
        """
        try:
            stats = self.usage_stats.copy()
            
            # Calculate derived metrics
            if stats['total_requests'] > 0:
                stats['cache_hit_rate'] = (stats['cache_hits'] / stats['total_requests']) * 100
                stats['average_processing_time'] = stats['total_processing_time'] / stats['total_requests']
                stats['average_cost_per_request'] = stats['total_cost'] / stats['total_requests']
            else:
                stats['cache_hit_rate'] = 0.0
                stats['average_processing_time'] = 0.0
                stats['average_cost_per_request'] = 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Performance metrics retrieval failed: {str(e)}")
            return self.usage_stats.copy()
    
    def clear_performance_metrics(self) -> None:
        """Clear performance metrics (for testing or reset)."""
        self.usage_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cost': 0.0,
            'total_processing_time': 0.0,
            'average_quality': 0.0
        }
        logger.info("Performance metrics cleared")


def calculate_request_cost(model: str, prompt_length: int, image_size: Tuple[int, int]) -> float:
    """
    Calculate estimated cost for API requests.
    
    Args:
        model: AI model being used
        prompt_length: Length of prompt in characters
        image_size: Image dimensions (width, height)
        
    Returns:
        float: Estimated cost in USD
    """
    try:
        # Cost estimates based on OpenAI pricing (as of 2024)
        if model == "gpt-image-1":
            # GPT Image pricing (estimated)
            base_cost = 0.08  # Base cost per image
            if image_size[0] * image_size[1] > 1024 * 1024:
                base_cost *= 1.5  # Higher resolution multiplier
            return base_cost
        elif model == "dall-e-3":
            # DALL-E 3 pricing
            if image_size[0] * image_size[1] > 1024 * 1024:
                return 0.080  # HD quality
            else:
                return 0.040  # Standard quality
        else:
            return 0.040  # Default estimate
            
    except Exception as e:
        logger.error(f"Cost calculation failed: {str(e)}")
        return 0.040  # Default fallback


def optimize_api_call_efficiency(image, prompt: str) -> Dict[str, Any]:
    """
    Optimize API call for efficiency and cost reduction.
    
    Args:
        image: PIL Image to optimize
        prompt: Prompt to optimize
        
    Returns:
        Dict with optimization results and optimized parameters
    """
    try:
        from .image_utils import optimize_image_for_api
        from .prompt_utils import optimize_prompt_for_api
        
        optimizations = {
            'image_optimized': False,
            'prompt_optimized': False,
            'cache_eligible': True,
            'estimated_cost': 0.0,
            'estimated_time': 0.0
        }
        
        # Image optimization
        optimized_image, was_resized = optimize_image_for_api(image, max_dimension=1024)
        optimizations['image_optimized'] = was_resized
        
        # Prompt optimization
        original_prompt_length = len(prompt)
        optimized_prompt = optimize_prompt_for_api(prompt, max_length=1000)
        optimizations['prompt_optimized'] = len(optimized_prompt) < original_prompt_length
        
        # Cost and time estimation
        optimizations['estimated_cost'] = calculate_request_cost("gpt-image-1", len(optimized_prompt), optimized_image.size)
        optimizations['estimated_time'] = estimate_processing_time(optimized_image.size, len(optimized_prompt))
        
        return {
            'optimized_image': optimized_image,
            'optimized_prompt': optimized_prompt,
            'optimizations': optimizations
        }
        
    except Exception as e:
        logger.error(f"API call optimization failed: {str(e)}")
        return {
            'optimized_image': image,
            'optimized_prompt': prompt,
            'optimizations': {'cache_eligible': True}
        }


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


class CacheManager:
    """Manage caching for AI service requests."""
    
    def __init__(self, ttl_seconds: int = 86400):  # 24 hours default
        self.cache = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, cache_key: str) -> Any:
        """
        Get cached result if valid.
        
        Args:
            cache_key: Cache key to lookup
            
        Returns:
            Cached result or None if not found/expired
        """
        try:
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                
                # Check if cache entry is still valid
                if time.time() - cached_result['timestamp'] < self.ttl_seconds:
                    logger.info(f"Cache hit for key: {cache_key[:8]}...")
                    return cached_result['result']
                else:
                    # Remove expired cache entry
                    del self.cache[cache_key]
                    logger.info(f"Cache expired for key: {cache_key[:8]}...")
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
            return None
    
    def set(self, cache_key: str, result: Any) -> None:
        """
        Store result in cache.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        try:
            self.cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            logger.info(f"Stored result in cache: {cache_key[:8]}...")
            
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            int: Number of entries removed
        """
        try:
            current_time = time.time()
            expired_keys = [
                key for key, value in self.cache.items()
                if current_time - value['timestamp'] >= self.ttl_seconds
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.info(f"Removed {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")
            return 0
