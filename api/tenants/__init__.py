"""
Tenant Registry - Central point for tenant configuration resolution.

Usage:
    from api.tenants import get_tenant_config, get_tenant_prompts
    
    config = get_tenant_config()  # Returns active tenant config
    prompts = get_tenant_prompts()  # Returns active tenant prompts module
"""
import logging
from typing import Optional, Dict
from django.conf import settings

from .base import BaseTenantConfig
from .boss.config import BossTenantConfig

logger = logging.getLogger(__name__)

# Registry of all available tenants
_TENANT_REGISTRY: Dict[str, BaseTenantConfig] = {}

# Cached active tenant
_active_tenant: Optional[BaseTenantConfig] = None


def register_tenant(config: BaseTenantConfig) -> None:
    """Register a tenant configuration."""
    _TENANT_REGISTRY[config.tenant_id] = config
    logger.info(f"Registered tenant: {config.tenant_id}")


def get_tenant_config(tenant_id: Optional[str] = None) -> BaseTenantConfig:
    """
    Get tenant configuration.
    
    Args:
        tenant_id: Specific tenant ID, or None for active/default tenant
        
    Returns:
        BaseTenantConfig instance
        
    Raises:
        ValueError: If tenant not found
    """
    global _active_tenant
    
    if tenant_id:
        if tenant_id not in _TENANT_REGISTRY:
            raise ValueError(f"Unknown tenant: {tenant_id}")
        return _TENANT_REGISTRY[tenant_id]
    
    # Return cached active tenant
    if _active_tenant:
        return _active_tenant
    
    # Determine active tenant from settings
    active_id = getattr(settings, 'ACTIVE_TENANT', 'boss')
    
    if active_id not in _TENANT_REGISTRY:
        logger.warning(f"Configured tenant '{active_id}' not found, falling back to 'boss'")
        active_id = 'boss'
    
    _active_tenant = _TENANT_REGISTRY[active_id]
    return _active_tenant


def get_tenant_prompts(tenant_id: Optional[str] = None):
    """Get prompts module for tenant."""
    config = get_tenant_config(tenant_id)
    return config.get_prompts_module()


def get_all_tenants() -> Dict[str, BaseTenantConfig]:
    """Get all registered tenants."""
    return _TENANT_REGISTRY.copy()


def clear_cache() -> None:
    """Clear cached active tenant (for testing)."""
    global _active_tenant
    _active_tenant = None


# Auto-register Boss tenant on module load
register_tenant(BossTenantConfig())
