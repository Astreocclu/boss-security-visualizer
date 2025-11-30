"""Tests for tenant config API endpoint."""
from django.test import TestCase
from rest_framework.test import APIClient


class TenantConfigAPITest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
    
    def test_config_endpoint_accessible(self):
        """Config endpoint should be publicly accessible."""
        response = self.client.get('/api/config/')
        self.assertEqual(response.status_code, 200)
    
    def test_config_contains_required_keys(self):
        """Config response should contain all required keys."""
        response = self.client.get('/api/config/')
        data = response.json()
        
        self.assertIn('tenant_id', data)
        self.assertIn('display_name', data)
        self.assertIn('choices', data)
        self.assertIn('mesh', data['choices'])
        self.assertIn('frame_color', data['choices'])
