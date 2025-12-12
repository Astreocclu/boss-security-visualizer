# Multi-Vertical Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable single codebase to support windows, roofs, and future verticals while ensuring non-specific improvements flow to ALL verticals automatically.

**Architecture:** Single-repo multi-tenant V2 architecture. Core handlers are generic; tenant-specific logic lives in `api/tenants/{tenant}/`. Each tenant provides config.py (product schema, pipeline steps) and prompts.py (AI prompts). The pipeline_registry.py calls a standard `get_insertion_prompt()` interface.

**Tech Stack:** Django 4.x, Python 3.10+, existing tenant system

---

## Phase 1: Core Refactoring (Enable Generic Verticals)

### Task 1: Add Generic Prompt Interface to Boss Tenant

**Files:**
- Modify: `api/tenants/boss/prompts.py`

**Step 1: Write the failing test**

Create test file: `api/tenants/boss/tests/test_prompts.py`

```python
"""Test Boss prompts module has generic interface."""
import pytest
from api.tenants.boss import prompts


def test_get_insertion_prompt_exists():
    """Boss prompts must expose get_insertion_prompt for pipeline_registry."""
    assert hasattr(prompts, 'get_insertion_prompt')
    assert callable(prompts.get_insertion_prompt)


def test_get_insertion_prompt_returns_string():
    """get_insertion_prompt must return a prompt string."""
    result = prompts.get_insertion_prompt('windows', {'color': 'Black'})
    assert isinstance(result, str)
    assert len(result) > 0
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/boss/tests/test_prompts.py -v`

Expected: FAIL with `AttributeError: module has no attribute 'get_insertion_prompt'`

**Step 3: Write minimal implementation**

Add to end of `api/tenants/boss/prompts.py`:

```python
def get_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generic insertion prompt interface for pipeline_registry.

    Routes to the existing get_screen_insertion_prompt for Boss vertical.
    """
    return get_screen_insertion_prompt(feature_type, options)
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/boss/tests/test_prompts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/boss/prompts.py api/tenants/boss/tests/
git commit -m "feat(boss): add generic get_insertion_prompt interface

Adds get_insertion_prompt() wrapper that routes to existing
get_screen_insertion_prompt() for backwards compatibility.
This enables pipeline_registry to use a standard interface.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Add Generic Prompt Interface to Pools Tenant

**Files:**
- Modify: `api/tenants/pools/prompts.py`

**Step 1: Write the failing test**

Create test file: `api/tenants/pools/tests/test_prompts.py`

```python
"""Test Pools prompts module has generic interface."""
import pytest
from api.tenants.pools import prompts


def test_get_insertion_prompt_exists():
    """Pools prompts must expose get_insertion_prompt for pipeline_registry."""
    assert hasattr(prompts, 'get_insertion_prompt')
    assert callable(prompts.get_insertion_prompt)


def test_get_insertion_prompt_returns_string():
    """get_insertion_prompt must return a prompt string."""
    result = prompts.get_insertion_prompt('pool', {'pool_shape': 'rectangle'})
    assert isinstance(result, str)
    assert len(result) > 0
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py -v`

Expected: FAIL with `AttributeError: module has no attribute 'get_insertion_prompt'`

**Step 3: Write minimal implementation**

Add to end of `api/tenants/pools/prompts.py`:

```python
def get_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generic insertion prompt interface for pipeline_registry.

    Routes to the existing get_pool_insertion_prompt for Pools vertical.
    """
    return get_pool_insertion_prompt(feature_type, options)
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/pools/tests/test_prompts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/pools/prompts.py api/tenants/pools/tests/
git commit -m "feat(pools): add generic get_insertion_prompt interface

Adds get_insertion_prompt() wrapper that routes to existing
get_pool_insertion_prompt() for backwards compatibility.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Update Pipeline Registry to Use Generic Interface

**Files:**
- Modify: `api/services/pipeline_registry.py:80-86`
- Test: `api/services/tests/test_pipeline_registry.py`

**Step 1: Write the failing test**

Create/update `api/services/tests/test_pipeline_registry.py`:

```python
"""Test pipeline_registry uses generic prompt interface."""
import pytest
from unittest.mock import MagicMock, patch


def test_insertion_handler_uses_generic_interface():
    """insertion_handler must call get_insertion_prompt, not vertical-specific functions."""
    from api.services.pipeline_registry import insertion_handler

    # Create mock prompts module with ONLY generic interface
    mock_prompts = MagicMock()
    mock_prompts.get_insertion_prompt = MagicMock(return_value="Test prompt")
    # Explicitly remove vertical-specific functions
    del mock_prompts.get_screen_insertion_prompt
    del mock_prompts.get_pool_insertion_prompt

    mock_visualizer = MagicMock()
    mock_visualizer._call_gemini_edit = MagicMock(return_value="result_image")

    context = {
        'visualizer': mock_visualizer,
        'image': 'test_image',
        'prompts': mock_prompts,
        'scope': {'windows': True},
        'options': {'color': 'Black'},
    }
    step_config = {
        'type': 'insertion',
        'feature_name': 'windows',
        'scope_key': 'windows',
    }

    result = insertion_handler('windows', step_config, context)

    # Verify generic interface was called
    mock_prompts.get_insertion_prompt.assert_called_once_with('windows', {'color': 'Black'})
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/services/tests/test_pipeline_registry.py::test_insertion_handler_uses_generic_interface -v`

Expected: FAIL (current code checks for `get_screen_insertion_prompt` first)

**Step 3: Write minimal implementation**

Edit `api/services/pipeline_registry.py`, replace lines 80-86:

**BEFORE:**
```python
    # Get appropriate insertion prompt
    if hasattr(prompts, 'get_screen_insertion_prompt'):
        prompt = prompts.get_screen_insertion_prompt(feature_name, options)
    elif hasattr(prompts, 'get_pool_insertion_prompt'):
        prompt = prompts.get_pool_insertion_prompt(feature_name, options)
    else:
        raise ValueError(f"No insertion prompt function in prompts module")
```

**AFTER:**
```python
    # Get insertion prompt using standard interface
    if not hasattr(prompts, 'get_insertion_prompt'):
        raise ValueError(
            f"Prompts module missing get_insertion_prompt(). "
            f"Each tenant's prompts.py must implement this function."
        )
    prompt = prompts.get_insertion_prompt(feature_name, options)
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/services/tests/test_pipeline_registry.py::test_insertion_handler_uses_generic_interface -v`

Expected: PASS

**Step 5: Run full test suite to verify no regressions**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/ -v --tb=short`

Expected: All existing tests pass

**Step 6: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/services/pipeline_registry.py api/services/tests/
git commit -m "refactor(pipeline): use generic get_insertion_prompt interface

BREAKING: Removes hardcoded checks for get_screen_insertion_prompt and
get_pool_insertion_prompt. All tenant prompts.py modules must now
implement get_insertion_prompt(feature_type, options).

This enables arbitrary new verticals (windows, roofs, etc.) without
modifying pipeline_registry.py.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Add Windows Vertical

### Task 4: Create Windows Tenant Directory Structure

**Files:**
- Create: `api/tenants/windows/__init__.py`
- Create: `api/tenants/windows/config.py`
- Create: `api/tenants/windows/prompts.py`
- Create: `api/tenants/windows/tests/__init__.py`

**Step 1: Create directory and __init__.py**

```bash
mkdir -p /home/reid/testhome/boss-security-visualizer/api/tenants/windows/tests
touch /home/reid/testhome/boss-security-visualizer/api/tenants/windows/__init__.py
touch /home/reid/testhome/boss-security-visualizer/api/tenants/windows/tests/__init__.py
```

**Step 2: Write the failing test for config**

Create `api/tenants/windows/tests/test_config.py`:

```python
"""Test Windows tenant configuration."""
import pytest
from api.tenants.windows.config import WindowsTenantConfig


def test_tenant_id():
    config = WindowsTenantConfig()
    assert config.tenant_id == "windows"


def test_display_name():
    config = WindowsTenantConfig()
    assert config.display_name == "Window Visualizer"


def test_product_schema_has_required_fields():
    config = WindowsTenantConfig()
    schema = config.get_product_schema()

    assert isinstance(schema, list)
    assert len(schema) >= 2  # At least window_type and frame_color

    keys = [cat['key'] for cat in schema]
    assert 'window_type' in keys
    assert 'frame_color' in keys


def test_pipeline_steps():
    config = WindowsTenantConfig()
    steps = config.get_pipeline_steps()

    assert 'cleanup' in steps
    assert 'quality_check' in steps
    assert steps[0] == 'cleanup'  # Cleanup first
    assert steps[-1] == 'quality_check'  # QC last
```

**Step 3: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/windows/tests/test_config.py -v`

Expected: FAIL with `ModuleNotFoundError`

**Step 4: Write config.py implementation**

Create `api/tenants/windows/config.py`:

```python
"""Window Visualizer tenant configuration."""
from typing import List, Dict, Any
from ..base import BaseTenantConfig


class WindowsTenantConfig(BaseTenantConfig):

    @property
    def tenant_id(self) -> str:
        return "windows"

    @property
    def display_name(self) -> str:
        return "Window Visualizer"

    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Product categories for Window Visualizer.

        Defines window-specific configuration options.
        """
        return [
            {
                "key": "window_type",
                "label": "Window Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "double_hung", "label": "Double Hung"},
                    {"value": "casement", "label": "Casement"},
                    {"value": "sliding", "label": "Sliding"},
                    {"value": "picture", "label": "Picture Window"},
                    {"value": "bay", "label": "Bay Window"},
                    {"value": "awning", "label": "Awning"},
                ]
            },
            {
                "key": "frame_color",
                "label": "Frame Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "white", "label": "White"},
                    {"value": "black", "label": "Black"},
                    {"value": "bronze", "label": "Bronze"},
                    {"value": "almond", "label": "Almond"},
                    {"value": "wood_grain", "label": "Wood Grain"},
                ]
            },
            {
                "key": "glass_type",
                "label": "Glass Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "clear", "label": "Clear"},
                    {"value": "low_e", "label": "Low-E"},
                    {"value": "tinted", "label": "Tinted"},
                    {"value": "frosted", "label": "Frosted"},
                ]
            },
            {
                "key": "grid_pattern",
                "label": "Grid Pattern",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "none", "label": "None"},
                    {"value": "colonial", "label": "Colonial"},
                    {"value": "prairie", "label": "Prairie"},
                    {"value": "diamond", "label": "Diamond"},
                ]
            },
        ]

    def get_pipeline_steps(self) -> List[str]:
        """Pipeline steps for window visualization."""
        return ['cleanup', 'window_insertion', 'quality_check']

    def get_prompts_module(self):
        from . import prompts
        return prompts

    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'description': 'Preparing image',
                'progress_weight': 20
            },
            'window_insertion': {
                'type': 'insertion',
                'feature_name': 'windows',
                'scope_key': 'windows',
                'description': 'Visualizing Windows',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Final Review',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
```

**Step 5: Run test to verify config passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/windows/tests/test_config.py -v`

Expected: PASS

**Step 6: Commit config**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/windows/
git commit -m "feat(windows): add WindowsTenantConfig

Adds new windows vertical with:
- Window types: double hung, casement, sliding, picture, bay, awning
- Frame colors: white, black, bronze, almond, wood grain
- Glass types: clear, low-e, tinted, frosted
- Grid patterns: none, colonial, prairie, diamond

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Create Windows Prompts Module

**Files:**
- Create: `api/tenants/windows/prompts.py`
- Test: `api/tenants/windows/tests/test_prompts.py`

**Step 1: Write the failing test**

Create `api/tenants/windows/tests/test_prompts.py`:

```python
"""Test Windows prompts module."""
import pytest
from api.tenants.windows import prompts


def test_get_cleanup_prompt():
    result = prompts.get_cleanup_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_insertion_prompt():
    result = prompts.get_insertion_prompt('windows', {
        'window_type': 'double_hung',
        'frame_color': 'white',
        'glass_type': 'clear'
    })
    assert isinstance(result, str)
    assert 'double_hung' in result.lower() or 'double hung' in result.lower()


def test_get_quality_check_prompt():
    result = prompts.get_quality_check_prompt({'windows': True})
    assert isinstance(result, str)
    assert len(result) > 0
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/windows/tests/test_prompts.py -v`

Expected: FAIL

**Step 3: Write prompts.py implementation**

Create `api/tenants/windows/prompts.py`:

```python
"""Window Visualizer AI prompts.

Prompts for visualizing replacement windows on homes.
"""


def get_cleanup_prompt() -> str:
    """Return cleanup prompt for window visualization."""
    return """Analyze this image for window visualization preparation.

Clean the image by:
- Removing any temporary items near windows (ladders, tools, covers)
- Ensuring clear visibility of all window openings
- Maintaining the natural lighting and house architecture

PRESERVE EXACTLY:
- All permanent structures
- Existing window frames and openings
- House siding, trim, and architectural details
- Landscaping and surroundings

Output the cleaned image maintaining original perspective and lighting."""


def get_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generic insertion prompt interface for pipeline_registry.

    Args:
        feature_type: 'windows' (primary feature for this vertical)
        options: Dict with window_type, frame_color, glass_type, grid_pattern
    """
    window_type = options.get('window_type', 'double_hung')
    frame_color = options.get('frame_color', 'white')
    glass_type = options.get('glass_type', 'clear')
    grid_pattern = options.get('grid_pattern', 'none')

    # Format window type for display
    window_type_display = window_type.replace('_', ' ').title()

    prompt = f"""Photorealistic window replacement visualization.

Replace the existing windows with new {window_type_display} windows.

Window specifications:
- Type: {window_type_display}
- Frame Color: {frame_color.replace('_', ' ').title()}
- Glass: {glass_type.replace('_', ' ').title()}"""

    if grid_pattern != 'none':
        prompt += f"\n- Grid Pattern: {grid_pattern.replace('_', ' ').title()}"

    prompt += """

Render requirements:
- Realistic window frame profiles matching the style
- Natural glass reflections appropriate for the lighting
- Proper shadows on frames from sunlight direction
- Seamless integration with existing trim and siding
- Maintain architectural proportions and symmetry
- No distortion of surrounding house elements

Do not modify anything except the windows themselves."""

    return prompt


def get_quality_check_prompt(scope: dict = None) -> str:
    """Return quality check prompt for window visualization."""
    return """Review this window visualization for quality and realism.

Compare Image 1 (reference) with Image 2 (final result).

Check for:
- Realistic window frame appearance and proportions
- Natural glass reflections matching lighting conditions
- Proper integration with existing trim and siding
- No distortion of house structure or surroundings
- Consistent shadow direction with original image
- No visual artifacts or floating elements

Rate quality 0.0 to 1.0:
- Below 0.5: Major issues (wrong proportions, obvious artifacts)
- Below 0.7: Minor issues (slight inconsistencies)
- Above 0.7: Good quality visualization

Return ONLY a JSON object:
{
    "score": float,
    "reason": "string"
}"""
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/windows/tests/test_prompts.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/windows/prompts.py api/tenants/windows/tests/test_prompts.py
git commit -m "feat(windows): add AI prompts for window visualization

Implements get_cleanup_prompt, get_insertion_prompt, and
get_quality_check_prompt for the windows vertical.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 6: Register Windows Tenant

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Write the failing test**

Add to existing test file or create `api/tenants/tests/test_registry.py`:

```python
"""Test tenant registry includes all tenants."""
import pytest
from api.tenants import get_tenant_config, get_all_tenants


def test_windows_tenant_registered():
    """Windows tenant must be in registry."""
    tenants = get_all_tenants()
    assert 'windows' in tenants


def test_windows_tenant_config_loadable():
    """Windows tenant config must be loadable."""
    config = get_tenant_config('windows')
    assert config.tenant_id == 'windows'
```

**Step 2: Run test to verify it fails**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/tests/test_registry.py -v`

Expected: FAIL with `ValueError: Unknown tenant: windows`

**Step 3: Update __init__.py**

Edit `api/tenants/__init__.py`, add import and registration:

After line 16 (`from .pools.config import PoolsTenantConfig`), add:
```python
from .windows.config import WindowsTenantConfig
```

After line 87 (`register_tenant(PoolsTenantConfig())`), add:
```python
register_tenant(WindowsTenantConfig())
```

**Step 4: Run test to verify it passes**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/tests/test_registry.py -v`

Expected: PASS

**Step 5: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/__init__.py api/tenants/tests/
git commit -m "feat(tenants): register windows vertical

Windows tenant is now available via ACTIVE_TENANT=windows

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 3: Add Roofs Vertical

### Task 7: Create Roofs Tenant (Following Same Pattern)

**Files:**
- Create: `api/tenants/roofs/__init__.py`
- Create: `api/tenants/roofs/config.py`
- Create: `api/tenants/roofs/prompts.py`
- Create: `api/tenants/roofs/tests/`

**Step 1: Create directory structure**

```bash
mkdir -p /home/reid/testhome/boss-security-visualizer/api/tenants/roofs/tests
touch /home/reid/testhome/boss-security-visualizer/api/tenants/roofs/__init__.py
touch /home/reid/testhome/boss-security-visualizer/api/tenants/roofs/tests/__init__.py
```

**Step 2: Write test for config**

Create `api/tenants/roofs/tests/test_config.py`:

```python
"""Test Roofs tenant configuration."""
import pytest
from api.tenants.roofs.config import RoofsTenantConfig


def test_tenant_id():
    config = RoofsTenantConfig()
    assert config.tenant_id == "roofs"


def test_product_schema_has_required_fields():
    config = RoofsTenantConfig()
    schema = config.get_product_schema()

    keys = [cat['key'] for cat in schema]
    assert 'roof_material' in keys
    assert 'roof_color' in keys
```

**Step 3: Write config.py**

Create `api/tenants/roofs/config.py`:

```python
"""Roof Visualizer tenant configuration."""
from typing import List, Dict, Any
from ..base import BaseTenantConfig


class RoofsTenantConfig(BaseTenantConfig):

    @property
    def tenant_id(self) -> str:
        return "roofs"

    @property
    def display_name(self) -> str:
        return "Roof Visualizer"

    def get_product_schema(self) -> List[Dict[str, Any]]:
        """Product categories for Roof Visualizer."""
        return [
            {
                "key": "roof_material",
                "label": "Roof Material",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "asphalt_shingle", "label": "Asphalt Shingle"},
                    {"value": "metal", "label": "Metal"},
                    {"value": "tile_clay", "label": "Clay Tile"},
                    {"value": "tile_concrete", "label": "Concrete Tile"},
                    {"value": "slate", "label": "Slate"},
                    {"value": "wood_shake", "label": "Wood Shake"},
                ]
            },
            {
                "key": "roof_color",
                "label": "Roof Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "charcoal", "label": "Charcoal"},
                    {"value": "black", "label": "Black"},
                    {"value": "brown", "label": "Brown"},
                    {"value": "gray", "label": "Gray"},
                    {"value": "terracotta", "label": "Terracotta"},
                    {"value": "weathered_wood", "label": "Weathered Wood"},
                ]
            },
            {
                "key": "roof_style",
                "label": "Roof Style",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "dimensional", "label": "Dimensional/Architectural"},
                    {"value": "3_tab", "label": "3-Tab"},
                    {"value": "standing_seam", "label": "Standing Seam"},
                    {"value": "spanish", "label": "Spanish Tile"},
                ]
            },
        ]

    def get_pipeline_steps(self) -> List[str]:
        return ['cleanup', 'roof_insertion', 'quality_check']

    def get_prompts_module(self):
        from . import prompts
        return prompts

    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'description': 'Preparing image',
                'progress_weight': 20
            },
            'roof_insertion': {
                'type': 'insertion',
                'feature_name': 'roof',
                'scope_key': 'roof',
                'description': 'Visualizing Roof',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Final Review',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
```

**Step 4: Write prompts.py**

Create `api/tenants/roofs/prompts.py`:

```python
"""Roof Visualizer AI prompts.

Prompts for visualizing roof replacements on homes.
"""


def get_cleanup_prompt() -> str:
    """Return cleanup prompt for roof visualization."""
    return """Analyze this image for roof visualization preparation.

Clean the image by:
- Ensuring clear visibility of the entire roof surface
- Removing any temporary items (tarps, equipment)
- Maintaining natural lighting and sky conditions

PRESERVE EXACTLY:
- House structure and architecture
- Existing gutters and trim
- Chimneys, vents, and skylights
- Surrounding landscape

Output the cleaned image maintaining original perspective."""


def get_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generic insertion prompt interface for pipeline_registry.

    Args:
        feature_type: 'roof' (primary feature for this vertical)
        options: Dict with roof_material, roof_color, roof_style
    """
    roof_material = options.get('roof_material', 'asphalt_shingle')
    roof_color = options.get('roof_color', 'charcoal')
    roof_style = options.get('roof_style', 'dimensional')

    # Format for display
    material_display = roof_material.replace('_', ' ').title()
    color_display = roof_color.replace('_', ' ').title()
    style_display = roof_style.replace('_', ' ').title()

    return f"""Photorealistic roof replacement visualization.

Replace the existing roof with new {material_display} roofing.

Roof specifications:
- Material: {material_display}
- Color: {color_display}
- Style: {style_display}

Render requirements:
- Realistic texture matching the material type
- Natural weathering and dimension appropriate to material
- Proper shadow patterns from roof planes
- Seamless integration at edges, ridges, and valleys
- Maintain existing roof geometry and pitch
- Preserve all vents, chimneys, and skylights
- Natural color variation (not perfectly uniform)

Do not modify house structure, only the roof surface material."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Return quality check prompt for roof visualization."""
    return """Review this roof visualization for quality and realism.

Compare Image 1 (reference) with Image 2 (final result).

Check for:
- Realistic roof texture and material appearance
- Proper coverage of entire roof surface
- Natural color variation (not artificially uniform)
- Correct shadow patterns
- Preserved roof geometry and pitch
- All vents, chimneys, skylights intact
- No floating or disconnected elements

Rate quality 0.0 to 1.0:
- Below 0.5: Major issues (wrong material, incomplete coverage)
- Below 0.7: Minor issues (slight texture problems)
- Above 0.7: Good quality visualization

Return ONLY a JSON object:
{
    "score": float,
    "reason": "string"
}"""
```

**Step 5: Write test for prompts**

Create `api/tenants/roofs/tests/test_prompts.py`:

```python
"""Test Roofs prompts module."""
import pytest
from api.tenants.roofs import prompts


def test_get_insertion_prompt():
    result = prompts.get_insertion_prompt('roof', {
        'roof_material': 'asphalt_shingle',
        'roof_color': 'charcoal'
    })
    assert isinstance(result, str)
    assert 'asphalt' in result.lower()
```

**Step 6: Run tests**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/roofs/tests/ -v`

Expected: PASS

**Step 7: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/roofs/
git commit -m "feat(roofs): add roof visualizer vertical

Adds new roofs vertical with:
- Materials: asphalt shingle, metal, clay/concrete tile, slate, wood shake
- Colors: charcoal, black, brown, gray, terracotta, weathered wood
- Styles: dimensional, 3-tab, standing seam, spanish

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 8: Register Roofs Tenant

**Files:**
- Modify: `api/tenants/__init__.py`

**Step 1: Update __init__.py**

Add import after WindowsTenantConfig:
```python
from .roofs.config import RoofsTenantConfig
```

Add registration at end:
```python
register_tenant(RoofsTenantConfig())
```

**Step 2: Run full test suite**

Run: `cd /home/reid/testhome/boss-security-visualizer && source venv/bin/activate && python3 -m pytest api/tenants/ -v`

Expected: All PASS

**Step 3: Commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add api/tenants/__init__.py
git commit -m "feat(tenants): register roofs vertical

Roofs tenant now available via ACTIVE_TENANT=roofs

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: Integration Testing

### Task 9: Verify All Tenants Work

**Step 1: Run complete test suite**

```bash
cd /home/reid/testhome/boss-security-visualizer
source venv/bin/activate
python3 -m pytest api/ -v --tb=short
```

Expected: All tests pass

**Step 2: Manual smoke test each tenant**

```bash
# Test Boss
ACTIVE_TENANT=boss python3 manage.py shell -c "from api.tenants import get_tenant_config; print(get_tenant_config().display_name)"
# Expected: Boss Security Screens

# Test Windows
ACTIVE_TENANT=windows python3 manage.py shell -c "from api.tenants import get_tenant_config; print(get_tenant_config().display_name)"
# Expected: Window Visualizer

# Test Roofs
ACTIVE_TENANT=roofs python3 manage.py shell -c "from api.tenants import get_tenant_config; print(get_tenant_config().display_name)"
# Expected: Roof Visualizer
```

**Step 3: Final commit**

```bash
cd /home/reid/testhome/boss-security-visualizer
git add .
git commit -m "feat: complete multi-vertical support

Summary:
- Refactored pipeline_registry to use generic get_insertion_prompt()
- Added windows vertical (window types, frames, glass, grids)
- Added roofs vertical (materials, colors, styles)
- All verticals share core infrastructure
- Non-specific improvements flow to all verticals automatically

Testing:
- ACTIVE_TENANT=windows python3 manage.py runserver 8001
- ACTIVE_TENANT=roofs python3 manage.py runserver 8002

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] `python3 -m pytest api/` - All tests pass
- [ ] Boss tenant still works: `ACTIVE_TENANT=boss python3 manage.py runserver`
- [ ] Windows tenant works: `ACTIVE_TENANT=windows python3 manage.py runserver 8001`
- [ ] Roofs tenant works: `ACTIVE_TENANT=roofs python3 manage.py runserver 8002`
- [ ] No hardcoded `get_screen_insertion_prompt` or `get_pool_insertion_prompt` in pipeline_registry.py
- [ ] Each tenant has `get_insertion_prompt()` in its prompts.py

---

## Rollback Plan

If issues occur:

1. **Revert pipeline_registry.py:**
   ```bash
   git checkout HEAD~1 -- api/services/pipeline_registry.py
   ```

2. **Remove new tenants:**
   ```bash
   rm -rf api/tenants/windows api/tenants/roofs
   git checkout HEAD~1 -- api/tenants/__init__.py
   ```

3. **Remove adapters from existing tenants:**
   ```bash
   git checkout HEAD~1 -- api/tenants/boss/prompts.py api/tenants/pools/prompts.py
   ```
