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
