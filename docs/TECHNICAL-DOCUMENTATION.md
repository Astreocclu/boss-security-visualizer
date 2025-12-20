# Boss Security Visualizer - Technical Documentation

**Last Updated:** December 1, 2025
**Version:** 1.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Django Apps & Modules](#3-django-apps--modules)
4. [Database Models](#4-database-models)
5. [API Endpoints](#5-api-endpoints)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Core Services](#7-core-services)
8. [AI Integration](#8-ai-integration)
9. [Multi-Tenant System](#9-multi-tenant-system)
10. [Pipeline Architecture](#10-pipeline-architecture)
11. [Configuration](#11-configuration)
12. [Dependencies](#12-dependencies)
13. [Testing](#13-testing)
14. [Security](#14-security)

---

## 1. Project Overview

**Project Name:** Boss Security Visualizer
**Purpose:** AI-powered visualization of security screens on building images

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 4.0+, Django REST Framework |
| Frontend | React 19.1, React Router 7, Zustand |
| Database | PostgreSQL (prod) / SQLite (dev) |
| AI | Google Gemini API (gemini-3-pro-image-preview) |
| PDF | ReportLab |
| Payments | Stripe (stubbed) |
| Image Processing | Pillow |

---

## 2. Directory Structure

```
boss-security-visualizer/
├── api/                          # Django backend
│   ├── models.py                 # Core models
│   ├── views.py                  # API viewsets
│   ├── serializers.py            # DRF serializers
│   ├── urls.py                   # API routes
│   ├── ai_services/              # AI abstraction layer
│   │   ├── providers/
│   │   │   └── gemini_provider.py
│   │   ├── factory.py
│   │   └── registry.py
│   ├── audit/                    # Security audit module
│   │   ├── services.py
│   │   └── prompts.py
│   ├── visualizer/               # Image processing pipeline
│   │   ├── services.py           # ScreenVisualizer
│   │   └── prompts.py
│   └── tenants/                  # Multi-tenant config
│       ├── base.py
│       └── boss/
│           ├── config.py
│           └── prompts.py
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── pages/                # Page components
│   │   ├── components/           # Reusable components
│   │   ├── store/                # Zustand state
│   │   └── services/             # API client
│   └── cypress/                  # E2E tests
├── homescreen_project/           # Django settings
├── media/                        # Uploaded/generated images
│   ├── originals/
│   ├── generated/
│   ├── pipeline_steps/           # Debug images
│   └── thinking_logs/            # AI reasoning logs
├── docs/                         # Documentation
└── requirements.txt
```

---

## 3. Django Apps & Modules

### Main App: `api`

| Module | Purpose |
|--------|---------|
| `visualizer` | Image visualization pipeline |
| `audit` | Security vulnerability detection |
| `ai_services` | AI provider abstraction |
| `tenants` | Multi-tenant configuration |
| `feedback` | User feedback collection |
| `monitoring` | Production monitoring |

---

## 4. Database Models

### VisualizationRequest (Core Model)

```python
class VisualizationRequest(models.Model):
    user = models.ForeignKey(User)
    original_image = models.ImageField()
    clean_image = models.ImageField()

    # Configuration
    screen_categories = models.JSONField()  # ['windows', 'doors', 'patio']
    mesh_choice = models.CharField()        # '10x10', '12x12', '12x12_american'
    frame_color = models.CharField()        # 'Black', 'Dark Bronze', etc.
    mesh_color = models.CharField()         # 'Black', 'Stucco', 'Bronze'
    scope = models.JSONField()              # {hasPatio, hasWindows, hasDoors, doorType}

    # Status tracking
    status = models.CharField()             # pending/processing/complete/failed
    progress_percentage = models.PositiveIntegerField()
    status_message = models.CharField()
    error_message = models.TextField()

    # Timestamps
    created_at = models.DateTimeField()
    processing_started_at = models.DateTimeField()
    processing_completed_at = models.DateTimeField()
```

### GeneratedImage

```python
class GeneratedImage(models.Model):
    request = models.OneToOneField(VisualizationRequest)
    generated_image = models.ImageField()
    file_size = models.PositiveIntegerField()
    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()
    metadata = models.JSONField()  # quality scores, generation params
```

### AuditReport

```python
class AuditReport(models.Model):
    request = models.OneToOneField(VisualizationRequest)
    has_ground_level_access = models.BooleanField()
    has_concealment = models.BooleanField()
    has_glass_proximity = models.BooleanField()
    has_hardware_weakness = models.BooleanField()
    vulnerabilities = models.JSONField()  # detailed findings with coordinates
    analysis_summary = models.TextField()
```

---

## 5. API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login (returns JWT tokens) |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/logout/` | Logout |

### Visualizations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/visualizations/` | List user's requests |
| POST | `/api/visualizations/` | Create new request |
| GET | `/api/visualizations/{id}/` | Get specific request |
| DELETE | `/api/visualizations/{id}/` | Delete request |
| POST | `/api/visualizations/{id}/retry/` | Retry failed request |
| GET | `/api/visualizations/{id}/pdf/` | Download PDF quote |

### Audit

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/audit/{id}/generate/` | Generate security audit |
| GET | `/api/audit/{id}/retrieve_report/` | Get audit report |

### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config/` | Get tenant configuration |

---

## 6. Frontend Architecture

### Pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/login` | LoginPage | User authentication |
| `/register` | RegisterPage | Account creation |
| `/` | DashboardPage | Main interface |
| `/upload` | UploadPage | 5-step upload wizard |
| `/results` | ResultsPage | Results listing |
| `/results/{id}` | ResultDetailPage | Detailed result view |

### Upload Wizard Steps

1. **Step1Categories** - Select screen types (window, door, patio)
2. **Step2Mesh** - Choose mesh type
3. **Step3Customization** - Frame/mesh colors
4. **Step4Upload** - Image file upload
5. **Step5Review** - Final confirmation

### State Management (Zustand)

```javascript
// authStore - Authentication state
const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: async (credentials) => { ... },
  logout: () => { ... },
}));

// visualizationStore - Request state
const useVisualizationStore = create((set) => ({
  requests: [],
  scope: { hasPatio: false, hasWindows: true, hasDoors: false },
  fetchRequests: async () => { ... },
  createRequest: async (formData) => { ... },
}));
```

---

## 7. Core Services

### ScreenVisualizer (`api/visualizer/services.py`)

Main image processing service using Gemini AI.

```python
class ScreenVisualizer:
    def process_pipeline(self, original_image, scope, options, progress_callback):
        """Execute visualization steps sequentially."""
        # 1. Cleanup - Remove debris, enhance weather
        # 2. Doors - Add security screens to doors
        # 3. Windows - Add security screens to windows
        # 4. Patio - Add patio enclosure
        # 5. Quality Check - Validate output

    def _call_gemini_edit(self, image, prompt, step_name):
        """API call with thinking mode enabled."""
        config_args = {
            "response_modalities": ["TEXT", "IMAGE"],
            "thinking_config": ThinkingConfig(include_thoughts=True),
            "image_generation_config": ImageGenerationConfig(
                guidance_scale=70,
                person_generation="dont_generate_people"
            )
        }

    def _log_thinking(self, step_name, prompt, thinking_text):
        """Save AI reasoning to media/thinking_logs/"""
```

### AuditService (`api/audit/services.py`)

Security vulnerability detection service.

```python
class AuditService:
    def perform_audit(self, visualization_request):
        """Analyze image for security vulnerabilities."""
        # Returns: ground_level_access, concealment, glass_proximity, etc.
```

---

## 8. AI Integration

### Google Gemini API

**Model:** `gemini-3-pro-image-preview`

**Configuration:**
```python
config = {
    "response_modalities": ["TEXT", "IMAGE"],
    "thinking_config": ThinkingConfig(include_thoughts=True),
    "image_generation_config": ImageGenerationConfig(
        guidance_scale=70,
        person_generation="dont_generate_people"
    )
}
```

**Features:**
- Thinking Mode - Better reasoning for complex edits
- Retry logic with exponential backoff (handles 429 rate limits)
- Token usage tracking per step
- Thinking logs saved to `media/thinking_logs/`

### Thinking Logs

Location: `media/thinking_logs/thinking_{timestamp}_{step}.txt`

Format:
```
=== Gemini Thinking Log ===
Timestamp: 2025-12-01T19:30:00
Step: patio_analysis

--- PROMPT ---
[full prompt text]

--- THINKING ---
[Part 1]
- OPENING WIDTH: 18 feet
- MULLION COUNT: 3
- POSITIONS: [25%, 50%, 75%]
```

---

## 9. Multi-Tenant System

### Architecture

```python
# Base configuration (api/tenants/base.py)
class BaseTenantConfig(ABC):
    @abstractmethod
    def get_pipeline_steps(self) -> List[str]: ...

    @abstractmethod
    def get_mesh_choices(self) -> List[dict]: ...

    @abstractmethod
    def get_frame_colors(self) -> List[dict]: ...

# Boss implementation (api/tenants/boss/config.py)
class BossTenantConfig(BaseTenantConfig):
    def get_pipeline_steps(self):
        return ['cleanup', 'doors', 'windows', 'patio', 'quality_check']

    def get_mesh_choices(self):
        return [
            {'value': '10x10', 'label': '10x10 Standard'},
            {'value': '12x12', 'label': '12x12 Heavy Duty'},
            {'value': '12x12_american', 'label': '12x12 American'},
        ]
```

### Configuration Options

| Option | Values |
|--------|--------|
| Mesh Types | 10x10, 12x12, 12x12_american |
| Frame Colors | Black, Dark Bronze, Stucco, White, Almond |
| Mesh Colors | Black, Stucco, Bronze |
| Opacity | 80%, 95%, 99% |

---

## 10. Pipeline Architecture

### Execution Order

```
cleanup → doors → windows → patio → quality_check
```

### Step Configuration

```python
STEP_CONFIGS = {
    'cleanup': {
        'type': 'cleanup',
        'description': 'Cleaning image',
        'progress_weight': 20,
    },
    'doors': {
        'type': 'insertion',
        'scope_key': 'doors',
        'feature_name': 'entry doors',
        'progress_weight': 40,
    },
    'windows': {
        'type': 'insertion',
        'scope_key': 'windows',
        'feature_name': 'windows',
        'progress_weight': 60,
    },
    'patio': {
        'type': 'insertion',
        'scope_key': 'patio',
        'feature_name': 'patio enclosure',
        'progress_weight': 80,
    },
    'quality_check': {
        'type': 'quality_check',
        'progress_weight': 100,
    },
}
```

### Prompts

**Cleanup Prompt:**
```
Please clean this image of any debris, furniture, and temporary items.
Make the weather conditions ideal and sunny with clear blue sky.
Keep all permanent structures exactly as they are.
```

**Screen Insertion Prompt (Patio):**
```
Photorealistic inpainting. Install {color} security screens on the patio enclosure.
Render the screen material as a heavy-duty {color} mesh with {opacity}.
Maintain flush mounting frames.

In your text response, state EXACTLY:
- OPENING WIDTH: [X] feet
- MULLION COUNT: [Y]
- POSITIONS: [list]

IMPORTANT: Install visible vertical aluminum structural mullions (support posts)
every 5 feet across the screen span - these mullions are essential and must be
clearly visible.

Focus EXCLUSIVELY on enclosing the open patio/porch areas.
Leave all standard windows and other openings in their original state.
```

---

## 11. Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
ACTIVE_TENANT=boss
USE_TENANT_REGISTRY=true
STRIPE_API_KEY=sk_test_...
DEBUG=True
```

### Django Settings

```python
# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# CORS
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 12. Dependencies

### Backend (`requirements.txt`)

```
Django>=4.0
djangorestframework>=3.14
django-cors-headers
djangorestframework-simplejwt
Pillow>=10.0.0
google-genai>=0.3.0
reportlab>=4.0.0
stripe>=7.0.0
```

### Frontend (`package.json`)

```json
{
  "dependencies": {
    "react": "^19.1.0",
    "react-router-dom": "^7.6.1",
    "zustand": "^5.0.3",
    "axios": "^1.8.4",
    "lucide-react": "^0.555.0"
  }
}
```

---

## 13. Testing

### Backend Tests

```bash
python manage.py test api.tests
```

Test files:
- `test_ai_services.py` - AI integration tests
- `test_screen_visualizer.py` - Pipeline tests
- `test_tenant_api.py` - Tenant configuration tests

### Frontend Tests

```bash
# Unit tests
npm run test

# E2E tests
npx cypress open
```

Test files:
- `cypress/e2e/auth.cy.js` - Authentication flow
- `cypress/e2e/dashboard.cy.js` - Dashboard interactions
- `cypress/e2e/image-upload.cy.js` - Upload workflow

---

## 14. Security

### Authentication

- JWT-based authentication
- Access tokens: 60-minute lifetime
- Refresh tokens: 7-day lifetime
- Auto-refresh on 401 response

### Image Validation

```python
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_DIMENSIONS = (8192, 8192)
```

### API Permissions

- `IsAuthenticated` - Most endpoints
- `IsOwnerOrReadOnly` - User-specific resources
- `AllowAny` - Config, registration

---

## Debug Outputs

### Pipeline Steps

Location: `media/pipeline_steps/`

Filenames: `pipeline_{timestamp}_{step_number}_{step_name}.jpg`

### Thinking Logs

Location: `media/thinking_logs/`

Filenames:
- Regular: `thinking_{timestamp}_{step_name}.txt`
- Patio: `thinking_{timestamp}_patio_analysis.txt`

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Django Models | 4 |
| API Endpoints | 25+ |
| Frontend Pages | 8 |
| React Components | 30+ |
| Pipeline Steps | 5 |

---

*Documentation generated December 1, 2025*
