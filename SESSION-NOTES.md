# Session Notes

## Latest Session
**Date:** 2025-12-01
**Branch:** fix/scope-mismatch-20251201-0956 (created from feature/ui-testing)
**Duration:** Ongoing

### What We Did
- Created comprehensive TENANT-ARCHITECTURE.md documentation (~700 lines)
  - Documented tenant configuration system (BaseTenantConfig, BossTenantConfig)
  - Documented scope system flow: frontend → backend → AI pipeline
  - Documented AI prompts system (cleanup, insertion, quality check)
  - Added live database example output
  - Mapped pipeline steps to scope keys
  - Listed all related files
- Updated CLAUDE.md with "During Session" logging requirements
- Investigated scope mismatch concern:
  - Created safety branch `fix/scope-mismatch-20251201-0956`
  - Ran diagnostic on all 104 VisualizationRequests
  - **Finding: NOT A BUG** - Empty `scope: {}` is historical data (IDs 1-35)
  - Scope system working correctly since ID 36+
  - Created DIAGNOSTIC-SCOPE-MISMATCH.md with full report
- Deep dive investigation (5 questions):
  - Q1: `screen_categories` vs `scope` - scope is source of truth, categories is dead code
  - Q2: Legacy fallback exists in gemini_provider.py:101-113 (could mask bugs)
  - Q3: Cleanup runs UNCONDITIONALLY - weather issues are prompt bugs, not scope
  - Q4: No `hasPatio` format in DB - all lowercase, transform happens in UploadPage.js
  - Q5: Step2Scope.js → Zustand → UploadPage.js (transforms) → Backend
- Discovered hidden issues:
  - `doorType` is collected but NOT sent to backend (missing from scopePayload)
  - `screen_categories` is dead code cluttering the model
- Weather change investigation (DIAGNOSTIC-WEATHER-CHANGE.md):
  - Analyzed 14 pipeline debug images across multiple sequences
  - **Finding: PATIO step causes weather change, not cleanup**
  - Brick house: overcast → blue sky at patio step
  - Modern house: weather preserved throughout (image-dependent)
  - Windows-only: weather always preserved
  - Root cause: Patio prompt lacks sky preservation instruction
  - Quality check doesn't validate weather preservation
- **Comprehensive visual analysis (ANALYSIS-WEATHER-VISUAL.md):**
  - Reviewed ~25 sequences from 307 total pipeline images
  - **Finding: Weather change is STOCHASTIC, not deterministic**
  - Same image can produce different weather across runs (~50% change rate)
  - Brick house: ~60% of runs change weather
  - Modern house: 0% of runs change weather
  - **RECOMMENDATION: GO WITH DISCLAIMER** instead of fixing
- **Implemented AI disclaimer in UI:**
  - Added to `ResultDetailPage.js` below image comparison
  - Text: "AI-enhanced visualization. Lighting and weather conditions may vary from actual appearance."
  - Styled with `.ai-disclaimer` class (italic, centered, subtle gray)
- **Pipeline reorder + prompt updates:**
  - Changed pipeline order: cleanup → doors → windows → patio → quality_check
  - Reason: Patio is largest envelope, must see doors/windows already installed
  - Updated cleanup prompt to explicitly make weather sunny
  - Reverted insertion prompts to original (complex) version
  - Synced both `api/tenants/boss/prompts.py` and `api/visualizer/prompts.py`
- **RESTORED THINKING MODE (likely root cause of all issues!):**
  - Found that commit `4ccfea9` (Nov 28) removed thinking mode
  - Original: `ThinkingConfig(include_thoughts=True)` + `response_modalities: ["TEXT", "IMAGE"]`
  - After revert: `pass` (no thinking at all)
  - **This explains weather changes, inconsistent results, ignored instructions**
  - Restored original config with `include_thoughts=True`
  - Added thinking log output to `media/thinking_logs/` for debugging
  - Each step logs: timestamp, prompt, and Gemini's reasoning

### What's Working
- Tenant registry system auto-registers Boss tenant
- Scope flows from frontend wizard through to AI pipeline
- Quality check prompts adapt based on scope flags
- **Scope IS being saved correctly** on all recent requests (ID 36+)

### What's Broken / Blocked
- `screen-visualizer` branch referenced in TODO.md doesn't exist
- 3 requests stuck in `processing` status (IDs 3, 52, 59)
- `screen_categories` field is deprecated but still in model
- **`doorType` not being sent to backend** - UI collects but UploadPage.js doesn't include it
- Legacy fallback in gemini_provider.py could mask scope bugs
- ~~PATIO prompt changes weather~~ → **ACCEPTABLE** (use disclaimer instead)

### Next Session Should
- ~~Add disclaimer to results UI~~ ✓ DONE
- ~~Pipeline reorder + sunny prompts~~ ✓ DONE
- **Organize reference images** - Move from `_raw/` to feature folders
- **Implement reference image loading** - Add to services.py
- **Fix `doorType` transmission** - Add to scopePayload in UploadPage.js
- Remove `screen_categories` from model/serializers (migration)
- Add logging to fallback in gemini_provider.py to detect when it activates
- Investigate stuck `processing` requests (3, 52, 59)

---

## Previous Sessions

### 2025-11-30
- Cleaned up git branches
- Deleted dev repo
- Created feature branches from master
