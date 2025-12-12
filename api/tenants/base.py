"""Abstract base class for tenant configurations."""
import warnings
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any


class BaseTenantConfig(ABC):
    """Base class all tenant configs must implement."""
    
    @property
    @abstractmethod
    def tenant_id(self) -> str:
        """Unique tenant identifier."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable tenant name."""
        pass
    
    # =========================================================================
    # NEW: Schema-based product configuration
    # =========================================================================
    
    @abstractmethod
    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Return product categories schema for dynamic form rendering.
        
        Returns a list of category definitions matching the frontend schema format:
        [
            {
                "key": "mesh_type",
                "label": "Mesh Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "10x10_standard", "label": "10x10 Standard"},
                    ...
                ]
            },
            ...
        ]
        """
        pass
    
    def get_options_for_category(self, category_key: str) -> List[Tuple[str, str]]:
        """
        Get options for a specific category from the product schema.
        
        Returns list of (value, label) tuples for backwards compatibility
        with legacy choice methods.
        """
        for category in self.get_product_schema():
            if category.get('key') == category_key:
                options = category.get('options', [])
                return [(opt['value'], opt['label']) for opt in options]
        return []
    
    # =========================================================================
    # DEPRECATED: Legacy choice methods - use get_product_schema() instead
    # These are kept for backwards compatibility with serializers/models
    # =========================================================================
    
    def get_mesh_choices(self) -> List[Tuple[str, str]]:
        """
        DEPRECATED: Use get_options_for_category('mesh_type') instead.
        
        Returns mesh type choices for forms.
        """
        warnings.warn(
            "get_mesh_choices() is deprecated. Use get_options_for_category('mesh_type') instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_options_for_category('mesh_type')
    
    def get_frame_color_choices(self) -> List[Tuple[str, str]]:
        """
        DEPRECATED: Use get_options_for_category('frame_color') instead.
        
        Returns frame color choices for forms.
        """
        warnings.warn(
            "get_frame_color_choices() is deprecated. Use get_options_for_category('frame_color') instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_options_for_category('frame_color')
    
    def get_mesh_color_choices(self) -> List[Tuple[str, str]]:
        """
        DEPRECATED: Use get_options_for_category('mesh_color') instead.
        
        Returns mesh color choices for forms.
        """
        warnings.warn(
            "get_mesh_color_choices() is deprecated. Use get_options_for_category('mesh_color') instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_options_for_category('mesh_color')
    
    def get_opacity_choices(self) -> List[Tuple[str, str]]:
        """
        DEPRECATED: Opacity is determined by mesh density/color, not a separate choice.
        
        This method exists only for backwards compatibility. New tenants should
        NOT include an 'opacity' category in their product schema.
        """
        warnings.warn(
            "get_opacity_choices() is deprecated. Opacity is determined by mesh density/color.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_options_for_category('opacity')
    
    # =========================================================================
    # Pipeline configuration - still required
    # =========================================================================
    
    @abstractmethod
    def get_pipeline_steps(self) -> List[str]:
        """Return ordered list of pipeline step identifiers."""
        pass
    
    @abstractmethod
    def get_prompts_module(self):
        """Return the prompts module for this tenant."""
        pass

    @abstractmethod
    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        """
        Return configuration for a specific pipeline step.
        
        Returns dict containing:
            - type: 'cleanup', 'insertion', 'quality_check'
            - feature_name: (for insertion) e.g. 'patio enclosure'
            - scope_key: (for insertion) e.g. 'patio'
            - progress_weight: (optional) int 0-100
            - description: (optional) for progress updates
        """
        pass
