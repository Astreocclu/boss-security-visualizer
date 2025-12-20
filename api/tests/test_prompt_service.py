"""
Tests for api/services/prompt_service.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase

from api.services.prompt_service import (
    get_prompt,
    create_prompt_override,
    rollback_prompt_override,
)
from api.models import PromptOverride


class TestGetPrompt(TestCase):
    """Tests for get_prompt function."""

    @patch('api.services.prompt_service.get_tenant_config')
    @patch('api.services.prompt_service.PromptOverride.objects')
    def test_get_prompt_uses_db_override_when_exists(self, mock_override_objects, mock_get_config):
        """Should use DB override when one exists."""
        mock_config = Mock()
        mock_config.tenant_id = 'boss'
        mock_get_config.return_value = mock_config

        mock_override = Mock()
        mock_override.prompt_text = "Override prompt text"
        mock_override.version = 1
        mock_override_objects.filter.return_value.order_by.return_value.first.return_value = mock_override

        result = get_prompt('cleanup', tenant_id='boss')

        assert result == "Override prompt text"

    @patch('api.services.prompt_service.get_tenant_config')
    @patch('api.services.prompt_service.PromptOverride.objects')
    def test_get_prompt_falls_back_to_code_default(self, mock_override_objects, mock_get_config):
        """Should fall back to code default when no DB override."""
        mock_prompts = Mock()
        mock_prompts.get_cleanup_prompt.return_value = "Code default prompt"

        mock_config = Mock()
        mock_config.tenant_id = 'boss'
        mock_config.get_prompts_module.return_value = mock_prompts
        mock_config.get_step_config.return_value = {'type': 'cleanup'}
        mock_get_config.return_value = mock_config

        # No DB override
        mock_override_objects.filter.return_value.order_by.return_value.first.return_value = None

        result = get_prompt('cleanup', tenant_id='boss')

        assert result == "Code default prompt"
        mock_prompts.get_cleanup_prompt.assert_called_once()

    @patch('api.services.prompt_service.get_tenant_config')
    @patch('api.services.prompt_service.PromptOverride.objects')
    def test_get_prompt_insertion_type(self, mock_override_objects, mock_get_config):
        """Should call get_screen_insertion_prompt for insertion type."""
        mock_prompts = Mock()
        mock_prompts.get_screen_insertion_prompt.return_value = "Install screens on doors"

        mock_config = Mock()
        mock_config.tenant_id = 'boss'
        mock_config.get_prompts_module.return_value = mock_prompts
        mock_config.get_step_config.return_value = {
            'type': 'insertion',
            'feature_name': 'entry doors'
        }
        mock_get_config.return_value = mock_config

        # No DB override
        mock_override_objects.filter.return_value.order_by.return_value.first.return_value = None

        result = get_prompt('doors', tenant_id='boss', color='Black')

        mock_prompts.get_screen_insertion_prompt.assert_called_once()
        assert result == "Install screens on doors"


class TestCreatePromptOverride(TestCase):
    """Tests for create_prompt_override function."""

    def test_create_first_override(self):
        """Should create version 1 override when none exist."""
        # Clean up any existing overrides
        PromptOverride.objects.filter(tenant_id='test', step_name='cleanup').delete()

        override = create_prompt_override(
            tenant_id='test',
            step_name='cleanup',
            prompt_text='Test prompt'
        )

        assert override.version == 1
        assert override.is_active is True
        assert override.prompt_text == 'Test prompt'

        # Cleanup
        override.delete()

    def test_create_increments_version(self):
        """Should increment version number for new overrides."""
        # Clean up and create v1
        PromptOverride.objects.filter(tenant_id='test', step_name='cleanup').delete()

        v1 = create_prompt_override('test', 'cleanup', 'Version 1')
        v2 = create_prompt_override('test', 'cleanup', 'Version 2')

        assert v2.version == 2
        assert v2.is_active is True

        # Previous version should be deactivated
        v1.refresh_from_db()
        assert v1.is_active is False

        # Cleanup
        v1.delete()
        v2.delete()


class TestRollbackPromptOverride(TestCase):
    """Tests for rollback_prompt_override function."""

    def test_rollback_returns_none_when_no_previous(self):
        """Should return None when no previous version to rollback to."""
        PromptOverride.objects.filter(tenant_id='test', step_name='rollback_test').delete()

        create_prompt_override('test', 'rollback_test', 'Only version')

        result = rollback_prompt_override('test', 'rollback_test')

        assert result is None

        # Cleanup
        PromptOverride.objects.filter(tenant_id='test', step_name='rollback_test').delete()

    def test_rollback_activates_previous_version(self):
        """Should deactivate current and activate previous version."""
        PromptOverride.objects.filter(tenant_id='test', step_name='rollback_test').delete()

        v1 = create_prompt_override('test', 'rollback_test', 'Version 1')
        v2 = create_prompt_override('test', 'rollback_test', 'Version 2')

        result = rollback_prompt_override('test', 'rollback_test')

        v1.refresh_from_db()
        v2.refresh_from_db()

        assert result == v1
        assert v1.is_active is True
        assert v2.is_active is False

        # Cleanup
        v1.delete()
        v2.delete()
