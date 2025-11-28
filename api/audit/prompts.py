def get_audit_prompt():
    """
    Returns the prompt for the Security Audit analysis.
    """
    return """
    You are a Home Security Expert and Auditor. Analyze this image of a home exterior for security vulnerabilities.
    
    Focus on these specific risk factors:
    1. Ground Level Access: Are there windows within 6ft of the ground?
    2. Concealment: Are there windows hidden by dense landscaping (bushes, trees) that could hide an intruder?
    3. Glass Proximity: Is there glass within 40 inches of a door lock (risk of "break and reach")?
    4. Hardware Weakness: Are there visible standard fly screens (which are easily cut)?

    Output your analysis in strict JSON format with the following structure:
    {
        "has_ground_level_access": boolean,
        "has_concealment": boolean,
        "has_glass_proximity": boolean,
        "has_hardware_weakness": boolean,
        "vulnerabilities": [
            {
                "type": "string (e.g., 'Ground Level Window', 'Concealed Entry')",
                "description": "string (brief description of the specific instance)",
                "severity": "string ('High', 'Medium', 'Low')",
                "location": "string (e.g., 'Left window', 'Front door')"
            }
        ],
        "analysis_summary": "string (A professional summary of the home's security state, 2-3 sentences)"
    }
    """
