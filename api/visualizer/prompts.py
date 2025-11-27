"""
Boss Security Visualizer - Prompts
----------------------------------
Contains the "Narrative Vibe" prompts and structural definitions.
"""

CLEANUP_SCENE_PROMPT = """
TASK: Cleanse the scene.
1. Remove any existing window screens, bug screens, or bars.
2. Ensure the glass is clear and reflective where appropriate.
3. Remove any visual clutter (dirt, cobwebs) from the window/door frames.
4. CRITICAL: Do NOT alter the architecture of the home. Keep the siding, brick, trim, landscaping, and lighting EXACTLY as is.
5. CRITICAL: Do NOT generate a new house. You are EDITING the existing image.
"""

def get_mesh_physics(mesh_choice="12x12"):
    """
    Returns the physics prompt for the specific mesh choice.
    """
    if mesh_choice == "12x12_american":
        return "Texture: Marine-grade stainless steel mesh. Weave: High-density 12x12 strands per inch. Appearance: Semi-gloss black powder coat. Physics: 75% stronger than standard, subtle moiré pattern."
    elif mesh_choice == "10x10":
        return "Texture: Standard security mesh. Weave: 10x10 strands per inch. Appearance: Matte black."
    else: # Default 12x12 Standard
        return "Texture: Standard security mesh. Weave: 12x12 strands per inch. Appearance: Matte black."

def get_structural_prompt(category):
    """
    Returns the structural narrative for the specific category.
    """
    category = category.lower()
    if 'door' in category:
        return "Install security doors with heavy-duty aluminum frames, 3-point locking mechanisms, and no exterior screws."
    elif 'window' in category:
        return "Fit flush-mounted security screens with 0.035-inch diameter stainless steel mesh."
    elif 'patio' in category:
        return "Enclose the patio with floor-to-ceiling security screens, ensuring high visibility and airflow."
    else:
        # Fallback or default
        return "Fit flush-mounted security screens with 0.035-inch diameter stainless steel mesh."

def get_screen_insertion_prompt(screen_type, color="Black", opacity="95%", mesh_type="12x12"):
    """
    Combines physics and structure into the final prompt.
    """
    # Map screen_type to category for the new prompt logic
    category = "Window"
    if "door" in screen_type.lower():
        category = "Door"
    elif "patio" in screen_type.lower():
        category = "Patio"
        
    physics = get_mesh_physics(mesh_type)
    structure = get_structural_prompt(category)
    
    return f"""
    {physics}
    
    TASK:
    Look at the Reference Image (Second Image). Note the frame thickness, the handle hardware, and the steel mesh texture.
    Inpaint that EXACT product into the opening of the User Image (First Image).
    
    CONFIGURATION:
    Category: {category}
    Type: {screen_type}
    Color: {color}
    Opacity: {opacity}
    
    {structure}

    CONSTRAINTS:
    1. CRITICAL: Do NOT generate a new house. You are EDITING the existing image.
    2. Keep the siding, brick, trim, landscaping, and lighting EXACTLY as is.
    3. Only change the pixels inside the window/door openings to apply the screen and frame.
    """
