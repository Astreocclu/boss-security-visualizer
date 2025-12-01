# Tenant Architecture Documentation

## Overview

Boss Security Visualizer uses a **configuration-based multi-tenancy system** with a shared database. While currently operating as a single-tenant deployment (Boss Security Screens), the architecture is designed for future multi-tenant expansion.

**Strategy:** Single active tenant per deployment, shared database, row-level user isolation.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TENANT CONFIGURATION LAYER               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ BaseTenantConfig (Abstract Interface)                  │ │
│  │ - tenant_id, display_name                              │ │
│  │ - get_mesh_choices(), get_frame_color_choices()        │ │
│  │ - get_pipeline_steps(), get_step_config()              │ │
│  │ - get_prompts_module()                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ▲                                  │
│                          │ implements                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ BossTenantConfig                                       │ │
│  │ - Boss-specific mesh/frame/color choices               │ │
│  │ - Pipeline: cleanup → patio → windows → doors → QC     │ │
│  │ - Boss-specific AI prompts                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    TENANT REGISTRY (Singleton)              │
│  _TENANT_REGISTRY: Dict[tenant_id → config]                 │
│  _active_tenant: Cached global tenant                       │
│  get_tenant_config(): Returns active tenant                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              SETTINGS.ACTIVE_TENANT = "boss"                │
│              (configurable via environment variable)        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER (SHARED)                      │
│  Database: PostgreSQL (single shared DB)                    │
│  Models: User, UserProfile, VisualizationRequest,           │
│          GeneratedImage                                     │
│  Isolation: Row-level via User ownership (ForeignKey)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Tenant Configuration System

### How Tenant Context is Determined

```
Environment Variable: ACTIVE_TENANT (default: 'boss')
         │
         ▼
Django Settings loads ACTIVE_TENANT
         │
         ▼
Tenant Registry auto-registers BossTenantConfig on module load
         │
         ▼
get_tenant_config() returns cached active tenant
         │
         ▼
Views, Services, Models use tenant config for business logic
         │
         ▼
Frontend fetches config via GET /api/config/
```

**Important:** Tenant is determined **globally per deployment**, not per-user or per-request.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTIVE_TENANT` | `boss` | Which tenant configuration to activate |
| `USE_TENANT_REGISTRY` | `true` | Enable/disable tenant registry system |

---

## File Structure

```
api/
├── tenants/
│   ├── __init__.py          # Registry: register_tenant(), get_tenant_config()
│   ├── base.py              # BaseTenantConfig abstract class
│   └── boss/
│       ├── __init__.py
│       ├── config.py        # BossTenantConfig implementation
│       └── prompts.py       # Boss-specific AI prompts
├── models.py                # Uses get_tenant_config() for dynamic choices
├── views_config.py          # TenantConfigView (GET /api/config/)
├── serializers.py           # Uses tenant config for validation
└── visualizer/
    └── services.py          # ExecutionService uses tenant pipeline

frontend/
├── src/
│   ├── hooks/
│   │   └── useTenantConfig.js   # React hook for tenant config
│   └── services/
│       └── api.js               # fetchTenantConfig() function
```

---

## BaseTenantConfig Interface

All tenant configurations must implement this interface:

```python
# api/tenants/base.py

class BaseTenantConfig(ABC):
    @property
    @abstractmethod
    def tenant_id(self) -> str:
        """Unique identifier for the tenant"""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable tenant name"""

    @abstractmethod
    def get_mesh_choices(self) -> list[tuple[str, str]]:
        """Available mesh/screen types"""

    @abstractmethod
    def get_frame_color_choices(self) -> list[tuple[str, str]]:
        """Available frame colors"""

    @abstractmethod
    def get_mesh_color_choices(self) -> list[tuple[str, str]]:
        """Available mesh colors"""

    @abstractmethod
    def get_opacity_choices(self) -> list[tuple[str, str]]:
        """Available opacity levels"""

    @abstractmethod
    def get_pipeline_steps(self) -> list[str]:
        """Ordered list of processing steps"""

    @abstractmethod
    def get_step_config(self, step_name: str) -> dict:
        """Configuration for a specific pipeline step"""

    @abstractmethod
    def get_prompts_module(self):
        """Module containing AI prompt functions"""
```

---

## Boss Tenant Configuration

### Choices

| Category | Options |
|----------|---------|
| **Mesh Types** | 10x10, 12x12, 12x12 American |
| **Frame Colors** | Black, Dark Bronze, Stucco, White, Almond |
| **Mesh Colors** | Black, Stucco, Bronze |
| **Opacity** | 80%, 95%, 99% |

### Processing Pipeline

| Step | Type | Description | Progress Weight |
|------|------|-------------|-----------------|
| `cleanup` | preprocessing | Foundation image cleanup | 10% |
| `patio` | feature | Process patio doors | 25% |
| `windows` | feature | Process windows | 25% |
| `doors` | feature | Process entry doors | 25% |
| `quality_check` | validation | Final quality validation | 15% |

### AI Prompts

Located in `api/tenants/boss/prompts.py`:

- `get_cleanup_prompt()` - Image preprocessing instructions
- `get_screen_insertion_prompt(feature_type, options)` - Feature-specific screen installation
- `get_quality_check_prompt(scope)` - Quality validation per scope

---

## Tenant Registry API

```python
from api.tenants import (
    register_tenant,      # Register a new tenant config
    get_tenant_config,    # Get active tenant config (cached)
    get_tenant_prompts,   # Get tenant's prompts module
    get_all_tenants,      # List all registered tenants
    clear_cache,          # Clear cached active tenant
)

# Usage examples
config = get_tenant_config()
mesh_choices = config.get_mesh_choices()
prompts = get_tenant_prompts()
```

---

## API Endpoint

### GET /api/config/

Returns the active tenant's configuration for frontend consumption.

**Response:**
```json
{
  "tenant_id": "boss",
  "display_name": "Boss Security Screens",
  "mesh_choices": [
    {"value": "10x10", "label": "10x10"},
    {"value": "12x12", "label": "12x12"},
    {"value": "12x12_american", "label": "12x12 American"}
  ],
  "frame_color_choices": [...],
  "mesh_color_choices": [...],
  "opacity_choices": [...],
  "pipeline_steps": ["cleanup", "patio", "windows", "doors", "quality_check"]
}
```

**Permission:** Public (AllowAny)

---

## Frontend Integration

### useTenantConfig Hook

```javascript
// frontend/src/hooks/useTenantConfig.js

import { useTenantConfig } from '../hooks/useTenantConfig';

function MyComponent() {
  const { config, loading, error } = useTenantConfig();

  if (loading) return <Spinner />;

  return (
    <Select options={config.meshChoices} />
  );
}
```

**Features:**
- Fetches from `/api/config/` on mount
- Caches in `sessionStorage` for performance
- Falls back to hardcoded defaults if API unavailable

---

## Data Isolation

### Current Strategy: Row-Level User Ownership

All data models link to Django's `User` model via ForeignKey:

```python
# All queries automatically filter by user
class VisualizationRequestViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return VisualizationRequest.objects.filter(user=self.request.user)
```

**What this means:**
- Users only see their own data
- No cross-user data access possible
- Tenant context doesn't affect data queries (all users share same tenant config)

### Database Schema

```
┌─────────────────┐     ┌──────────────────────┐
│ User            │     │ UserProfile          │
│ (Django built-in)│────│ - user (FK)          │
└─────────────────┘     │ - company_name       │
        │               │ - phone_number       │
        │               └──────────────────────┘
        │
        ▼
┌──────────────────────┐     ┌──────────────────────┐
│ VisualizationRequest │     │ GeneratedImage       │
│ - user (FK)          │────│ - request (FK)       │
│ - image, mesh_type   │     │ - processed_image    │
│ - frame_color, etc.  │     │ - step_name          │
└──────────────────────┘     └──────────────────────┘
```

---

## Adding a New Tenant

1. **Create tenant directory:**
   ```
   api/tenants/newtenant/
   ├── __init__.py
   ├── config.py
   └── prompts.py
   ```

2. **Implement config.py:**
   ```python
   from api.tenants.base import BaseTenantConfig

   class NewTenantConfig(BaseTenantConfig):
       @property
       def tenant_id(self):
           return "newtenant"

       @property
       def display_name(self):
           return "New Tenant Name"

       # ... implement all abstract methods
   ```

3. **Implement prompts.py:**
   ```python
   def get_cleanup_prompt():
       return "..."

   def get_screen_insertion_prompt(feature_type, options):
       return "..."

   def get_quality_check_prompt(scope):
       return "..."
   ```

4. **Register the tenant** in `api/tenants/__init__.py`:
   ```python
   from .newtenant.config import NewTenantConfig
   register_tenant(NewTenantConfig())
   ```

5. **Activate via environment:**
   ```bash
   ACTIVE_TENANT=newtenant python manage.py runserver
   ```

---

## Current Limitations

| Limitation | Description |
|------------|-------------|
| **Single Active Tenant** | Only one tenant per deployment; can't have user A on "boss" and user B on another tenant |
| **No Per-Request Routing** | No subdomain/header/URL path tenant detection |
| **No Tenant-Aware Middleware** | Tenant context is global, not per-request |
| **Restart Required** | Changing `ACTIVE_TENANT` requires application restart |
| **No Admin UI** | Tenants are defined in code, not via admin interface |
| **Shared Database** | No per-tenant database or schema isolation |
| **No Tenant Analytics** | No per-tenant usage metrics or reporting |

---

## Future Multi-Tenancy Expansion

To support true multi-tenancy (multiple tenants in single deployment):

1. **Add tenant middleware** to extract tenant from subdomain/header
2. **Add tenant field** to User or create TenantMembership model
3. **Update queries** to filter by tenant context
4. **Implement tenant switching** without restart
5. **Add admin interface** for tenant management

The current architecture's clean separation of tenant config from business logic makes this expansion straightforward.

---

## Scope System

The **scope** system determines which features (patio, windows, doors) the AI pipeline should process for a given visualization request.

### Live Database Example

```python
# python3 manage.py shell -c "from api.models import VisualizationRequest; r = VisualizationRequest.objects.last(); print(f'ID: {r.id}, Scope: {r.scope}')"

ID: 1
Scope: {}
Screen Categories: ['Window', 'Door']
Mesh Choice: 12x12
Frame Color: Black
```

### Scope Data Structure

**Frontend State** (`visualizationStore.js`):
```javascript
scope: {
  hasPatio: false,      // Enclose covered patio/outdoor area
  hasWindows: true,     // Install screens on windows (default: true)
  hasDoors: false,      // Install security doors
  doorType: null        // 'security_door' | 'french_door' | 'sliding_door'
}
```

**Backend Model** (`VisualizationRequest.scope`):
```python
scope = models.JSONField(
    default=dict,
    blank=True,
    help_text="Sales scope (hasPatio, hasWindows, hasDoors, doorType)"
)
```

**API Payload** (transformed on submit):
```json
{
  "windows": true,
  "doors": false,
  "patio": false
}
```

### Scope Flow: Frontend → Backend → AI

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND: Upload Wizard Step 2 (Step2Scope.js)                 │
│                                                                 │
│  User answers Yes/No questions:                                 │
│  1. "Do you have a covered patio?" → hasPatio                   │
│  2. "Security screens on windows?" → hasWindows                 │
│  3. "Do you need security doors?"  → hasDoors                   │
│  4. (If doors) "What type?"        → doorType                   │
│                                                                 │
│  Stored in Zustand: useVisualizationStore().scope               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND: Form Submission (UploadPage.js)                      │
│                                                                 │
│  const scopePayload = {                                         │
│    windows: scope.hasWindows,                                   │
│    doors: scope.hasDoors,                                       │
│    patio: scope.hasPatio                                        │
│  };                                                             │
│  data.append('scope', JSON.stringify(scopePayload));            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND: VisualizationRequest Model (api/models.py)            │
│                                                                 │
│  scope = JSONField(default=dict)                                │
│  # Stored as: {"windows": true, "doors": false, "patio": true}  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND: ScreenVisualizer.process_pipeline()                   │
│  (api/visualizer/services.py)                                   │
│                                                                 │
│  for step_name in tenant_config.get_pipeline_steps():           │
│      step_config = tenant_config.get_step_config(step_name)     │
│                                                                 │
│      if step_config['type'] == 'insertion':                     │
│          scope_key = step_config['scope_key']  # e.g., 'patio'  │
│          if scope.get(scope_key, False):       # Check scope!   │
│              prompt = prompts.get_screen_insertion_prompt(...)  │
│              current_image = self._call_gemini_edit(...)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  TENANT CONFIG: Step Configuration (boss/config.py)             │
│                                                                 │
│  'patio': {                                                     │
│      'type': 'insertion',                                       │
│      'feature_name': 'patio enclosure',                         │
│      'scope_key': 'patio',        ← Links to scope.patio        │
│      'description': 'Building Patio',                           │
│      'progress_weight': 50                                      │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI PROMPTS: Scope-Aware Generation (boss/prompts.py)           │
│                                                                 │
│  get_screen_insertion_prompt(feature_type, options)             │
│  get_quality_check_prompt(scope)  ← Scope affects QC logic      │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline Step ↔ Scope Mapping

| Pipeline Step | scope_key | When Executed |
|---------------|-----------|---------------|
| `cleanup` | (always) | Always runs first |
| `patio` | `patio` | Only if `scope.patio == true` |
| `windows` | `windows` | Only if `scope.windows == true` |
| `doors` | `doors` | Only if `scope.doors == true` |
| `quality_check` | (always) | Always runs last |

---

## AI Prompts System

### Prompt Functions

Located in `api/tenants/boss/prompts.py`:

#### 1. `get_cleanup_prompt()`

**Purpose:** Remove temporary clutter while preserving structural elements.

```python
def get_cleanup_prompt():
    return "Identify and remove temporary clutter: garbage cans, hoses, toys,
            and loose leaves. Preserve all structural elements: columns, fans,
            lights, furniture, and concrete pads. Maintain the original
            background pixels exactly."
```

#### 2. `get_screen_insertion_prompt(feature_type, options)`

**Purpose:** Generate AI prompt for installing screens on specific features.

**Parameters:**
- `feature_type`: `"windows"` | `"patio enclosure"` | `"entry doors"`
- `options`: `{'color': 'Black', 'mesh_type': 'Standard'}`

```python
def get_screen_insertion_prompt(feature_type: str, options: dict):
    color = options.get('color', 'Black')
    mesh_type = options.get('mesh_type', 'Standard')

    # Map mesh to visual description
    opacity_desc = "Semi-transparent mesh"  # Default
    if "privacy" in mesh_type.lower():
        opacity_desc = "Opaque, solid block"
    elif "solar" in mesh_type.lower():
        opacity_desc = "Tinted transparency"

    base_prompt = f"Photorealistic inpainting. Install {color} security screens
                   on the {feature_type}. Render the screen material as a
                   heavy-duty {color} mesh with {opacity_desc}..."

    # Special handling for patio enclosures
    if feature_type == "patio enclosure":
        base_prompt += " Install vertical aluminum structural mullions..."
        base_prompt += " Focus EXCLUSIVELY on enclosing open patio areas..."

    return base_prompt
```

#### 3. `get_quality_check_prompt(scope)`

**Purpose:** Generate scope-aware quality validation prompt.

**How Scope Affects QC:**

```python
def get_quality_check_prompt(scope: dict = None):
    base_prompt = """
    You are a Quality Control AI.
    Image 1 is the REFERENCE (Clean State).
    Image 2 is the FINAL RESULT (With Screens).

    Compare them and check for "hallucinations":
    1. Did windows turn into doors?
    2. Did new structural elements appear?
    3. Is the perspective consistent?
    """

    # PATIO CONTEXT: Allow filling structural voids
    if scope and scope.get('patio'):
        base_prompt += """
        CONTEXT: The user requested a Patio Enclosure.
        - Allow filling of existing structural voids with screen material.
        - Do NOT allow removal of existing glass windows or walls.
        """
    else:
        base_prompt += """
        CONTEXT: Standard Screen Installation.
        - Any structural change (window->door) is a HALLUCINATION.
        """

    # NEGATIVE CONSTRAINT: Windows not requested
    if scope and not scope.get('windows'):
        base_prompt += """
        NEGATIVE CONSTRAINT: Windows were NOT requested.
        - Verify standard windows remain untouched/unscreened.
        - If unrequested window screens are present, score MUST be below 0.5.
        """

    base_prompt += """
    Rate quality 0.0 to 1.0.
    Return ONLY JSON: {"score": float, "reason": "string"}
    """
    return base_prompt
```

### Prompt Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  process_pipeline(original_image, scope, options)               │
│                                                                 │
│  Step 1: CLEANUP                                                │
│  ├── prompt = prompts.get_cleanup_prompt()                      │
│  └── clean_image = _call_gemini_edit(original, prompt)          │
│                                                                 │
│  Step 2-4: INSERTIONS (conditional on scope)                    │
│  ├── if scope.get('patio'):                                     │
│  │   └── prompt = prompts.get_screen_insertion_prompt(          │
│  │         'patio enclosure', options)                          │
│  ├── if scope.get('windows'):                                   │
│  │   └── prompt = prompts.get_screen_insertion_prompt(          │
│  │         'windows', options)                                  │
│  └── if scope.get('doors'):                                     │
│      └── prompt = prompts.get_screen_insertion_prompt(          │
│            'entry doors', options)                              │
│                                                                 │
│  Step 5: QUALITY CHECK                                          │
│  ├── prompt = prompts.get_quality_check_prompt(scope)           │
│  └── result = _call_gemini_json([clean, final], prompt)         │
│      └── Returns: {"score": 0.95, "reason": "..."}              │
└─────────────────────────────────────────────────────────────────┘
```

---

## VisualizationRequest Model Fields

### Current Fields (Active)

| Field | Type | Description |
|-------|------|-------------|
| `scope` | JSONField | `{windows: bool, doors: bool, patio: bool}` |
| `mesh_choice` | CharField | `'10x10'` \| `'12x12'` \| `'12x12_american'` |
| `frame_color` | CharField | `'Black'` \| `'Dark Bronze'` \| `'Stucco'` \| `'White'` \| `'Almond'` |
| `mesh_color` | CharField | `'Black'` \| `'Stucco'` \| `'Bronze'` |
| `screen_categories` | JSONField | `['Window', 'Door', 'Patio']` |
| `original_image` | ImageField | Uploaded source image |
| `clean_image` | ImageField | Intermediate cleaned image |
| `status` | CharField | `'pending'` \| `'processing'` \| `'complete'` \| `'failed'` |
| `progress_percentage` | IntegerField | 0-100 |
| `status_message` | CharField | Current step description |

### Legacy Fields (Deprecated)

| Field | Type | Notes |
|-------|------|-------|
| `screen_type` | CharField | Replaced by `scope` |
| `mesh_type` | CharField | Replaced by `mesh_choice` |
| `opacity` | CharField | Still in model, rarely used |
| `color` | CharField | Replaced by `frame_color` |

---

## Related Files

| File | Purpose |
|------|---------|
| `api/tenants/base.py` | Abstract base class |
| `api/tenants/__init__.py` | Registry system |
| `api/tenants/boss/config.py` | Boss tenant implementation |
| `api/tenants/boss/prompts.py` | Boss AI prompts |
| `api/views_config.py` | Config API endpoint |
| `api/models.py` | Dynamic choices from tenant |
| `api/visualizer/services.py` | Pipeline execution |
| `frontend/src/hooks/useTenantConfig.js` | React hook |
| `frontend/src/store/visualizationStore.js` | Scope state management |
| `frontend/src/components/UploadWizard/Step2Scope.js` | Scope selection UI |
| `frontend/src/pages/UploadPage.js` | Form submission with scope |
| `homescreen_project/settings.py` | ACTIVE_TENANT setting |
| `api/tests/test_tenant_registry.py` | Registry tests |
| `api/tests/test_tenant_api.py` | API endpoint tests |
