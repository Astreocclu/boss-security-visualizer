"""Abstract base class for tenant configurations."""
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
    
    @abstractmethod
    def get_mesh_choices(self) -> List[Tuple[str, str]]:
        """Return mesh type choices for forms."""
        pass
    
    @abstractmethod
    def get_frame_color_choices(self) -> List[Tuple[str, str]]:
        """Return frame color choices for forms."""
        pass
    
    @abstractmethod
    def get_mesh_color_choices(self) -> List[Tuple[str, str]]:
        """Return mesh color choices for forms."""
        pass
    
    @abstractmethod
    def get_opacity_choices(self) -> List[Tuple[str, str]]:
        """Return opacity choices for forms."""
        pass
    
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
