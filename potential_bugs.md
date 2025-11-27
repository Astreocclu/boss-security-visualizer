# Potential Bugs Causing "Output = Input" Issue

## Issue
The web app returns the exact same image as input, indicating the AI pipeline is failing silently.

## Root Cause Candidates

### 1. **API Key Not Being Passed**
**File:** `api/ai_services/providers/gemini_provider.py` (Line 64)
```python
self.visualizer = ScreenVisualizer(api_key=config.api_key)
```
**Problem:** `config.api_key` might be `None` because:
- `AIServiceConfig` is created without an API key in `factory.py` (Line 69-72)
- The factory creates a default config with `service_name` and `service_type` only
- No API key is pulled from environment in the factory

**Fix:** Pass `api_key=os.environ.get("GOOGLE_API_KEY")` explicitly when creating `ScreenVisualizer`.

---

### 2. **Silent Fallback in ScreenVisualizer**
**File:** `api/ai_services/screen_visualizer.py` (Lines 233-238)
```python
except Exception as e:
    logger.error(f"Image generation failed: {e}")
    for content in contents:
        if isinstance(content, Image.Image):
            return content
    return Image.new('RGB', (512, 512), color='gray')
```
**Problem:** If ANY exception occurs (invalid API key, network error, etc.), the code returns the original image without raising an error.

**Fix:** Remove the fallback or make it more restrictive. Let exceptions bubble up.

---

### 3. **Missing API Key in ScreenVisualizer Init**
**File:** `api/ai_services/screen_visualizer.py` (Lines 35-42)
```python
def __init__(self, api_key: Optional[str] = None):
    self.model_name = "gemini-3-pro-image-preview"
    if api_key:
        self.client = genai.Client(api_key=api_key)
    else:
        self.client = genai.Client()  # Uses GOOGLE_API_KEY from env
```
**Problem:** If `api_key` is `None` (which it likely is per Bug #1), the client tries to use env var. But if the env var isn't loaded in the background thread context, this will fail.

**Fix:** Explicitly require `api_key` or verify env var is set before init.

---

### 4. **Image Extraction Failure**
**File:** `api/ai_services/screen_visualizer.py` (Lines 226-231)
```python
if response.candidates and response.candidates[0].content.parts:
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            from io import BytesIO
            return Image.open(BytesIO(part.inline_data.data))
```
**Problem:** If the response structure is different (e.g., no `inline_data`, or image is in a different field), this extraction fails and hits the fallback.

**Fix:** Add logging to show what's actually in the response.

---

### 5. **Wrong Response Modality**
**File:** `api/ai_services/screen_visualizer.py` (Lines 207-209)
```python
config_args = {
    "response_modalities": ["TEXT", "IMAGE"] if include_thoughts else ["IMAGE"],
}
```
**Problem:** The API might not support `["TEXT", "IMAGE"]` or `["IMAGE"]` format. The model might require a different configuration.

**Fix:** Test with just `response_modalities=["IMAGE"]` for all calls.

---

### 6. **ImageGenerationConfig Incompatibility**
**File:** `api/ai_services/screen_visualizer.py` (Lines 215-219)
```python
if hasattr(types, 'ImageGenerationConfig'):
    config_args['image_generation_config'] = types.ImageGenerationConfig(
        guidance_scale=70,
        person_generation="dont_generate_people"
    )
```
**Problem:** `ImageGenerationConfig` might not exist, or these parameters might be invalid for `gemini-3-pro-image-preview`.

**Fix:** Remove or test without this config.

---

### 7. **No Logging of Actual API Errors**
**File:** `api/ai_services/screen_visualizer.py` (Line 224)
```python
except Exception as e:
    if "429" in str(e) and attempt < max_retries - 1:
        # ...
    else:
        raise e
```
**Problem:** The exception is caught in the outer `try/except` (Line 233) and logged with `logger.error`, but the actual error message might not be making it to the logs.

**Fix:** Add more verbose logging or re-raise the exception instead of falling back.

---

## Debugging Steps

1. **Check API Key Flow:**
   - Add `print(f"API Key in ScreenVisualizer: {api_key[:10]}...")` in `__init__`
   - Add `print(f"Config API Key: {config.api_key}")` in `GeminiImageGenerationService.__init__`

2. **Add Verbose Logging:**
   - In `_generate_content_image`, log the full response structure
   - Log every exception with full traceback using `logger.exception()`

3. **Test Direct API Call:**
   - Run `scripts/test_gemini_live.py` with explicit API key
   - Verify it works outside the Django context

4. **Remove Fallbacks Temporarily:**
   - Comment out the `return content` fallback in `_generate_content_image`
   - Force the system to crash and reveal the real error

---

## Most Likely Bug
**Bug #1 + Bug #2 Combined:**
The factory creates a config without an API key → `GeminiImageGenerationService` gets `config.api_key=None` → `ScreenVisualizer` tries to use env var but fails in background thread → API call fails → fallback returns original image → no error logged to user.
