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
    
    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Product categories for Boss Security Screens.
        
        Note: No 'opacity' category - mesh density and color determine visibility.
        """
        return [
            {
                "key": "mesh_type",
                "label": "Mesh Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "10x10_standard", "label": "10x10 Standard"},
                    {"value": "12x12_standard", "label": "12x12 Standard"},
                    {"value": "12x12_american", "label": "12x12 American"},
                ]
            },
            {
                "key": "frame_color",
                "label": "Frame Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "black", "label": "Black"},
                    {"value": "dark_bronze", "label": "Dark Bronze"},
                    {"value": "stucco", "label": "Stucco"},
                    {"value": "white", "label": "White"},
                    {"value": "almond", "label": "Almond"},
                ]
            },
            {
                "key": "mesh_color",
                "label": "Mesh Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "black", "label": "Black (Recommended)"},
                    {"value": "stucco", "label": "Stucco"},
                    {"value": "bronze", "label": "Bronze"},
                ]
            },
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
