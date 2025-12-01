# Scope Mismatch Diagnostic Report

**Date:** 2025-12-01
**Branch:** fix/scope-mismatch-20251201-0956
**Investigator:** Claude Code

---

## Summary

**Finding:** NOT A BUG - The empty `scope: {}` values are historical data from before the scope system was implemented.

---

## Diagnostic Commands Run

```bash
# Git safety
git stash -u
git checkout -b fix/scope-mismatch-20251201-0956
git stash pop

# Diagnostic query
python3 manage.py shell -c "
from api.models import VisualizationRequest
for r in VisualizationRequest.objects.order_by('id'):
    print(f'ID: {r.id}, Status: {r.status}, Scope: {r.scope}, Categories: {r.screen_categories}')
"
```

---

## Data Analysis

### Total Records: 104 VisualizationRequests

### Scope Distribution

| ID Range | Scope Status | Count | Notes |
|----------|--------------|-------|-------|
| 1-35 | `{}` (empty) | 35 | Pre-scope implementation |
| 36-104 | Populated | 69 | Scope working correctly |

### Scope Breakdown (IDs 36-104)

| Scope Pattern | Count | Example IDs |
|---------------|-------|-------------|
| `{windows: True, doors: False, patio: True}` | ~50 | 43, 44, 49, 51, 53-60, etc. |
| `{windows: False, doors: False, patio: True}` | ~15 | 36, 37, 39-42, 46, 47, 50, etc. |
| `{windows: True, doors: False, patio: False}` | ~5 | 38, 45, 48, 61, 63, 66, 67, 77 |
| `{windows: False, doors: True, patio: False}` | 1 | 93 |

### screen_categories Field (Legacy)

| Status | Count | Example IDs |
|--------|-------|-------------|
| Populated | 8 | 1, 3, 12, 17, 18, 19, 20, 21, 22, 24 |
| Empty `[]` | 96 | All others |

**Note:** `screen_categories` appears to be deprecated - only populated on early requests (IDs 1-24), and not used by the current system.

---

## Raw Output (Last 5 vs First 5)

### Recent Requests (Working Correctly)
```
ID: 104, Status: complete, Scope: {'windows': False, 'doors': False, 'patio': True}, Categories: []
ID: 103, Status: complete, Scope: {'windows': True, 'doors': False, 'patio': True}, Categories: []
ID: 102, Status: complete, Scope: {'windows': True, 'doors': False, 'patio': True}, Categories: []
ID: 101, Status: complete, Scope: {'windows': True, 'doors': False, 'patio': True}, Categories: []
ID: 100, Status: complete, Scope: {'windows': True, 'doors': False, 'patio': True}, Categories: []
```

### Oldest Requests (Pre-Scope)
```
ID: 1, Status: complete, Scope: {}, Categories: ['Window', 'Door']
ID: 2, Status: failed, Scope: {}, Categories: []
ID: 3, Status: processing, Scope: {}, Categories: ['Window', 'Door', 'Patio']
ID: 4, Status: failed, Scope: {}, Categories: []
ID: 5, Status: failed, Scope: {}, Categories: []
```

### Transition Point (ID 36)
```
ID: 35, Status: complete, Scope: {}, Categories: []
ID: 36, Status: complete, Scope: {'windows': False, 'doors': False, 'patio': True}, Categories: []
```

---

## Conclusions

1. **Scope system is working correctly** - All requests from ID 36+ have properly populated scope
2. **Empty scope on IDs 1-35** is expected - These were created before the scope feature was implemented
3. **`screen_categories` is deprecated** - Only used in early development, replaced by `scope`
4. **No code fix needed** - The system is functioning as designed

---

## Observations

### Interesting Patterns
- `doors: True` only appears once (ID 93) - Door security screens rarely requested
- Most common pattern: `{windows: True, patio: True}` - Users want both
- `patio: True` without windows (IDs 36-42, etc.) - Patio-only requests exist

### Stuck Requests
- ID 3: Status `processing` with empty scope (old request, likely orphaned)
- ID 52: Status `processing` with valid scope
- ID 59: Status `processing` with valid scope

---

## Recommendations

1. **No bug fix needed** - Close this investigation
2. **Consider data cleanup** - Could migrate old empty `scope` records using `screen_categories` data
3. **Consider removing `screen_categories`** - It's deprecated, clutters the model
4. **Investigate stuck `processing` requests** - IDs 3, 52, 59 may need cleanup

---

## Deep Dive Investigation

### Q1: What is `screen_categories` vs `scope`? Which is source of truth?

**Answer:** They serve different purposes, but there IS redundancy that could cause confusion.

| Field | Purpose | Used By | Format |
|-------|---------|---------|--------|
| `screen_categories` | Legacy: derive `screen_type` string | `ai_enhanced_processor.py:88-97` | `['Window', 'Door', 'Patio']` |
| `scope` | Current: control pipeline steps | `gemini_provider.py`, `services.py` | `{windows: bool, doors: bool, patio: bool}` |

**Code Evidence:**

```python
# ai_enhanced_processor.py:88-97 - screen_categories → screen_type
if visualization_request.screen_categories:
    categories = [c.lower() for c in visualization_request.screen_categories]
    if 'patio' in categories:
        screen_type = 'patio_enclosure'
    elif 'door' in categories:
        screen_type = 'door_single'
    else:
        screen_type = 'window_fixed'

# ai_enhanced_processor.py:127-128 - scope passed separately
if hasattr(visualization_request, 'scope') and visualization_request.scope:
    style_preferences["scope"] = visualization_request.scope
```

**Source of Truth:** `scope` is the source of truth for the pipeline. `screen_categories` is legacy dead code that only affects the `screen_type` variable name (not behavior).

---

### Q2: Is there a legacy fallback masking a bug?

**Answer:** YES! There is a fallback in `gemini_provider.py:101-113` that could mask issues.

```python
# gemini_provider.py:101-113
scope = style_preferences.get('scope', {})
if not scope:
    # Infer from screen_type (legacy support)
    scope = {
        'windows': 'window' in screen_type.lower(),
        'doors': 'door' in screen_type.lower(),
        'patio': 'patio' in screen_type.lower()
    }
    # If nothing matched, default to windows
    if not any(scope.values()):
        scope['windows'] = True
```

**Risk:** If frontend sends `screen_categories` but NOT `scope`:
1. `ai_enhanced_processor.py` derives `screen_type = 'patio_enclosure'`
2. `gemini_provider.py` gets empty `scope` from `style_preferences`
3. Fallback kicks in: infers `scope = {patio: True}` from `screen_type` string
4. **System appears to work, but via fallback, not direct scope**

**Current Status:** This fallback is NOT being triggered for recent requests (IDs 36+) because scope IS being sent correctly. But it could mask bugs if something changes.

---

### Q3: Where does cleanup run - before or after scope check?

**Answer:** Cleanup runs UNCONDITIONALLY - no scope check.

```python
# services.py:66-71
if step_type == 'cleanup':
    cleanup_prompt = prompts.get_cleanup_prompt()  # No scope passed!
    clean_image = self._call_gemini_edit(original_image, cleanup_prompt)
    current_image = clean_image
    logger.info(f"Pipeline Step: {step_name} complete.")
```

**Implication:** If cleanup is changing weather/sky, that's a **PROMPT issue**, not a scope issue. These are separate bugs:
- Bug A: Scope not being used correctly → affects which features get screens
- Bug B: Cleanup prompt changing weather → prompt needs refinement

**Cleanup Prompt (boss/prompts.py):**
```python
def get_cleanup_prompt():
    return "Identify and remove temporary clutter: garbage cans, hoses, toys,
            and loose leaves. Preserve all structural elements: columns, fans,
            lights, furniture, and concrete pads. Maintain the original
            background pixels exactly."
```

The prompt says "Maintain the original background pixels exactly" but Gemini may still alter sky/weather. This is a prompt engineering issue.

---

### Q4: Do you have existing database records with `hasPatio` format?

**Answer:** NO. All database records use lowercase format.

```python
# Database check
ID 104: keys = ['windows', 'doors', 'patio']
ID 93: scope = {'windows': False, 'doors': True, 'patio': False}
ID 50: scope = {'windows': False, 'doors': False, 'patio': True}
ID 36: scope = {'windows': False, 'doors': False, 'patio': True}
```

**Format Transformation:**

| Location | Format | Example |
|----------|--------|---------|
| Frontend Store (Zustand) | camelCase | `{hasPatio: true, hasWindows: false}` |
| Frontend Submit (UploadPage.js) | lowercase | `{patio: true, windows: false}` |
| Backend Model | lowercase | `{patio: true, windows: false}` |
| Pipeline | lowercase | `scope.get('patio', False)` |

**Code Evidence (UploadPage.js:34-39):**
```javascript
const scopePayload = {
  windows: scope.hasWindows,  // Transform here
  doors: scope.hasDoors,
  patio: scope.hasPatio
};
data.append('scope', JSON.stringify(scopePayload));
```

**No dual-format handling needed** - transformation happens at submit time.

---

### Q5: What's the actual frontend component sending this?

**Answer:** `Step2Scope.js` collects, `UploadPage.js` transforms and sends.

**Data Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Step2Scope.js - User Selection                                 │
│  └── setScope('hasPatio', true)                                 │
│  └── setScope('hasWindows', true)                               │
│  └── setScope('hasDoors', false)                                │
│  └── setScope('doorType', 'security_door')                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  visualizationStore.js (Zustand)                                │
│  scope: {                                                       │
│    hasPatio: true,      ← camelCase                             │
│    hasWindows: true,                                            │
│    hasDoors: false,                                             │
│    doorType: null                                               │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  UploadPage.js:34-39 - Transform on Submit                      │
│  const scopePayload = {                                         │
│    windows: scope.hasWindows,   ← Transform to lowercase        │
│    doors: scope.hasDoors,                                       │
│    patio: scope.hasPatio                                        │
│  };                                                             │
│  data.append('scope', JSON.stringify(scopePayload));            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend Serializer (serializers.py:261,267)                    │
│  fields = [..., 'scope']                                        │
│  extra_kwargs = {'scope': {'required': False}}                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Model (models.py:249-253)                                      │
│  scope = models.JSONField(default=dict, blank=True)             │
│  # Stored as: {"windows": true, "doors": false, "patio": true}  │
└─────────────────────────────────────────────────────────────────┘
```

**Frontend/Backend Agreement:** YES, they agree. Frontend transforms camelCase → lowercase before sending.

---

## Potential Hidden Issues

### Issue 1: `doorType` is lost
Frontend collects `doorType` (security_door, french_door, sliding_door) but it's NOT included in `scopePayload`:

```javascript
// UploadPage.js - doorType NOT sent!
const scopePayload = {
  windows: scope.hasWindows,
  doors: scope.hasDoors,
  patio: scope.hasPatio
  // doorType: scope.doorType  ← MISSING
};
```

**Impact:** Door type selection is captured in UI but never sent to backend.

### Issue 2: Fallback could activate unexpectedly
If scope transmission fails for any reason, the `gemini_provider.py` fallback would activate and infer from `screen_type`. This could produce unexpected results.

### Issue 3: `screen_categories` is dead code
It's still in serializers, model, and some processors but serves no purpose in current pipeline. Should be removed to prevent confusion.

---

## Revised Recommendations

1. **No immediate bug fix needed** for scope - it's working
2. **Add `doorType` to scopePayload** in UploadPage.js
3. **Remove `screen_categories`** from model/serializers (migration)
4. **Consider removing fallback** in gemini_provider.py or add logging
5. **Refine cleanup prompt** if weather changes are occurring
6. **Clean up stuck processing requests** (IDs 3, 52, 59)

---

## Next Steps

- [ ] Decide if historical data cleanup is needed
- [ ] Consider migration to populate old `scope` from `screen_categories`
- [ ] Consider removing deprecated fields from model
- [ ] Add `doorType` to scope payload in frontend
- [ ] Investigate cleanup prompt if weather is being changed
- [ ] Add logging to fallback in gemini_provider.py
