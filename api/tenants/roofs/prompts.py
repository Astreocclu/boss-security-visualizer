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
