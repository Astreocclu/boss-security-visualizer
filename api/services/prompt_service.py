"""
Prompt Service - Handles AI prompt resolution with DB override support.

Usage:
    from api.services.prompt_service import get_prompt
    
    prompt = get_prompt('cleanup', tenant_id='boss')
    prompt = get_prompt('doors', tenant_id='boss', feature_name='entry doors', color='Black')
"""
import logging
from typing import Optional, Dict, Any

from api.models import PromptOverride
from api.tenants import get_tenant_config

logger = logging.getLogger(__name__)


def get_prompt(
    step_name: str,
    tenant_id: Optional[str] = None,
    **kwargs
) -> str:
    """
    Get the prompt for a pipeline step.
    
    Priority:
    1. Active DB override (if exists)
    2. Code default from tenant prompts module
    
    Args:
        step_name: Pipeline step name (e.g., 'cleanup', 'doors', 'quality_check')
        tenant_id: Tenant ID (defaults to active tenant)
        **kwargs: Variables for prompt substitution (e.g., feature_name, color)
    
    Returns:
        Formatted prompt string
    """
    config = get_tenant_config(tenant_id)
    actual_tenant_id = config.tenant_id
    
    # Check for DB override first
    override = PromptOverride.objects.filter(
        tenant_id=actual_tenant_id,
        step_name=step_name,
        is_active=True
    ).order_by('-version').first()
    
    if override:
        logger.info(f"Using DB override for {actual_tenant_id}/{step_name} v{override.version}")
        try:
            return override.prompt_text.format(**kwargs)
        except KeyError as e:
            logger.warning(
                f"Prompt override missing variable {e}, falling back to code default"
            )
    
    # Fall back to code prompts
    prompts = config.get_prompts_module()
    
    # Map step names to prompt functions
    prompt_function_map = {
        'cleanup': 'get_cleanup_prompt',
        'quality_check': 'get_quality_check_prompt',
        # Insertion steps use get_screen_insertion_prompt or get_pool_insertion_prompt
    }
    
    step_config = config.get_step_config(step_name)
    step_type = step_config.get('type', '')
    
    if step_type == 'cleanup':
        return prompts.get_cleanup_prompt()
    
    elif step_type == 'quality_check':
        scope = kwargs.get('scope')
        return prompts.get_quality_check_prompt(scope)
    
    elif step_type == 'insertion':
        feature_name = step_config.get('feature_name', step_name)
        options = {
            'color': kwargs.get('color', 'Black'),
            'mesh_type': kwargs.get('mesh_type', 'Standard'),
            **kwargs
        }
        # Try tenant-specific insertion prompt function
        if hasattr(prompts, 'get_screen_insertion_prompt'):
            return prompts.get_screen_insertion_prompt(feature_name, options)
        elif hasattr(prompts, 'get_pool_insertion_prompt'):
            return prompts.get_pool_insertion_prompt(feature_name, options)
        else:
            logger.error(f"No insertion prompt function found for {actual_tenant_id}")
            raise ValueError(f"No insertion prompt handler for tenant {actual_tenant_id}")
    
    else:
        logger.error(f"Unknown step type '{step_type}' for step '{step_name}'")
        raise ValueError(f"Unknown step type: {step_type}")


def create_prompt_override(
    tenant_id: str,
    step_name: str,
    prompt_text: str,
    created_by=None
) -> PromptOverride:
    """
    Create a new prompt override version.
    
    Automatically increments version number and deactivates previous versions.
    """
    # Get the next version number
    latest = PromptOverride.objects.filter(
        tenant_id=tenant_id,
        step_name=step_name
    ).order_by('-version').first()
    
    next_version = (latest.version + 1) if latest else 1
    
    # Deactivate previous versions
    PromptOverride.objects.filter(
        tenant_id=tenant_id,
        step_name=step_name,
        is_active=True
    ).update(is_active=False)
    
    # Create new override
    override = PromptOverride.objects.create(
        tenant_id=tenant_id,
        step_name=step_name,
        prompt_text=prompt_text,
        version=next_version,
        is_active=True,
        created_by=created_by
    )
    
    logger.info(f"Created prompt override: {tenant_id}/{step_name} v{next_version}")
    return override


def rollback_prompt_override(tenant_id: str, step_name: str) -> Optional[PromptOverride]:
    """
    Rollback to the previous prompt override version.
    
    Returns the now-active previous version, or None if no previous version exists.
    """
    overrides = PromptOverride.objects.filter(
        tenant_id=tenant_id,
        step_name=step_name
    ).order_by('-version')[:2]
    
    if len(overrides) < 2:
        logger.warning(f"No previous version to rollback to for {tenant_id}/{step_name}")
        return None
    
    current, previous = overrides[0], overrides[1]
    
    # Deactivate current, activate previous
    current.is_active = False
    current.save()
    
    previous.is_active = True
    previous.save()
    
    logger.info(f"Rolled back {tenant_id}/{step_name} from v{current.version} to v{previous.version}")
    return previous
