"""Window Visualizer tenant configuration."""
from typing import List, Dict, Any
from ..base import BaseTenantConfig


class WindowsTenantConfig(BaseTenantConfig):

    @property
    def tenant_id(self) -> str:
        return "windows"

    @property
    def display_name(self) -> str:
        return "Window Visualizer"

    def get_product_schema(self) -> List[Dict[str, Any]]:
        """
        Product categories for Window Visualizer.

        Defines window-specific configuration options.
        """
        return [
            {
                "key": "window_type",
                "label": "Window Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "double_hung", "label": "Double Hung"},
                    {"value": "casement", "label": "Casement"},
                    {"value": "sliding", "label": "Sliding"},
                    {"value": "picture", "label": "Picture Window"},
                    {"value": "bay", "label": "Bay Window"},
                    {"value": "awning", "label": "Awning"},
                ]
            },
            {
                "key": "frame_color",
                "label": "Frame Color",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "white", "label": "White"},
                    {"value": "black", "label": "Black"},
                    {"value": "bronze", "label": "Bronze"},
                    {"value": "almond", "label": "Almond"},
                    {"value": "wood_grain", "label": "Wood Grain"},
                ]
            },
            {
                "key": "glass_type",
                "label": "Glass Type",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "clear", "label": "Clear"},
                    {"value": "low_e", "label": "Low-E"},
                    {"value": "tinted", "label": "Tinted"},
                    {"value": "frosted", "label": "Frosted"},
                ]
            },
            {
                "key": "grid_pattern",
                "label": "Grid Pattern",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "none", "label": "None"},
                    {"value": "colonial", "label": "Colonial"},
                    {"value": "prairie", "label": "Prairie"},
                    {"value": "diamond", "label": "Diamond"},
                ]
            },
        ]

    def get_pipeline_steps(self) -> List[str]:
        """Pipeline steps for window visualization."""
        return ['cleanup', 'window_insertion', 'quality_check']

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
            'window_insertion': {
                'type': 'insertion',
                'feature_name': 'windows',
                'scope_key': 'windows',
                'description': 'Visualizing Windows',
                'progress_weight': 70
            },
            'quality_check': {
                'type': 'quality_check',
                'description': 'Final Review',
                'progress_weight': 90
            }
        }
        return configs.get(step_name, {})
