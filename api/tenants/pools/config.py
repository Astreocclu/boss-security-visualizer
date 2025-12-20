"""Pool Visualizer tenant configuration."""
from typing import List, Dict, Any
from ..base import BaseTenantConfig


class PoolsTenantConfig(BaseTenantConfig):
    
    @property
    def tenant_id(self) -> str:
        return "pools"
    
    @property
    def display_name(self) -> str:
        return "Pool Visualizer"
    
    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Product categories for Pool Visualizer.
        
        Defines pool-specific configuration options with no security screen references.
        """
        return [
            {
                "key": "pool_shape",
                "label": "Pool Shape",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "rectangle", "label": "Rectangle"},
                    {"value": "freeform", "label": "Freeform"},
                    {"value": "kidney", "label": "Kidney"},
                    {"value": "l_shape", "label": "L-Shape"},
                ]
            },
            {
                "key": "pool_surface",
                "label": "Pool Surface",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "white_plaster", "label": "White Plaster"},
                    {"value": "pebble_tec_blue", "label": "Pebble Tec Blue"},
                    {"value": "pebble_tec_midnight", "label": "Pebble Tec Midnight"},
                ]
            },
            {
                "key": "deck_material",
                "label": "Deck Material",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "travertine", "label": "Travertine"},
                    {"value": "concrete", "label": "Concrete"},
                    {"value": "pavers", "label": "Pavers"},
                ]
            },
            {
                "key": "water_feature",
                "label": "Water Feature",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "none", "label": "None"},
                    {"value": "waterfall", "label": "Waterfall"},
                    {"value": "fountain", "label": "Fountain"},
                    {"value": "infinity_edge", "label": "Infinity Edge"},
                ]
            },
        ]
    
    def get_pipeline_steps(self) -> List[str]:
        """Pipeline steps for pool visualization."""
        return ['cleanup', 'pool_insertion', 'deck_insertion', 'quality_check']
    
    def get_prompts_module(self):
        from . import prompts
        return prompts

    def get_step_config(self, step_name: str) -> Dict[str, Any]:
        configs = {
            'cleanup': {
                'type': 'cleanup',
                'description': 'Preparing image',
                'progress_weight': 20
            },
            'pool_insertion': {
                'type': 'insertion',
                'feature_name': 'pool',
                'scope_key': 'pool',
                'description': 'Adding Pool',
                'progress_weight': 50
            },
            'deck_insertion': {
                'type': 'insertion',
                'feature_name': 'deck',
                'scope_key': 'deck',
                'description': 'Adding Deck',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Final Review',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
