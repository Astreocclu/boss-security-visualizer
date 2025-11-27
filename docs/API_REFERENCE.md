# 📚 **Homescreen API Reference Documentation**

## 🚀 **OpenAI Image Generation Service API**

### **Class: OpenAIImageGenerationService**

The main service class for AI-powered screen visualization with advanced quality improvement and performance optimization.

---

## 🔄 **Iterative Quality Improvement Methods**

### **generate_with_iterative_improvement()**

Generates images with automatic quality improvement through multiple iterations.

```python
def generate_with_iterative_improvement(
    self,
    image: Image.Image,
    prompt: str,
    target_quality: float = 0.85,
    max_iterations: int = 3,
    progress_callback=None
) -> Dict[str, Any]
```

**Parameters:**
- `image` (PIL.Image): Source image for screen visualization
- `prompt` (str): Base prompt for image generation
- `target_quality` (float): Target quality score (0.0-1.0, default: 0.85)
- `max_iterations` (int): Maximum number of improvement iterations (default: 3)
- `progress_callback` (callable): Optional callback for progress updates

**Returns:**
```python
{
    'success': bool,                    # Whether generation succeeded
    'best_result': AIServiceResult,     # Best result achieved
    'best_quality': float,              # Highest quality score achieved
    'target_quality': float,            # Target quality that was aimed for
    'target_achieved': bool,            # Whether target was reached
    'total_iterations': int,            # Number of iterations performed
    'iterations': List[Dict],           # Details of each iteration
    'total_time': float,                # Total processing time in seconds
    'improvement_factor': float         # Quality improvement ratio
}
```

**Example Usage:**
```python
service = OpenAIImageGenerationService(config)
result = service.generate_with_iterative_improvement(
    image=house_image,
    prompt="Add professional security screens",
    target_quality=0.90,
    max_iterations=3
)

if result['success'] and result['target_achieved']:
    print(f"Target achieved in {result['total_iterations']} iterations")
    generated_image = result['best_result'].generated_image
```

---

### **generate_with_quality_enforcement()**

Generates images with strict quality enforcement and automatic retry.

```python
def generate_with_quality_enforcement(
    self,
    image: Image.Image,
    prompt: str,
    minimum_quality: float = None,
    progress_callback=None
) -> Dict[str, Any]
```

**Parameters:**
- `image` (PIL.Image): Source image for screen visualization
- `prompt` (str): Base prompt for image generation
- `minimum_quality` (float): Minimum acceptable quality (default: 0.75)
- `progress_callback` (callable): Optional callback for progress updates

**Returns:**
```python
{
    'success': bool,                    # Whether generation succeeded
    'best_result': AIServiceResult,     # Best result achieved
    'best_quality': float,              # Quality score of best result
    'minimum_quality': float,           # Minimum quality threshold
    'quality_enforced': bool,           # Whether enforcement was applied
    'enhancement_used': bool            # Whether enhanced prompts were used
}
```

---

## ⚡ **Performance Optimization Methods**

### **get_performance_metrics()**

Retrieves comprehensive performance metrics and analytics.

```python
def get_performance_metrics(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    'total_requests': int,              # Total number of requests processed
    'cache_hits': int,                  # Number of cache hits
    'cache_misses': int,                # Number of cache misses
    'total_cost': float,                # Total cost in USD
    'total_processing_time': float,     # Total processing time in seconds
    'average_quality': float,           # Average quality score
    'cache_hit_rate': float,            # Cache hit rate percentage
    'average_processing_time': float,   # Average processing time per request
    'average_cost_per_request': float,  # Average cost per request
    'cache_size': int,                  # Current cache size
    'cache_efficiency': float           # Cache efficiency percentage
}
```

**Example Usage:**
```python
metrics = service.get_performance_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1f}%")
print(f"Average quality: {metrics['average_quality']:.3f}")
print(f"Total cost: ${metrics['total_cost']:.2f}")
```

---

### **clear_performance_metrics()**

Clears all performance metrics (useful for testing or reset).

```python
def clear_performance_metrics(self) -> None
```

---

## 🖼️ **Reference System Methods**

### **_load_screen_references()**

Loads reference images for enhanced prompt generation.

```python
def _load_screen_references(self, screen_type: str) -> Dict[str, Any]
```

**Parameters:**
- `screen_type` (str): Type of screen ('security', 'lifestyle', 'solar', 'pet_resistant')

**Returns:**
```python
{
    'real_installs': List[Dict],        # Real installation photos
    'fabric_samples': List[Dict],       # Material and mesh patterns
    'top_tier_renders': List[Dict],     # Professional visualizations
    'angle_variations': List[Dict],     # Different perspective examples
    'lighting_examples': List[Dict],    # Various lighting conditions
    'brand_samples': List[Dict]         # Brand-specific references
}
```

**Reference Structure:**
```python
{
    'path': str,                        # Full path to reference image
    'filename': str,                    # Image filename
    'type': str                         # Reference category
}
```

---

### **_create_reference_enhanced_prompt()**

Creates enhanced prompts using loaded reference characteristics.

```python
def _create_reference_enhanced_prompt(
    self, 
    base_prompt: str, 
    screen_type: str, 
    references: Dict[str, Any]
) -> str
```

**Parameters:**
- `base_prompt` (str): Original prompt text
- `screen_type` (str): Type of screen for enhancement
- `references` (Dict): Loaded reference data

**Returns:**
- `str`: Enhanced prompt with reference-based specifications

**Enhancement Examples:**
- Real installs → "based on real professional installations"
- Fabric samples → "accurate mesh pattern and texture"
- Angle variations → "correct perspective alignment with window angles"
- Lighting examples → "natural lighting interaction with screen material"

---

## 💾 **Caching System Methods**

### **_generate_cache_key()**

Generates unique cache keys for request deduplication.

```python
def _generate_cache_key(self, image_hash: str, prompt: str, model: str) -> str
```

**Parameters:**
- `image_hash` (str): MD5 hash of source image
- `prompt` (str): Generation prompt
- `model` (str): AI model used

**Returns:**
- `str`: Unique cache key (MD5 hash)

---

### **_check_cache()**

Checks if a cached result exists and is still valid.

```python
def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `cache_key` (str): Cache key to check

**Returns:**
- `Dict` or `None`: Cached result if valid, None otherwise

**Cache TTL:** 24 hours (86400 seconds)

---

## 🔧 **Quality Assessment Methods**

### **_improve_prompt_based_on_quality()**

Improves prompts based on quality assessment gaps.

```python
def _improve_prompt_based_on_quality(
    self, 
    prompt: str, 
    current_quality: float, 
    target_quality: float
) -> str
```

**Parameters:**
- `prompt` (str): Original prompt
- `current_quality` (float): Current quality score
- `target_quality` (float): Target quality score

**Returns:**
- `str`: Improved prompt with quality enhancements

**Enhancement Logic:**
- Gap > 0.2: "ultra-high resolution", "professional architectural photography"
- Gap > 0.1: "high-resolution detail", "crisp edges", "enhanced contrast"
- Gap ≤ 0.1: "refined details", "improved lighting"

---

### **_create_maximum_quality_prompt()**

Creates maximum quality prompt for quality enforcement.

```python
def _create_maximum_quality_prompt(self, base_prompt: str) -> str
```

**Parameters:**
- `base_prompt` (str): Original prompt

**Returns:**
- `str`: Enhanced prompt with maximum quality terms

**Quality Terms Added:**
- "ultra-high resolution"
- "professional architectural photography"
- "exceptional detail and clarity"
- "photorealistic quality"
- "perfect lighting and shadows"
- "crisp edges and textures"
- "premium visualization standards"
- "maximum quality optimization"

---

## 📊 **Cost Tracking Methods**

### **_calculate_request_cost()**

Calculates estimated cost for API requests.

```python
def _calculate_request_cost(self, model: str, prompt_length: int, image_size: tuple) -> float
```

**Parameters:**
- `model` (str): AI model being used
- `prompt_length` (int): Length of prompt in characters
- `image_size` (tuple): Image dimensions (width, height)

**Returns:**
- `float`: Estimated cost in USD

**Pricing Logic:**
- GPT Image: $0.08 base cost, 1.5x for high resolution
- DALL-E 3: $0.08 HD, $0.04 standard
- Default: $0.04 fallback

---

### **_track_request_performance()**

Tracks performance metrics for monitoring.

```python
def _track_request_performance(
    self, 
    processing_time: float, 
    cost: float, 
    quality_score: float, 
    cache_hit: bool = False
) -> None
```

**Parameters:**
- `processing_time` (float): Request processing time in seconds
- `cost` (float): Request cost in USD
- `quality_score` (float): Quality assessment score
- `cache_hit` (bool): Whether request was served from cache

**Side Effects:**
- Updates internal usage statistics
- Logs performance summary every 10 requests
- Maintains running averages

---

## 🔍 **Optimization Methods**

### **_optimize_api_call_efficiency()**

Optimizes API calls for efficiency and cost reduction.

```python
def _optimize_api_call_efficiency(self, image: Image.Image, prompt: str) -> Dict[str, Any]
```

**Parameters:**
- `image` (PIL.Image): Source image to optimize
- `prompt` (str): Prompt to optimize

**Returns:**
```python
{
    'optimized_image': Image.Image,     # Optimized image
    'optimized_prompt': str,            # Optimized prompt
    'optimizations': {
        'image_optimized': bool,        # Whether image was resized
        'prompt_optimized': bool,       # Whether prompt was truncated
        'cache_eligible': bool,         # Whether result can be cached
        'estimated_cost': float,        # Estimated request cost
        'estimated_time': float         # Estimated processing time
    }
}
```

**Optimization Logic:**
- **Image**: Resize to max 1024x1024 if larger
- **Prompt**: Truncate to 150 words, preserve key terms
- **Cost**: Calculate based on optimized parameters
- **Time**: Estimate based on complexity

---

### **_estimate_processing_time()**

Estimates processing time based on request complexity.

```python
def _estimate_processing_time(self, image_size: tuple, prompt_length: int) -> float
```

**Parameters:**
- `image_size` (tuple): Image dimensions
- `prompt_length` (int): Prompt length in characters

**Returns:**
- `float`: Estimated processing time in seconds

**Estimation Logic:**
- Base time: 15 seconds
- Large images (>1024x1024): +50% time
- Medium images (>512x512): +20% time
- Long prompts (>500 chars): +30% time
- Medium prompts (>200 chars): +10% time

---

## 🚨 **Error Handling**

All methods implement comprehensive error handling with:
- **Logging**: Detailed error messages with context
- **Graceful Degradation**: Fallback to simpler methods when possible
- **Exception Propagation**: Proper exception handling and re-raising
- **Resource Cleanup**: Automatic cleanup of temporary resources

**Common Exception Types:**
- `ValueError`: Invalid parameters or configuration
- `ConnectionError`: API connectivity issues
- `TimeoutError`: Request timeout exceeded
- `AuthenticationError`: Invalid API credentials
- `RateLimitError`: API rate limit exceeded

---

## 📈 **Usage Examples**

### **Complete Workflow Example**

```python
from api.ai_services.providers.openai_provider import OpenAIImageGenerationService
from api.ai_services.config import AIServiceConfig
from api.ai_services.interfaces import AIServiceType
from PIL import Image

# Initialize service
config = AIServiceConfig(
    service_name="openai_generation",
    service_type=AIServiceType.IMAGE_GENERATION,
    api_key="your-openai-api-key",
    api_endpoint="https://api.openai.com/v1"
)
service = OpenAIImageGenerationService(config)

# Load image
image = Image.open("house_photo.jpg")

# Generate with quality improvement
result = service.generate_with_iterative_improvement(
    image=image,
    prompt="Add professional security screens with stainless steel mesh",
    target_quality=0.90,
    max_iterations=3
)

# Check results
if result['success']:
    print(f"Quality achieved: {result['best_quality']:.3f}")
    if result['target_achieved']:
        print("Target quality reached!")
    
    # Save generated image
    result['best_result'].generated_image.save("result.jpg")
    
    # Get performance metrics
    metrics = service.get_performance_metrics()
    print(f"Total cost: ${metrics['total_cost']:.2f}")
    print(f"Cache hit rate: {metrics['cache_hit_rate']:.1f}%")
```

This API reference provides comprehensive documentation for all Phase 3 advanced features and methods implemented in the OpenAI Image Generation Service.
