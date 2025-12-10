# White-Label Documentation & Testing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete documentation and test coverage for the new hybrid tenant architecture (YAML + DB + Python).

**Architecture:** The system uses YAML files as source of truth, DB as cache/override layer, Python services for pipeline execution and prompt resolution, and React DynamicForm for schema-driven UI.

**Tech Stack:** Django 5.2, Python 3.x, pytest, React 19.1

---

## Task 1: Create V2 Architecture Documentation

**Files:**
- Create: `docs/TENANT_ARCHITECTURE_V2.md`

**Step 1: Create the V2 architecture document**

```markdown
# Tenant Architecture V2 (Hybrid System)

**Status:** Active Implementation
**Last Updated:** 2025-12-10

## Overview

The V2 Architecture moves from a code-heavy inheritance model to a **Configuration-Driven Hybrid System**. This allows new white-label verticals (e.g., Pools, Landscaping) to be spun up by adding a YAML config file, while retaining Python for complex logic.

## Core Design Principles

1. **YAML as Source of Truth:** Tenant configuration lives in version-controlled YAML files (`api/tenants/{tenant}/config.yaml`).
2. **Database as Cache & Override:** DB caches YAML config and allows runtime overrides (like AI Prompts) without code deploys.
3. **Generic Frontend:** `DynamicForm.js` renders inputs based entirely on JSON schema, knowing nothing about "screens" or "pools".
4. **Pipeline Registry:** Central registry maps step names to Python handler functions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONFIGURATION LAYER                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ YAML Config (api/tenants/{tenant}/config.yaml)             │ │
│  │ - tenant_id, display_name                                  │ │
│  │ - product_categories (schema for DynamicForm)              │ │
│  │ - pipeline_steps, step_configs                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          │                                       │
│                          ▼ sync_tenant_config                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Database Cache (TenantConfig model)                        │ │
│  │ - Cached YAML data for fast access                         │ │
│  │ - PromptOverride for runtime prompt edits                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │ Pipeline Registry       │  │ Prompt Service               │  │
│  │ - cleanup_handler       │  │ - get_prompt()               │  │
│  │ - insertion_handler     │  │ - DB override → Code default │  │
│  │ - quality_check_handler │  │ - create/rollback overrides  │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DynamicForm.js                                             │ │
│  │ - Renders from product_categories JSON schema              │ │
│  │ - Domain-agnostic (no hardcoded product references)        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ useTenantConfig.js                                         │ │
│  │ - Fetches /api/config/ on mount                            │ │
│  │ - Caches in sessionStorage                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. YAML Configuration (`api/tenants/{tenant}/config.yaml`)

```yaml
tenant_id: boss
display_name: Boss Security Screens

product_categories:
  - key: mesh_type
    label: Mesh Type
    type: select
    options:
      - value: 10x10
        label: "10x10"
      - value: 12x12
        label: "12x12"
  - key: frame_color
    label: Frame Color
    type: select
    options:
      - value: black
        label: Black
      - value: bronze
        label: Dark Bronze

pipeline_steps:
  - cleanup
  - doors
  - windows
  - patio
  - quality_check

step_configs:
  cleanup:
    type: cleanup
    progress_weight: 10
  doors:
    type: insertion
    feature_name: entry doors
    scope_key: doors
    progress_weight: 25
```

### 2. Pipeline Registry (`api/services/pipeline_registry.py`)

Maps step types to Python handlers:

```python
STEP_HANDLERS = {
    'cleanup': cleanup_handler,
    'insertion': insertion_handler,
    'quality_check': quality_check_handler,
}

# Usage
result = execute_step('cleanup', step_config, context)
```

### 3. Prompt Service (`api/services/prompt_service.py`)

Resolves prompts with DB override priority:

```python
# Priority: 1. Active DB override → 2. Code default
prompt = get_prompt('cleanup', tenant_id='boss')

# Create override (versioned)
create_prompt_override('boss', 'cleanup', 'New prompt text...')

# Rollback to previous version
rollback_prompt_override('boss', 'cleanup')
```

### 4. DynamicForm (`frontend/src/components/DynamicForm/`)

Renders forms purely from JSON schema:

```jsx
<DynamicForm
    schema={tenantConfig}  // { product_categories: [...] }
    formData={formState}
    onChange={setFormState}
/>
```

## Management Commands

```bash
# Sync YAML → DB
python3 manage.py sync_tenant_config

# Export DB → YAML
python3 manage.py export_tenant_config
```

## Adding a New Tenant

1. Create `api/tenants/{tenant_id}/config.yaml`
2. Create `api/tenants/{tenant_id}/prompts.py` with prompt functions
3. Register in `api/tenants/__init__.py`
4. Run `python3 manage.py sync_tenant_config`
5. Set `ACTIVE_TENANT={tenant_id}` in environment

## Migration from V1

V1 used Python-class inheritance (`BaseTenantConfig` → `BossTenantConfig`).
V2 uses YAML + Python handlers. The Python classes still work during transition.

**Deprecated files:**
- `docs/investigations/TENANT-ARCHITECTURE.md` (V1 docs)
- `TENANT-SPEC.md` (analysis document, not architecture)

## Related Files

| File | Purpose |
|------|---------|
| `api/tenants/{tenant}/config.yaml` | YAML configuration |
| `api/tenants/{tenant}/prompts.py` | AI prompts |
| `api/services/pipeline_registry.py` | Step handlers |
| `api/services/prompt_service.py` | Prompt resolution |
| `api/management/commands/sync_tenant_config.py` | YAML → DB |
| `api/management/commands/export_tenant_config.py` | DB → YAML |
| `frontend/src/components/DynamicForm/` | Schema-driven forms |
| `frontend/src/hooks/useTenantConfig.js` | Config fetching |
```

**Step 2: Verify the file was created**

Run: `cat docs/TENANT_ARCHITECTURE_V2.md | head -20`
Expected: Shows the header and overview section

**Step 3: Commit**

```bash
git add docs/TENANT_ARCHITECTURE_V2.md
git commit -m "docs: add V2 tenant architecture documentation"
```

---

## Task 2: Update WHITE-LABEL-PLAN.md Status

**Files:**
- Modify: `WHITE-LABEL-PLAN.md`

**Step 1: Update the plan with accurate status**

Replace the entire file with:

```markdown
# White-Label Architecture Plan

## Status: Integration Phase
**Last Updated:** 2025-12-10

---

## Goal
Design a system to make verticals (boss-security-visualizer, pools-visualizer, etc.) easily copyable with client-configurable reference images and product names (white-label SaaS approach).

---

## Implementation Status

### Phase 0: Frontend Proof - COMPLETE
- [x] `DynamicForm.js` component created
- [x] Renders forms from `product_categories` JSON schema
- [x] Domain-agnostic (no hardcoded product references)

### Phase 1: YAML Config System - COMPLETE
- [x] YAML config format defined (`api/tenants/{tenant}/config.yaml`)
- [x] `sync_tenant_config` management command
- [x] `export_tenant_config` management command
- [x] Boss tenant YAML config created
- [x] Pools tenant YAML config created

### Phase 2: Prompt Override System - COMPLETE
- [x] `PromptOverride` model with version history
- [x] `prompt_service.py` - DB override → Code default priority
- [x] Rollback capability

### Phase 3: Pipeline Step Registry - COMPLETE
- [x] `pipeline_registry.py` - Step type → handler mapping
- [x] Handlers: cleanup, insertion, quality_check
- [x] Scope-based step skipping

### Phase 4: Reference Image System - PENDING
- [ ] `ReferenceImage` model with tenant FK
- [ ] Upload endpoint with processing
- [ ] Frontend gallery
- [ ] AI pipeline integration

---

## Remaining Work

### Testing (Priority: High)
- [ ] Tests for `pipeline_registry.py`
- [ ] Tests for `prompt_service.py`
- [ ] Integration test: YAML → API → DynamicForm

### API Integration (Priority: High)
- [ ] Verify `/api/config/` returns `product_categories` schema
- [ ] Update `useTenantConfig.js` if needed

### Documentation (Priority: Medium)
- [x] `docs/TENANT_ARCHITECTURE_V2.md` - New architecture docs
- [ ] Deprecation notices on old docs

### Tech Debt (Priority: Low)
- `frontend/src/store/visualizationStore.js` - screen refs
- `api/ai_services/utils/prompt_utils.py` - screen refs
- `frontend/src/components/Upload/MeshSelector.js` - should rename

---

## Architecture Decision: Hybrid Config Pattern

- **YAML files in Git** = Source of Truth
- **DB** = Read-only cache (except reference images)
- **Only reference images** are client-mutable in DB
- **Prompts** use "override" pattern: code default + optional DB override

See `docs/TENANT_ARCHITECTURE_V2.md` for full architecture documentation.
```

**Step 2: Verify the update**

Run: `head -30 WHITE-LABEL-PLAN.md`
Expected: Shows "Status: Integration Phase" and completed checkboxes

**Step 3: Commit**

```bash
git add WHITE-LABEL-PLAN.md
git commit -m "docs: update WHITE-LABEL-PLAN status to reflect implementation"
```

---

## Task 3: Add Deprecation Notices to Old Docs

**Files:**
- Modify: `docs/investigations/TENANT-ARCHITECTURE.md` (add header)
- Modify: `TENANT-SPEC.md` (add header)

**Step 1: Add deprecation notice to V1 architecture doc**

Add this block at the very top of `docs/investigations/TENANT-ARCHITECTURE.md`:

```markdown
> **DEPRECATED:** This document describes the legacy V1 architecture (Python-class inheritance).
> Please refer to `docs/TENANT_ARCHITECTURE_V2.md` for the active Hybrid Architecture.

---

```

**Step 2: Add deprecation notice to TENANT-SPEC.md**

Add this block at the very top of `TENANT-SPEC.md`:

```markdown
> **DEPRECATED:** This document was an analysis/spec written during planning.
> Please refer to `docs/TENANT_ARCHITECTURE_V2.md` for the active Hybrid Architecture.

---

```

**Step 3: Verify both files have notices**

Run: `head -5 docs/investigations/TENANT-ARCHITECTURE.md && head -5 TENANT-SPEC.md`
Expected: Both show "DEPRECATED" notice

**Step 4: Commit**

```bash
git add docs/investigations/TENANT-ARCHITECTURE.md TENANT-SPEC.md
git commit -m "docs: add deprecation notices to V1 architecture docs"
```

---

## Task 4: Write Tests for Pipeline Registry

**Files:**
- Create: `api/tests/test_pipeline_registry.py`

**Step 1: Write the test file**

```python
"""
Tests for api/services/pipeline_registry.py
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from PIL import Image

from api.services.pipeline_registry import (
    cleanup_handler,
    insertion_handler,
    quality_check_handler,
    get_handler,
    register_handler,
    execute_step,
    STEP_HANDLERS,
)


class TestGetHandler:
    """Tests for get_handler function."""

    def test_get_cleanup_handler(self):
        """Should return cleanup_handler for 'cleanup' type."""
        handler = get_handler('cleanup')
        assert handler == cleanup_handler

    def test_get_insertion_handler(self):
        """Should return insertion_handler for 'insertion' type."""
        handler = get_handler('insertion')
        assert handler == insertion_handler

    def test_get_quality_check_handler(self):
        """Should return quality_check_handler for 'quality_check' type."""
        handler = get_handler('quality_check')
        assert handler == quality_check_handler

    def test_get_unknown_handler_returns_none(self):
        """Should return None for unknown step type."""
        handler = get_handler('unknown_step_type')
        assert handler is None


class TestRegisterHandler:
    """Tests for register_handler function."""

    def test_register_custom_handler(self):
        """Should register a custom handler."""
        def custom_handler(step_name, step_config, context):
            return {'custom': True}

        register_handler('custom_type', custom_handler)

        assert get_handler('custom_type') == custom_handler

        # Cleanup
        del STEP_HANDLERS['custom_type']


class TestExecuteStep:
    """Tests for execute_step function."""

    def test_execute_step_missing_type_raises(self):
        """Should raise ValueError if step config missing 'type'."""
        with pytest.raises(ValueError, match="missing 'type'"):
            execute_step('test_step', {}, {})

    def test_execute_step_unknown_type_raises(self):
        """Should raise ValueError if no handler for step type."""
        with pytest.raises(ValueError, match="No handler registered"):
            execute_step('test_step', {'type': 'nonexistent'}, {})


class TestCleanupHandler:
    """Tests for cleanup_handler."""

    def test_cleanup_handler_calls_gemini_edit(self):
        """Should call _call_gemini_edit with cleanup prompt."""
        mock_visualizer = Mock()
        mock_image = Mock(spec=Image.Image)
        mock_clean_image = Mock(spec=Image.Image)
        mock_visualizer._call_gemini_edit.return_value = mock_clean_image

        mock_prompts = Mock()
        mock_prompts.get_cleanup_prompt.return_value = "Clean the image"

        context = {
            'visualizer': mock_visualizer,
            'image': mock_image,
            'prompts': mock_prompts,
        }

        result = cleanup_handler('cleanup', {'type': 'cleanup'}, context)

        mock_prompts.get_cleanup_prompt.assert_called_once()
        mock_visualizer._call_gemini_edit.assert_called_once_with(
            mock_image, "Clean the image", step_name='cleanup'
        )
        assert result['image'] == mock_clean_image
        assert result['clean_image'] == mock_clean_image


class TestInsertionHandler:
    """Tests for insertion_handler."""

    def test_insertion_skips_when_scope_disabled(self):
        """Should skip and return unchanged image when scope not enabled."""
        mock_image = Mock(spec=Image.Image)

        context = {
            'visualizer': Mock(),
            'image': mock_image,
            'prompts': Mock(),
            'scope': {'doors': False},
            'options': {},
        }
        step_config = {
            'type': 'insertion',
            'scope_key': 'doors',
            'feature_name': 'entry doors',
        }

        result = insertion_handler('doors', step_config, context)

        assert result['image'] == mock_image
        context['visualizer']._call_gemini_edit.assert_not_called()

    def test_insertion_executes_when_scope_enabled(self):
        """Should execute insertion when scope is enabled."""
        mock_visualizer = Mock()
        mock_image = Mock(spec=Image.Image)
        mock_result_image = Mock(spec=Image.Image)
        mock_visualizer._call_gemini_edit.return_value = mock_result_image

        mock_prompts = Mock()
        mock_prompts.get_screen_insertion_prompt.return_value = "Install screens"

        context = {
            'visualizer': mock_visualizer,
            'image': mock_image,
            'prompts': mock_prompts,
            'scope': {'doors': True},
            'options': {'color': 'Black'},
        }
        step_config = {
            'type': 'insertion',
            'scope_key': 'doors',
            'feature_name': 'entry doors',
        }

        result = insertion_handler('doors', step_config, context)

        mock_prompts.get_screen_insertion_prompt.assert_called_once_with(
            'entry doors', {'color': 'Black'}
        )
        assert result['image'] == mock_result_image


class TestQualityCheckHandler:
    """Tests for quality_check_handler."""

    def test_quality_check_returns_score_and_reason(self):
        """Should return score and reason from Gemini JSON response."""
        mock_visualizer = Mock()
        mock_visualizer._call_gemini_json.return_value = {
            'score': 0.95,
            'reason': 'Quality looks good'
        }

        mock_prompts = Mock()
        mock_prompts.get_quality_check_prompt.return_value = "Check quality"

        mock_clean = Mock(spec=Image.Image)
        mock_final = Mock(spec=Image.Image)

        context = {
            'visualizer': mock_visualizer,
            'clean_image': mock_clean,
            'image': mock_final,
            'prompts': mock_prompts,
            'scope': {'doors': True},
        }

        result = quality_check_handler('quality_check', {}, context)

        assert result['score'] == 0.95
        assert result['reason'] == 'Quality looks good'
        mock_visualizer._call_gemini_json.assert_called_once()
```

**Step 2: Run tests to verify they pass**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tests/test_pipeline_registry.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add api/tests/test_pipeline_registry.py
git commit -m "test: add tests for pipeline_registry service"
```

---

## Task 5: Write Tests for Prompt Service

**Files:**
- Create: `api/tests/test_prompt_service.py`

**Step 1: Write the test file**

```python
"""
Tests for api/services/prompt_service.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase

from api.services.prompt_service import (
    get_prompt,
    create_prompt_override,
    rollback_prompt_override,
)
from api.models import PromptOverride


class TestGetPrompt(TestCase):
    """Tests for get_prompt function."""

    @patch('api.services.prompt_service.get_tenant_config')
    @patch('api.services.prompt_service.PromptOverride.objects')
    def test_get_prompt_uses_db_override_when_exists(self, mock_override_objects, mock_get_config):
        """Should use DB override when one exists."""
        mock_config = Mock()
        mock_config.tenant_id = 'boss'
        mock_get_config.return_value = mock_config

        mock_override = Mock()
        mock_override.prompt_text = "Override prompt text"
        mock_override.version = 1
        mock_override_objects.filter.return_value.order_by.return_value.first.return_value = mock_override

        result = get_prompt('cleanup', tenant_id='boss')

        assert result == "Override prompt text"

    @patch('api.services.prompt_service.get_tenant_config')
    @patch('api.services.prompt_service.PromptOverride.objects')
    def test_get_prompt_falls_back_to_code_default(self, mock_override_objects, mock_get_config):
        """Should fall back to code default when no DB override."""
        mock_prompts = Mock()
        mock_prompts.get_cleanup_prompt.return_value = "Code default prompt"

        mock_config = Mock()
        mock_config.tenant_id = 'boss'
        mock_config.get_prompts_module.return_value = mock_prompts
        mock_config.get_step_config.return_value = {'type': 'cleanup'}
        mock_get_config.return_value = mock_config

        # No DB override
        mock_override_objects.filter.return_value.order_by.return_value.first.return_value = None

        result = get_prompt('cleanup', tenant_id='boss')

        assert result == "Code default prompt"
        mock_prompts.get_cleanup_prompt.assert_called_once()

    @patch('api.services.prompt_service.get_tenant_config')
    @patch('api.services.prompt_service.PromptOverride.objects')
    def test_get_prompt_insertion_type(self, mock_override_objects, mock_get_config):
        """Should call get_screen_insertion_prompt for insertion type."""
        mock_prompts = Mock()
        mock_prompts.get_screen_insertion_prompt.return_value = "Install screens on doors"

        mock_config = Mock()
        mock_config.tenant_id = 'boss'
        mock_config.get_prompts_module.return_value = mock_prompts
        mock_config.get_step_config.return_value = {
            'type': 'insertion',
            'feature_name': 'entry doors'
        }
        mock_get_config.return_value = mock_config

        # No DB override
        mock_override_objects.filter.return_value.order_by.return_value.first.return_value = None

        result = get_prompt('doors', tenant_id='boss', color='Black')

        mock_prompts.get_screen_insertion_prompt.assert_called_once()
        assert result == "Install screens on doors"


class TestCreatePromptOverride(TestCase):
    """Tests for create_prompt_override function."""

    def test_create_first_override(self):
        """Should create version 1 override when none exist."""
        # Clean up any existing overrides
        PromptOverride.objects.filter(tenant_id='test', step_name='cleanup').delete()

        override = create_prompt_override(
            tenant_id='test',
            step_name='cleanup',
            prompt_text='Test prompt'
        )

        assert override.version == 1
        assert override.is_active is True
        assert override.prompt_text == 'Test prompt'

        # Cleanup
        override.delete()

    def test_create_increments_version(self):
        """Should increment version number for new overrides."""
        # Clean up and create v1
        PromptOverride.objects.filter(tenant_id='test', step_name='cleanup').delete()

        v1 = create_prompt_override('test', 'cleanup', 'Version 1')
        v2 = create_prompt_override('test', 'cleanup', 'Version 2')

        assert v2.version == 2
        assert v2.is_active is True

        # Previous version should be deactivated
        v1.refresh_from_db()
        assert v1.is_active is False

        # Cleanup
        v1.delete()
        v2.delete()


class TestRollbackPromptOverride(TestCase):
    """Tests for rollback_prompt_override function."""

    def test_rollback_returns_none_when_no_previous(self):
        """Should return None when no previous version to rollback to."""
        PromptOverride.objects.filter(tenant_id='test', step_name='rollback_test').delete()

        create_prompt_override('test', 'rollback_test', 'Only version')

        result = rollback_prompt_override('test', 'rollback_test')

        assert result is None

        # Cleanup
        PromptOverride.objects.filter(tenant_id='test', step_name='rollback_test').delete()

    def test_rollback_activates_previous_version(self):
        """Should deactivate current and activate previous version."""
        PromptOverride.objects.filter(tenant_id='test', step_name='rollback_test').delete()

        v1 = create_prompt_override('test', 'rollback_test', 'Version 1')
        v2 = create_prompt_override('test', 'rollback_test', 'Version 2')

        result = rollback_prompt_override('test', 'rollback_test')

        v1.refresh_from_db()
        v2.refresh_from_db()

        assert result == v1
        assert v1.is_active is True
        assert v2.is_active is False

        # Cleanup
        v1.delete()
        v2.delete()
```

**Step 2: Run tests to verify they pass**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tests/test_prompt_service.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add api/tests/test_prompt_service.py
git commit -m "test: add tests for prompt_service"
```

---

## Task 6: Verify API Returns New Schema Format

**Files:**
- Read: `api/views_config.py`

**Step 1: Check current API response format**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 manage.py shell -c "from api.tenants import get_tenant_config; c = get_tenant_config(); print(hasattr(c, 'get_product_schema'))"`

Expected: `True` if new schema method exists, `False` if still legacy

**Step 2: If False, check what TenantConfigView returns**

Run: `cat api/views_config.py`

Evaluate: Does it return `product_categories` array or legacy `mesh_choices`/`frame_color_choices`?

**Step 3: Document finding**

If API needs updating, create a follow-up task. If API is correct, verify with curl:

Run: `curl http://localhost:8000/api/config/ 2>/dev/null | python3 -m json.tool | head -30`

---

## Task 7: Run All Tests and Verify

**Step 1: Run full test suite**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tests/ -v --tb=short`

Expected: All tests pass

**Step 2: Check test coverage for new services**

Run: `python3 -m pytest api/tests/test_pipeline_registry.py api/tests/test_prompt_service.py -v --tb=short`

Expected: All new tests pass

**Step 3: Final commit if any changes**

```bash
git status
# If clean, done. If changes, review and commit.
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Create V2 Architecture Documentation | `docs/TENANT_ARCHITECTURE_V2.md` |
| 2 | Update WHITE-LABEL-PLAN.md Status | `WHITE-LABEL-PLAN.md` |
| 3 | Add Deprecation Notices | V1 docs |
| 4 | Write Pipeline Registry Tests | `api/tests/test_pipeline_registry.py` |
| 5 | Write Prompt Service Tests | `api/tests/test_prompt_service.py` |
| 6 | Verify API Schema Format | `api/views_config.py` |
| 7 | Run All Tests | - |

**Total estimated commits:** 5-6
