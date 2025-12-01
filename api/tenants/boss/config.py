"""Boss Security Screens tenant configuration."""
from typing import List, Tuple, Dict, Any
from ..base import BaseTenantConfig

class BossTenantConfig(BaseTenantConfig):
    
    @property
    def tenant_id(self) -> str:
        return "boss"
    
    @property
    def display_name(self) -> str:
        return "Boss Security Screens"
    
    def get_mesh_choices(self) -> List[Tuple[str, str]]:
        return [
            ('10x10', '10x10 Standard'),
            ('12x12', '12x12 Standard'),
            ('12x12_american', '12x12 American'),
        ]
    
    def get_frame_color_choices(self) -> List[Tuple[str, str]]:
        return [
            ('Black', 'Black'),
            ('Dark Bronze', 'Dark Bronze'),
            ('Stucco', 'Stucco'),
            ('White', 'White'),
            ('Almond', 'Almond'),
        ]
    
    def get_mesh_color_choices(self) -> List[Tuple[str, str]]:
        return [
            ('Black', 'Black (Recommended)'),
            ('Stucco', 'Stucco'),
            ('Bronze', 'Bronze'),
        ]
    
    def get_opacity_choices(self) -> List[Tuple[str, str]]:
        return [
            ('80', '80%'),
            ('95', '95%'),
            ('99', '99%'),
        ]
    
    def get_pipeline_steps(self) -> List[str]:
        # Order: doors → windows → patio (patio last as largest envelope)
        return ['cleanup', 'doors', 'windows', 'patio', 'quality_check']
    
    def get_prompts_module(self):
        from . import prompts
        return prompts

    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'description': 'Cleaning',
                'progress_weight': 30
            },
            'patio': {
                'type': 'insertion',
                'feature_name': 'patio enclosure',
                'scope_key': 'patio',
                'description': 'Building Patio',
                'progress_weight': 50
            },
            'windows': {
                'type': 'insertion',
                'feature_name': 'windows',
                'scope_key': 'windows',
                'description': 'Building Windows',
                'progress_weight': 60
            },
            'doors': {
                'type': 'insertion',
                'feature_name': 'entry doors',
                'scope_key': 'doors',
                'description': 'Building Doors',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Checking Quality',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
