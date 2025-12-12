"""Roof Visualizer tenant configuration."""
from typing import List, Dict, Any
from ..base import BaseTenantConfig


class RoofsTenantConfig(BaseTenantConfig):

    @property
    def tenant_id(self) -> str:
        return "roofs"

    @property
    def display_name(self) -> str:
        return "Roof Visualizer"

    def get_product_schema(self) -> List[Dict[str, Any]]:
        """Product categories for Roof Visualizer."""
        return [
            {
                "key": "roof_material",
                "label": "Roof Material",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "asphalt_shingle", "label": "Asphalt Shingle"},
                    {"value": "metal", "label": "Metal"},
                    {"value": "tile_clay", "label": "Clay Tile"},
                    {"value": "tile_concrete", "label": "Concrete Tile"},
                    {"value": "slate", "label": "Slate"},
                    {"value": "wood_shake", "label": "Wood Shake"},
                ]
            },
            {
                "key": "roof_color",
                "label": "Roof Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "charcoal", "label": "Charcoal"},
                    {"value": "black", "label": "Black"},
                    {"value": "brown", "label": "Brown"},
                    {"value": "gray", "label": "Gray"},
                    {"value": "terracotta", "label": "Terracotta"},
                    {"value": "weathered_wood", "label": "Weathered Wood"},
                ]
            },
            {
                "key": "roof_style",
                "label": "Roof Style",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "dimensional", "label": "Dimensional/Architectural"},
                    {"value": "3_tab", "label": "3-Tab"},
                    {"value": "standing_seam", "label": "Standing Seam"},
                    {"value": "spanish", "label": "Spanish Tile"},
                ]
            },
        ]

    def get_pipeline_steps(self) -> List[str]:
        return ['cleanup', 'roof_insertion', 'quality_check']

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
            'roof_insertion': {
                'type': 'insertion',
                'feature_name': 'roof',
                'scope_key': 'roof',
                'description': 'Visualizing Roof',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Final Review',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
