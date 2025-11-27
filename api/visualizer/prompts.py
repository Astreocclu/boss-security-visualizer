"""
Boss Security Visualizer - Prompts
----------------------------------
Contains the "Narrative Vibe" prompts and structural definitions.
"""

CLEANUP_SCENE_PROMPT = """
TASK: Cleanse the scene.
1. Remove any existing window screens, bug screens, or bars.
2. Remove ALL living things from the scene, including people, pets, and wildlife.
3. Ensure the glass is clear and reflective where appropriate.
4. Remove any visual clutter (dirt, cobwebs, hoses, trash) from the window/door frames and patio areas.
5. CRITICAL: Do NOT alter the architecture of the home. Keep the siding, brick, trim, landscaping, and lighting EXACTLY as is.
6. CRITICAL: Do NOT generate a new house. You are EDITING the existing image.
"""

class PromptFactory:
    """
    Constructs strictly ordered, layered prompts for the Boss Security Visualizer.
    Enforces the sequence: CLEAN -> PATIO -> WINDOWS -> DOORS -> QC.
    """
    
    @staticmethod
    def get_mesh_physics(mesh_choice="12x12"):
        if mesh_choice == "12x12_american":
            return "Texture: Marine-grade stainless steel mesh. Weave: High-density 12x12 strands per inch. Appearance: Semi-gloss black powder coat. Physics: 75% stronger than standard, subtle moiré pattern."
        elif mesh_choice == "10x10":
            return "Texture: Standard security mesh. Weave: 10x10 strands per inch. Appearance: Matte black."
        else: # Default 12x12 Standard
            return "Texture: Standard security mesh. Weave: 12x12 strands per inch. Appearance: Matte black."

    @staticmethod
    def build_prompt(options):
        """
        Constructs the final prompt based on the scope options.
        options: dict containing 'scope' (dict) and other settings like 'mesh_choice', 'frame_color'.
        """
        scope = options.get('scope', {})
        mesh_choice = options.get('mesh_choice', '12x12')
        frame_color = options.get('frame_color', 'Black')
        
        prompt_parts = []
        
        # 1. BASE & CLEAN (The Foundation)
        prompt_parts.append("TASK: Photorealistic architectural visualization of Boss Security Screens products installed on a home.")
        prompt_parts.append(CLEANUP_SCENE_PROMPT.strip())
        
        # 2. PATIO (Background Layer)
        if scope.get('hasPatio'):
            prompt_parts.append(f"""
            STEP: PATIO ENCLOSURE
            - Enclose the covered patio area with "Boss Security Screen" floor-to-ceiling panels.
            - Frame Color: {frame_color}.
            - Mesh: {PromptFactory.get_mesh_physics(mesh_choice)}
            - Structure: Heavy-duty aluminum frames. If wide span (>5ft), install vertical mullions for structural support.
            - Physics: The mesh should slightly darken the area behind it but maintain visibility.
            """)
            
        # 3. WINDOWS (Midground Layer)
        if scope.get('hasWindows'):
            prompt_parts.append(f"""
            STEP: WINDOW SCREENS
            - Install "Boss Security Screen" flush-mounted screens on ALL visible windows.
            - Frame Color: {frame_color}.
            - Mesh: {PromptFactory.get_mesh_physics(mesh_choice)}
            - Detail: 0.035-inch diameter stainless steel mesh.
            - Appearance: Clean, modern look. No bars or grilles. The mesh sits flat and tight.
            """)
            
        # 4. DOORS (Foreground Layer)
        if scope.get('hasDoors'):
            door_type = scope.get('doorType', 'security_door')
            door_desc = "Standard Security Door"
            if door_type == 'french_door':
                door_desc = "Double French Security Doors"
            elif door_type == 'sliding_door':
                door_desc = "Sliding Security Door"
                
            prompt_parts.append(f"""
            STEP: SECURITY DOORS
            - Install {door_desc} on the main entryways.
            - Frame Color: {frame_color}.
            - Mesh: {PromptFactory.get_mesh_physics(mesh_choice)}
            - Hardware: 3-point locking mechanism, heavy-duty hinges.
            - Design: Minimalist, high-security aesthetic.
            """)
            
        # 5. QC (The Vibe Check)
        prompt_parts.append(f"""
        QUALITY CONTROL:
        - PRODUCT: All screens must look like "Boss Security Screen" products (12x12 stainless steel mesh).
        - LIGHTING: Ensure the mesh casts realistic micro-shadows on the glass behind it.
        - CONSISTENCY: All frames must match the requested color ({frame_color}).
        - REALISM: Do not change the house geometry. Only add the screens.
        """)
        
        return "\n\n".join(prompt_parts)

# Legacy support if needed, but PromptFactory is preferred
def get_screen_insertion_prompt(screen_type, is_wide_span=False, color="Black", opacity="95%", mesh_type="12x12"):
    # Fallback to a simple window prompt using the factory if possible, or keep legacy logic.
    # For now, we'll map it to the new factory for consistency.
    options = {
        'scope': {'hasWindows': True}, # Default assumption
        'mesh_choice': mesh_type,
        'frame_color': color
    }
    if 'door' in screen_type.lower():
        options['scope'] = {'hasDoors': True, 'doorType': 'security_door'}
    elif 'patio' in screen_type.lower():
        options['scope'] = {'hasPatio': True}
        
    return PromptFactory.build_prompt(options)
