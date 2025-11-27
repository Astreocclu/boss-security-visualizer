"""
Prompts for ScreenVisualizer
----------------------------
Centralized storage for all AI prompts used in the ScreenVisualizer pipeline.
"""

CLEANUP_SCENE_PROMPT = """
Remove temporary visual noise such as garbage cans, hoses, toys, and loose leaves.
DO NOT remove structural elements like columns, fans, lights, furniture, or concrete pads.
Keep the background pixels locked.
"""

BUILD_OUT_PROMPT = """
Inpaint 4x4 or 6x6 Bronze/Black aluminum posts or headers to create a frame for the opening.
Ensure the frame is flush and suitable for mounting a motorized screen.
"""

SCREEN_INSERTION_PROMPT = """
Inpaint a motorized screen into the opening.
Housing: 5.5" Magnum Housing (Square or Beveled).
Tracks: Side Retention Tracks (Captured Edge) attached to columns.
State: Screen should be depicted 50% deployed (halfway down).
"""

def get_mesh_physics_prompt(mesh_type: str, opacity: str = None, color: str = None) -> str:
    """
    Generate the prompt for mesh texture and physics refinement.
    
    Args:
        mesh_type (str): Type of mesh (solar, privacy, etc.)
        opacity (str, optional): Opacity percentage (e.g., "95").
        color (str, optional): Screen color (e.g., "Black").
        
    Returns:
        str: Formatted prompt.
    """
    # Defaults if not provided
    if not opacity:
        opacity = "90" if mesh_type == "solar" else "99"
    
    if not color:
        color = "black"

    return f"""
    Apply {mesh_type} mesh texture to the screen.
    Color: {color}.
    Opacity: {opacity}%.
    Ensure visible transparency for solar mesh, solid block for privacy mesh.
    """
