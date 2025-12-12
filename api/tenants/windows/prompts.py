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
