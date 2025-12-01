# Weather Change Diagnostic Report

**Date:** 2025-12-01
**Branch:** fix/scope-mismatch-20251201-0956
**Investigator:** Claude Code

---

## Summary

**Finding:** Weather changes occur during the **PATIO insertion step**, not cleanup. The issue is **image-dependent** - some source images are affected, others are not.

**Root Cause:** The patio enclosure prompt does not explicitly instruct Gemini to preserve sky/weather, and the large structural changes involved in enclosing a patio give Gemini more "creative freedom" to alter the background.

---

## Evidence: Pipeline Step Analysis

### Image Set A: Brick House with Covered Patio (Pool)
**Source:** Multiple runs with same house image

| Sequence | Cleanup | Patio | Windows | Weather Change? |
|----------|---------|-------|---------|-----------------|
| 20251201_003000 | Overcast ☁️ | **BLUE SKY** ☀️ | Blue ☀️ | **YES at PATIO** |
| 20251201_154710 | Overcast ☁️ | **Clearing** 🌤️ | Blue ☀️ | **YES at PATIO** |
| 20251201_155429 | Overcast ☁️ | **Blue** ☀️ | (skipped) | **YES at PATIO** |
| 20251201_160332 | Overcast ☁️ | (skipped) | Overcast ☁️ | **NO** (windows-only) |
| 20251201_160426 | Overcast ☁️ | (skipped) | Overcast ☁️ | **NO** (windows-only) |

### Image Set B: Modern Stucco House with Balcony (Pool)
**Source:** Different house image

| Sequence | Cleanup | Patio | Windows | Weather Change? |
|----------|---------|-------|---------|-----------------|
| 20251130_191218 | Overcast ☁️ | Overcast ☁️ | Overcast ☁️ | **NO** |
| 20251130_192843 | Overcast ☁️ | Overcast ☁️ | Overcast ☁️ | **NO** |

---

## Visual Evidence

### Brick House - Weather CHANGES at Patio Step

**Sequence: 20251201_003000 → 003015 → 003029**

```
┌─────────────────────────────────────────────────────────────────┐
│  0_cleanup.jpg                                                  │
│  Sky: OVERCAST (gray clouds, moody)                             │
│  Patio: Open, no screens                                        │
│  Windows: Original glass                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ PATIO STEP
┌─────────────────────────────────────────────────────────────────┐
│  1_patio.jpg                                                    │
│  Sky: BLUE SKY (sunny, clear) ← CHANGED!                        │
│  Patio: Enclosed with screen mesh                               │
│  Windows: Original glass                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ WINDOWS STEP
┌─────────────────────────────────────────────────────────────────┐
│  2_windows.jpg                                                  │
│  Sky: Still blue (inherited from patio step)                    │
│  Patio: Enclosed                                                │
│  Windows: Now have security screens                             │
└─────────────────────────────────────────────────────────────────┘
```

### Brick House - Windows-Only Preserves Weather

**Sequence: 20251201_160332 → 160350** (scope: windows only, no patio)

```
┌─────────────────────────────────────────────────────────────────┐
│  0_cleanup.jpg                                                  │
│  Sky: OVERCAST                                                  │
│  Patio: Open (unchanged)                                        │
│  Windows: Original glass                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ WINDOWS STEP (patio skipped)
┌─────────────────────────────────────────────────────────────────┐
│  2_windows.jpg                                                  │
│  Sky: OVERCAST (preserved!) ✓                                   │
│  Patio: Open (unchanged)                                        │
│  Windows: Now have security screens                             │
└─────────────────────────────────────────────────────────────────┘
```

### Modern House - Weather Preserved Throughout

**Sequence: 20251130_192843 → 192857 → 192912**

```
┌─────────────────────────────────────────────────────────────────┐
│  0_cleanup.jpg → 1_patio.jpg → 2_windows.jpg                    │
│  Sky: OVERCAST → OVERCAST → OVERCAST ✓                          │
│  All steps preserve original weather                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pattern Analysis

### When Weather Changes
- **PATIO step on brick house image** - Consistently changes overcast → blue
- Large structural changes (enclosing open area) give Gemini more freedom

### When Weather Is Preserved
- **WINDOWS-only runs** - Weather preserved regardless of image
- **Modern house image** - Weather preserved even with patio step
- **CLEANUP step** - Always preserves weather (prompt explicitly says to)

### Hypothesis
The patio enclosure operation involves:
1. Filling large open structural voids
2. Adding mullions/supports
3. Significant image regeneration in that area

This gives Gemini more context to "improve" or "normalize" the image, and it defaults to sunny/blue sky as a more "appealing" result.

---

## Current Prompts Analysis

### Cleanup Prompt (Weather Preserved ✓)
```python
def get_cleanup_prompt():
    return "Identify and remove temporary clutter: garbage cans, hoses, toys,
            and loose leaves. Preserve all structural elements: columns, fans,
            lights, furniture, and concrete pads. Maintain the original
            background pixels exactly."
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          This instruction works!
```

### Patio Insertion Prompt (Weather Changes ✗)
```python
def get_screen_insertion_prompt(feature_type: str, options: dict):
    # ...
    base_prompt = f"Photorealistic inpainting. Install {color} security screens
                   on the {feature_type}. Render the screen material as a
                   heavy-duty {color} mesh with {opacity_desc}..."

    if feature_type == "patio enclosure":
        base_prompt += " Install vertical aluminum structural mullions every
                        5 feet to support the screen span."
        base_prompt += " Focus EXCLUSIVELY on enclosing the open patio/porch
                        areas. Leave all standard windows and other openings
                        in their original state."
        # NO SKY/WEATHER PRESERVATION INSTRUCTION!
```

### Windows Prompt (Weather Preserved ✓)
```python
# Same base prompt, but smaller changes = less opportunity for Gemini to alter sky
base_prompt = f"Photorealistic inpainting. Install {color} security screens
               on the {feature_type}..."
# Window screens are small, localized changes - sky not affected
```

---

## Log Evidence

```
INFO 2025-12-01 15:47:10 Pipeline Step: cleanup complete.
INFO 2025-12-01 15:47:31 Pipeline Step: patio complete.  ← Weather changed here
INFO 2025-12-01 15:47:47 Pipeline Step: windows complete.
INFO 2025-12-01 15:48:02 Quality Check: Score=1.0, Reason=The model correctly
     enclosed the open patio area with screens as requested...
```

Note: Quality check gives 1.0 score even when weather changes - it's not checking for weather preservation!

---

## Files Analyzed

| File | Step | Weather |
|------|------|---------|
| `pipeline_20251201_003000_0_cleanup.jpg` | cleanup | Overcast |
| `pipeline_20251201_003015_1_patio.jpg` | patio | **Blue** |
| `pipeline_20251201_003029_2_windows.jpg` | windows | Blue |
| `pipeline_20251201_154710_0_cleanup.jpg` | cleanup | Overcast |
| `pipeline_20251201_154731_1_patio.jpg` | patio | **Clearing** |
| `pipeline_20251201_154747_2_windows.jpg` | windows | Blue |
| `pipeline_20251201_160332_0_cleanup.jpg` | cleanup | Overcast |
| `pipeline_20251201_160350_2_windows.jpg` | windows | Overcast ✓ |
| `pipeline_20251130_191218_0_cleanup.jpg` | cleanup | Overcast |
| `pipeline_20251130_191231_1_patio.jpg` | patio | Overcast ✓ |
| `pipeline_20251130_191245_2_windows.jpg` | windows | Overcast ✓ |
| `pipeline_20251130_192843_0_cleanup.jpg` | cleanup | Overcast |
| `pipeline_20251130_192857_1_patio.jpg` | patio | Overcast ✓ |
| `pipeline_20251130_192912_2_windows.jpg` | windows | Overcast ✓ |

---

## Recommended Fix

### Option 1: Add Sky Preservation to Patio Prompt (Recommended)

```python
def get_screen_insertion_prompt(feature_type: str, options: dict):
    # ...
    base_prompt = f"Photorealistic inpainting. Install {color} security screens
                   on the {feature_type}..."

    if feature_type == "patio enclosure":
        base_prompt += " Install vertical aluminum structural mullions..."
        base_prompt += " Focus EXCLUSIVELY on enclosing the open patio/porch areas..."
        # ADD THIS:
        base_prompt += " CRITICAL: Preserve the original sky, weather, lighting,
                        and atmosphere exactly. Do not alter clouds, sun position,
                        or overall lighting conditions."

    return base_prompt
```

### Option 2: Add Global Sky Preservation to All Insertion Prompts

```python
def get_screen_insertion_prompt(feature_type: str, options: dict):
    # ...
    base_prompt = f"Photorealistic inpainting. Install {color} security screens..."

    # Add to ALL insertions:
    base_prompt += " Preserve the original sky, weather, and background exactly.
                    Only modify the specific feature being screened."

    return base_prompt
```

### Option 3: Add Weather Check to Quality Prompt

```python
def get_quality_check_prompt(scope: dict = None):
    base_prompt = """
    You are a Quality Control AI...

    # ADD THIS CHECK:
    4. Has the sky/weather changed from the reference image?
       - If weather has changed (cloudy→sunny or vice versa), this is a HALLUCINATION.
       - Score MUST be below 0.5 if weather changed significantly.
    """
```

---

## Summary

| Component | Issue | Fix |
|-----------|-------|-----|
| Cleanup Prompt | ✓ Working | None needed |
| Patio Prompt | ✗ No sky preservation | Add preservation instruction |
| Windows Prompt | ✓ Working (small changes) | Consider adding for safety |
| Doors Prompt | ? Untested | Add preservation instruction |
| Quality Check | ✗ Doesn't check weather | Add weather validation |

---

## Next Steps

- [ ] Update `get_screen_insertion_prompt()` in `api/tenants/boss/prompts.py`
- [ ] Add sky/weather preservation instruction to patio enclosure case
- [ ] Consider adding to all insertion prompts for consistency
- [ ] Update quality check to validate weather preservation
- [ ] Test with brick house image to confirm fix
