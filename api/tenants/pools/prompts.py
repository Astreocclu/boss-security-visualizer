"""Pool Visualizer prompts module.

Stub for future implementation. Pool-specific prompts will be added here.
"""


def get_cleanup_prompt() -> str:
    """Return cleanup prompt for pool visualization."""
    return """Analyze this image for pool visualization preparation.
    
Remove any existing pool or water features and prepare the backyard area
for virtual pool insertion. Maintain the natural landscape and architecture."""


def get_pool_insertion_prompt(feature_type: str, options: dict) -> str:
    """Return prompt for inserting pool features.
    
    Args:
        feature_type: 'pool', 'deck', 'water_feature'
        options: Dict with pool_shape, pool_surface, deck_material, water_feature
    """
    pool_shape = options.get('pool_shape', 'rectangle')
    pool_surface = options.get('pool_surface', 'pebble_tec_blue')
    
    return f"""Add a {pool_shape} shaped swimming pool with {pool_surface} finish.
    
The pool should blend naturally with the existing landscape and architecture.
Ensure realistic water reflections and appropriate shadowing."""


def get_quality_check_prompt(scope: dict = None) -> str:
    """Return quality check prompt for pool visualization."""
    return """Review this pool visualization for quality and realism.

Check for:
- Realistic water appearance and reflections
- Proper integration with landscape
- Natural lighting and shadows
- No visual artifacts or inconsistencies"""


def get_insertion_prompt(feature_type: str, options: dict) -> str:
    """
    Generic insertion prompt interface for pipeline_registry.

    Routes to the existing get_pool_insertion_prompt for Pools vertical.
    """
    return get_pool_insertion_prompt(feature_type, options)
