# File: api/visualizer/prompts.py

"""
Boss Security Visualizer - Prompts
----------------------------------
Simplified, atomic prompts for the Nano Banana Pro pipeline.
Focused on visual descriptions, not physical attributes.
"""

def get_cleanup_prompt():
    """
    Step 1: The Foundation.
    Focus: Clean image and enhance to ideal sunny conditions.
    """
    return """Please clean this image of any debris, furniture, and temporary items.
Make the weather conditions ideal and sunny with clear blue sky.
Keep all permanent structures exactly as they are."""

def get_screen_insertion_prompt(feature_type: str, options: dict):
    """
    Generates a focused inpainting prompt for a specific feature.

    Args:
        feature_type (str): "windows", "patio enclosure", or "entry doors"
        options (dict): Contains 'color', 'mesh_type', etc.
    """
    # Extract options with defaults
    color = options.get('color', 'Black')
    mesh_type = options.get('mesh_type', 'Standard')

    # Map mesh density to visual opacity description
    opacity_desc = "Semi-transparent mesh" # Default
    if "privacy" in mesh_type.lower():
        opacity_desc = "Opaque, solid block"
    elif "standard" in mesh_type.lower():
        opacity_desc = "Semi-transparent mesh"
    elif "solar" in mesh_type.lower():
        opacity_desc = "Tinted transparency"

    base_prompt = f"Photorealistic inpainting. Install {color} security screens on the {feature_type}. Render the screen material as a heavy-duty {color} mesh with {opacity_desc}. Maintain flush mounting frames. Ensure lighting and shadows interact naturally with the new mesh texture."

    if feature_type == "patio enclosure":
        # Add dimensional analysis for logging - Gemini will output this in TEXT response
        base_prompt += """

In your text response, state EXACTLY:
- OPENING WIDTH: [X] feet
- MULLION COUNT: [Y]
- POSITIONS: [list]"""
        base_prompt += " IMPORTANT: Install visible vertical aluminum structural mullions (support posts) every 5 feet across the screen span - these mullions are essential and must be clearly visible."
        base_prompt += " Focus EXCLUSIVELY on enclosing the open patio/porch areas. Leave all standard windows and other openings in their original state."

    return base_prompt

def get_quality_check_prompt(scope: dict = None):
    """
    Generates a prompt for the AI to evaluate the realism and consistency of the generated image compared to the reference.
    """
    base_prompt = """
    You are a Quality Control AI.
    Image 1 is the REFERENCE (Clean State).
    Image 2 is the FINAL RESULT (With Screens).

    Compare them and check for "hallucinations":
    1. Did windows turn into doors?
    2. Did new structural elements appear that weren't in the reference?
    3. Is the perspective consistent?
    """

    if scope and scope.get('patio'):
        base_prompt += """
    CONTEXT: The user requested a Patio Enclosure.
    - Allow filling of existing structural voids/openings with screen material.
    - Do NOT allow the removal or conversion of existing glass windows or load-bearing walls.
    """
    else:
        base_prompt += """
    CONTEXT: Standard Screen Installation.
    - Any structural change (window->door, new opening) is a HALLUCINATION.
    """

    if scope and not scope.get('windows'):
        base_prompt += """
    NEGATIVE CONSTRAINT: Windows were NOT requested.
    - Verify that standard windows remain untouched/unscreened.
    - If unrequested window screens are present, score MUST be below 0.5.
    """

    base_prompt += """
    Rate the quality on a scale of 0.0 to 1.0.
    - If forbidden hallucinations exist, score MUST be below 0.5.
    - If photorealism is poor, score MUST be below 0.7.

    Return ONLY a JSON object with the following structure:
    {
        "score": float,
        "reason": "string"
    }
    """
    return base_prompt
