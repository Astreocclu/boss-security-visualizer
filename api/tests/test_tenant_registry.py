"""Tests for tenant registry system."""
import unittest
from django.test import TestCase, override_settings

from api.tenants import (
    get_tenant_config, 
    get_tenant_prompts, 
    clear_cache,
    register_tenant
)
from api.tenants.boss.config import BossTenantConfig


class TenantRegistryTest(TestCase):
    
    def setUp(self):
        clear_cache()
    
    def test_boss_tenant_registered(self):
        """Boss tenant should be auto-registered."""
        config = get_tenant_config('boss')
        self.assertEqual(config.tenant_id, 'boss')
    
    def test_default_tenant_is_boss(self):
        """Default active tenant should be Boss."""
        config = get_tenant_config()
        self.assertEqual(config.tenant_id, 'boss')
    
    def test_mesh_choices_not_empty(self):
        """Mesh choices should be populated."""
        config = get_tenant_config()
        choices = config.get_mesh_choices()
        self.assertGreater(len(choices), 0)
        self.assertIn(('12x12', '12x12 Standard'), choices)
    
    def test_prompts_module_has_required_functions(self):
        """Prompts module should have all required functions."""
        prompts = get_tenant_prompts()
        self.assertTrue(hasattr(prompts, 'get_cleanup_prompt'))
        self.assertTrue(hasattr(prompts, 'get_screen_insertion_prompt'))
        self.assertTrue(hasattr(prompts, 'get_quality_check_prompt'))
    
    def test_unknown_tenant_raises_error(self):
        """Unknown tenant ID should raise ValueError."""
        with self.assertRaises(ValueError):
            get_tenant_config('nonexistent')


class PromptParityTest(TestCase):
    """Verify tenant prompts match original prompts exactly."""
    
    def test_cleanup_prompt_parity(self):
        """Cleanup prompt should match original."""
        from api.visualizer import prompts as original
        from api.tenants.boss import prompts as tenant
        
        self.assertEqual(
            original.get_cleanup_prompt(),
            tenant.get_cleanup_prompt()
        )
    
    def test_screen_insertion_prompt_parity(self):
        """Screen insertion prompt should match original."""
        from api.visualizer import prompts as original
        from api.tenants.boss import prompts as tenant
        
        test_cases = [
            ('windows', {'color': 'Black', 'mesh_type': 'Standard'}),
            ('patio enclosure', {'color': 'Dark Bronze', 'mesh_type': 'privacy'}),
            ('entry doors', {'color': 'Stucco', 'mesh_type': 'solar'}),
        ]
        
        for feature_type, options in test_cases:
            with self.subTest(feature_type=feature_type):
                self.assertEqual(
                    original.get_screen_insertion_prompt(feature_type, options),
                    tenant.get_screen_insertion_prompt(feature_type, options)
                )
    
    def test_quality_check_prompt_parity(self):
        """Quality check prompt should match original."""
        from api.visualizer import prompts as original
        from api.tenants.boss import prompts as tenant
        
        test_scopes = [
            None,
            {'patio': True},
            {'windows': False},
            {'patio': True, 'windows': False, 'doors': True},
        ]
        
        for scope in test_scopes:
            with self.subTest(scope=scope):
                self.assertEqual(
                    original.get_quality_check_prompt(scope),
                    tenant.get_quality_check_prompt(scope)
                )
