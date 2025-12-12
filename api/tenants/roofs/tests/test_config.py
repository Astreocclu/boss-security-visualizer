"""Test Roofs tenant configuration."""
import pytest
from api.tenants.roofs.config import RoofsTenantConfig


def test_tenant_id():
    config = RoofsTenantConfig()
    assert config.tenant_id == "roofs"


def test_display_name():
    config = RoofsTenantConfig()
    assert config.display_name == "Roof Visualizer"


def test_product_schema_has_required_fields():
    config = RoofsTenantConfig()
    schema = config.get_product_schema()

    keys = [cat['key'] for cat in schema]
    assert 'roof_material' in keys
    assert 'roof_color' in keys


def test_pipeline_steps():
    config = RoofsTenantConfig()
    steps = config.get_pipeline_steps()

    assert 'cleanup' in steps
    assert 'roof_insertion' in steps
    assert 'quality_check' in steps
    assert steps[0] == 'cleanup'
    assert steps[-1] == 'quality_check'
