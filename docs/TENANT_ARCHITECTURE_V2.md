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
