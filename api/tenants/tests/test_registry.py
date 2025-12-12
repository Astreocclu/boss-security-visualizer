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
