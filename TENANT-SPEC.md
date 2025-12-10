> **DEPRECATED:** This document was an analysis/spec written during planning.
> Please refer to `docs/TENANT_ARCHITECTURE_V2.md` for the active Hybrid Architecture.

---

# Tenant Specification

## Strategic Questions Answered

### Deployment Model: CLONED REPOS (Dev) → SINGLE DEPLOYMENT (Prod)
- **Development:** Separate folders (`pools-visualizer/`, `boss-security-visualizer/`)
- **Production:** Single codebase with `ACTIVE_TENANT` env var
- Tenant determined at runtime via env var OR subdomain middleware

### Who Buys This?
- Direct clients (contractors/dealers who sell products)
- Each tenant = different product vertical, NOT different customers
- Same business model, different physical products

### Data Isolation
- Currently: Separate SQLite databases per dev folder
- Production: Single DB, tenant field on models OR separate deployments

---

## Example Tenant Analysis: pools-visualizer vs boss-security-visualizer

### What DIFFERS (Minimum Viable Tenant Config)

| Category | Boss (Security Screens) | Pools |
|----------|-------------------------|-------|
| **tenant_id** | `boss` | `pools` |
| **display_name** | `Boss Security Screens` | `Swimming Pools` |
| **Product Options** | mesh types, frame colors, mesh colors, opacity | pool shapes, surfaces, deck materials, deck colors, water features, pool extras |
| **Pipeline Steps** | `cleanup → doors → windows → patio → quality_check` | `cleanup → pool_shape → deck → water_features → quality_check` |
| **AI Prompts** | Security screen insertion language | Pool rendering language |
| **Branding** | (not defined in code) | `PRIMARY_COLOR`, `SECONDARY_COLOR`, `LOGO_PATH` |

### What STAYS IDENTICAL (Never Configure)

| Component | Why |
|-----------|-----|
| Auth system (JWT) | Same user flows |
| Core visualizer service (`api/ai_services/`) | AI provider abstraction |
| Image upload handling | Same file processing |
| PDF generation skeleton | Same report structure |
| Frontend component library | Same UI patterns |
| Database schema | Same data model |
| Payment flow (Stripe) | Same checkout |

---

## The Actual Configurable Things

### MUST DIFFER (Required for each tenant)
1. **tenant_id** - Unique identifier (string)
2. **display_name** - Human-readable name
3. **pipeline_steps** - Ordered list of step names
4. **step_configs** - Per-step: type, feature_name, scope_key, progress_weight
5. **prompts** - AI prompts for each step (THE CORE IP)

### PRODUCT-SPECIFIC OPTIONS
- Boss: mesh_choices, frame_color_choices, mesh_color_choices, opacity_choices
- Pools: pool_shapes, pool_surfaces, deck_materials, deck_colors, water_features, pool_extras

**Pattern:** Each tenant has 4-6 "choice" categories, but the category NAMES differ.
Boss calls them "mesh" and "frame colors" because that's their product.
Pools calls them "pool shapes" and "deck materials" because that's their product.

### NICE-TO-HAVE (Branding)
- primary_color
- secondary_color
- logo_path

### NOT CONFIGURABLE (Currently)
- Pricing tiers (hardcoded $1350 mock)
- Feature flags
- UI copy beyond product names
- Workflow variations (wizard steps are hardcoded in React)

---

## Current Architecture Problems Exposed

### 1. BaseTenantConfig is too screen-specific
```python
# base.py has these methods:
get_mesh_choices()
get_frame_color_choices()
get_mesh_color_choices()
get_opacity_choices()
```
Pools has to ABUSE these methods:
```python
def get_mesh_choices(self):
    """For pools: return pool surface choices."""  # WTF
    return POOL_SURFACES
```

**Fix needed:** Generic `get_product_options() -> Dict[str, List[Tuple]]`

### 2. Pipeline step handlers are implicit
`get_step_config()` returns `type: 'insertion'` but the actual handler is determined by string matching in the service layer.

**Fix needed:** Explicit handler registry OR step type enum

### 3. Prompts are Python modules, not data
Prompts live in `.py` files with functions. This works but:
- Can't edit without deploy
- No version history
- Hard to A/B test

**Fix for later:** Prompt override system (code default + optional DB override)

### 4. Frontend wizard is hardcoded
The wizard steps (scope selection, options) are React components, not data-driven.

**Fix needed (Phase 0):** Frontend renders from JSON schema

---

## Minimum Viable Schema (For Phase 0 Frontend Proof)

```json
{
  "tenant_id": "pools",
  "display_name": "Swimming Pools",
  "product_categories": [
    {
      "key": "pool_shape",
      "label": "Pool Shape",
      "type": "select",
      "options": [
        {"value": "rectangle", "label": "Rectangle"},
        {"value": "freeform", "label": "Freeform"}
      ]
    },
    {
      "key": "pool_surface",
      "label": "Pool Surface",
      "type": "select",
      "options": [
        {"value": "plaster", "label": "White Plaster"},
        {"value": "pebble_blue", "label": "Pebble Tec - Blue"}
      ]
    }
  ],
  "pipeline_steps": ["cleanup", "pool_shape", "deck", "water_features", "quality_check"],
  "branding": {
    "primary_color": "#0077b6",
    "secondary_color": "#00b4d8"
  }
}
```

**Test:** Adding a new option to `product_categories` should appear in UI without code changes.

---

## Who Configures It?

**Current:** Developer edits Python files, deploys
**Goal:** Developer edits YAML, runs management command
**Stretch:** Admin UI for non-technical users (prompts only, not structure)

Reference images are the exception - those should be uploadable by non-technical users.

---

## What This Means for White-Label Planning

### The schema design IS the architecture
Before building DynamicForm.js, we need to:
1. Define the `product_categories` schema format
2. Decide if pipeline steps are also configurable or fixed per tenant
3. Handle the "Boss methods named wrong for Pools" problem

### Phase 0 should prove ONE thing
Can the frontend render product options from JSON without knowing the product domain?

```
Boss schema → UI shows mesh/frame options
Pools schema → UI shows pool shape/surface options
Same React component, different JSON
```

### Background processing can wait
We don't have Celery. Reference image processing can be synchronous for MVP.

---

## Recommended Next Steps

1. **Fix BaseTenantConfig** - Replace screen-specific methods with generic `get_product_options()`
2. **Create schema format** - JSON structure for product categories
3. **Build DynamicForm.js** - Renders from schema
4. **Test with both tenants** - Boss and Pools schemas render correctly
5. **Then** tackle YAML config, prompt overrides, etc.
