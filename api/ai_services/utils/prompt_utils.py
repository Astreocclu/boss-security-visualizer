"""
Prompt engineering utilities for AI services.
Extracted from openai_provider.py for better code organization.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def optimize_prompt_for_api(prompt: str, max_length: int = 1000) -> str:
    """
    Optimize prompt for API efficiency while preserving key terms.
    
    Args:
        prompt: Original prompt text
        max_length: Maximum prompt length in characters
        
    Returns:
        str: Optimized prompt
    """
    try:
        if len(prompt) <= max_length:
            return prompt
        
        # Key terms to preserve
        key_terms = [
            "security", "lifestyle", "professional", "high-quality", 
            "realistic", "stainless steel", "mesh", "screen", "window"
        ]
        
        # Split into words and keep first portion
        words = prompt.split()
        max_words = max_length // 6  # Rough estimate of words
        
        # Keep first portion of words
        optimized_words = words[:max_words]
        optimized_prompt = " ".join(optimized_words)
        
        # Ensure key terms are included
        for term in key_terms:
            if term not in optimized_prompt.lower() and term in prompt.lower():
                if len(optimized_prompt) + len(term) + 1 <= max_length:
                    optimized_prompt += f" {term}"
        
        logger.info(f"Prompt optimized: {len(prompt)} -> {len(optimized_prompt)} characters")
        return optimized_prompt
        
    except Exception as e:
        logger.error(f"Prompt optimization failed: {str(e)}")
        return prompt[:max_length]  # Fallback truncation


def improve_prompt_based_on_quality(prompt: str, current_quality: float, target_quality: float) -> str:
    """
    Improve prompt based on quality assessment gaps.
    
    Args:
        prompt: Original prompt
        current_quality: Current quality score (0.0-1.0)
        target_quality: Target quality score (0.0-1.0)
        
    Returns:
        str: Improved prompt with quality enhancements
    """
    try:
        quality_gap = target_quality - current_quality
        
        # Add quality enhancement terms based on gap
        enhancements = []
        
        if quality_gap > 0.2:  # Significant improvement needed
            enhancements.extend([
                "ultra-high resolution",
                "professional architectural photography",
                "exceptional detail and clarity",
                "photorealistic quality",
                "perfect lighting and shadows"
            ])
        elif quality_gap > 0.1:  # Moderate improvement needed
            enhancements.extend([
                "high-resolution detail",
                "crisp edges and textures",
                "enhanced contrast",
                "improved lighting effects"
            ])
        else:  # Minor improvement needed
            enhancements.extend([
                "refined details",
                "improved lighting",
                "enhanced clarity"
            ])
        
        # Add enhancements to prompt
        enhanced_prompt = prompt
        for enhancement in enhancements:
            if enhancement not in enhanced_prompt.lower():
                enhanced_prompt += f", {enhancement}"
        
        logger.info(f"Improved prompt for quality gap: {quality_gap:.3f}")
        return enhanced_prompt
        
    except Exception as e:
        logger.error(f"Prompt improvement failed: {str(e)}")
        return prompt


def create_maximum_quality_prompt(base_prompt: str) -> str:
    """
    Create maximum quality prompt for quality enforcement.
    
    Args:
        base_prompt: Original prompt
        
    Returns:
        str: Enhanced prompt with maximum quality terms
    """
    try:
        quality_terms = [
            "ultra-high resolution",
            "professional architectural photography",
            "exceptional detail and clarity",
            "photorealistic quality",
            "perfect lighting and shadows",
            "crisp edges and textures",
            "premium visualization standards",
            "maximum quality optimization"
        ]
        
        enhanced_prompt = base_prompt
        for term in quality_terms:
            if term not in enhanced_prompt.lower():
                enhanced_prompt += f", {term}"
        
        return enhanced_prompt
        
    except Exception as e:
        logger.error(f"Maximum quality prompt creation failed: {str(e)}")
        return base_prompt


def create_reference_enhanced_prompt(base_prompt: str, screen_type: str, references: Dict[str, Any]) -> str:
    """
    Create enhanced prompt using reference image characteristics.
    
    Args:
        base_prompt: Original prompt text
        screen_type: Type of screen for enhancement
        references: Loaded reference data
        
    Returns:
        str: Enhanced prompt with reference-based specifications
    """
    try:
        # Count available references
        ref_counts = {k: len(v) for k, v in references.items() if v}
        total_refs = sum(ref_counts.values())
        
        if total_refs == 0:
            logger.warning(f"No references found for {screen_type}, using standard prompt")
            return base_prompt
        
        logger.info(f"Enhancing prompt with {total_refs} reference images")
        
        # Build reference-enhanced prompt
        enhanced_prompt = base_prompt
        
        # Add reference-based specifications
        reference_specs = []
        
        # Real installation references
        if references.get('real_installs'):
            reference_specs.extend([
                "based on real professional installations",
                "authentic screen mounting and alignment",
                "realistic frame integration with window structures"
            ])
        
        # Fabric/material references
        if references.get('fabric_samples'):
            reference_specs.extend([
                "accurate mesh pattern and texture",
                "realistic material opacity and light filtering",
                "authentic fabric weave appearance"
            ])
        
        # Top tier render references
        if references.get('top_tier_renders'):
            reference_specs.extend([
                "professional architectural visualization quality",
                "precise perspective and dimensional accuracy",
                "high-end rendering standards"
            ])
        
        # Angle variation references
        if references.get('angle_variations'):
            reference_specs.extend([
                "correct perspective alignment with window angles",
                "accurate depth and dimensional representation",
                "proper screen plane orientation"
            ])
        
        # Lighting references
        if references.get('lighting_examples'):
            reference_specs.extend([
                "natural lighting interaction with screen material",
                "realistic shadows and light filtering effects",
                "authentic material reflectance properties"
            ])
        
        # Brand sample references
        if references.get('brand_samples'):
            reference_specs.extend([
                "brand-accurate material specifications",
                "authentic product appearance and finish",
                "manufacturer-standard installation details"
            ])
        
        # Add reference specifications to prompt (limit to top 6)
        if reference_specs:
            enhanced_prompt += f", {', '.join(reference_specs[:6])}"
        
        # Add screen type specific enhancements
        material_specs = get_material_specifications(screen_type)
        if material_specs.get('material_description'):
            enhanced_prompt += f", {material_specs['material_description']}"
        
        # Add technical quality requirements
        enhanced_prompt += ", ultra-high resolution detail, photorealistic quality, professional architectural photography"
        
        logger.info(f"Enhanced prompt length: {len(enhanced_prompt)} characters")
        logger.info(f"Reference specifications added: {len(reference_specs)}")
        
        return enhanced_prompt
        
    except Exception as e:
        logger.error(f"Reference prompt enhancement failed: {str(e)}")
        return base_prompt


def get_material_specifications(screen_type: str) -> Dict[str, str]:
    """
    Get material specifications for different screen types.
    
    Args:
        screen_type: Type of screen ('security', 'lifestyle', 'solar', etc.)
        
    Returns:
        Dict with material specifications
    """
    try:
        specifications = {
            'security': {
                'material_description': 'heavy-duty stainless steel mesh with robust mounting system',
                'mesh_pattern': 'fine security mesh pattern',
                'color': 'charcoal or black frame',
                'opacity': 'high visibility through mesh'
            },
            'lifestyle': {
                'material_description': 'fine mesh fabric for privacy and comfort',
                'mesh_pattern': 'elegant fine weave pattern',
                'color': 'neutral tones matching architecture',
                'opacity': 'balanced privacy and visibility'
            },
            'solar': {
                'material_description': 'UV-blocking solar mesh for energy efficiency',
                'mesh_pattern': 'specialized solar blocking weave',
                'color': 'dark mesh for maximum UV protection',
                'opacity': 'optimized for solar control'
            },
            'environmental': {
                'material_description': 'environmental protection mesh for comfort',
                'mesh_pattern': 'fine environmental mesh pattern',
                'color': 'natural tones',
                'opacity': 'balanced environmental protection'
            },
            'pet_resistant': {
                'material_description': 'durable pet-resistant mesh material',
                'mesh_pattern': 'reinforced mesh pattern',
                'color': 'durable finish',
                'opacity': 'clear visibility with pet protection'
            }
        }
        
        return specifications.get(screen_type, specifications['security'])
        
    except Exception as e:
        logger.error(f"Material specifications lookup failed: {str(e)}")
        return {
            'material_description': 'professional screen material',
            'mesh_pattern': 'standard mesh pattern',
            'color': 'neutral color',
            'opacity': 'balanced visibility'
        }


def create_chatgpt_quality_prompt(base_prompt: str, context: Dict[str, Any]) -> str:
    """
    Create ChatGPT-level quality prompt with advanced engineering.
    
    Args:
        base_prompt: Original prompt
        context: Additional context for enhancement
        
    Returns:
        str: ChatGPT-level enhanced prompt
    """
    try:
        # ChatGPT-level enhancement terms
        quality_enhancements = [
            "professional architectural visualization",
            "photorealistic rendering quality",
            "exceptional detail and clarity",
            "perfect lighting and shadows",
            "accurate material representation",
            "precise perspective and depth",
            "high-end visualization standards"
        ]
        
        # Technical specifications
        technical_specs = [
            "ultra-high resolution detail",
            "crisp edges and textures",
            "natural lighting effects",
            "realistic material properties",
            "accurate color representation"
        ]
        
        # Build enhanced prompt
        enhanced_prompt = base_prompt
        
        # Add quality enhancements
        for enhancement in quality_enhancements[:4]:  # Limit to top 4
            if enhancement not in enhanced_prompt.lower():
                enhanced_prompt += f", {enhancement}"
        
        # Add technical specifications
        for spec in technical_specs[:3]:  # Limit to top 3
            if spec not in enhanced_prompt.lower():
                enhanced_prompt += f", {spec}"
        
        logger.info(f"ChatGPT-level prompt created: {len(enhanced_prompt)} characters")
        return enhanced_prompt
        
    except Exception as e:
        logger.error(f"ChatGPT-level prompt creation failed: {str(e)}")
        return base_prompt
