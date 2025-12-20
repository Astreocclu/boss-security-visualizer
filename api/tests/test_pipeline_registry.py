"""
Tests for api/services/pipeline_registry.py
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from PIL import Image

from api.services.pipeline_registry import (
    cleanup_handler,
    insertion_handler,
    quality_check_handler,
    get_handler,
    register_handler,
    execute_step,
    STEP_HANDLERS,
)


class TestGetHandler:
    """Tests for get_handler function."""

    def test_get_cleanup_handler(self):
        """Should return cleanup_handler for 'cleanup' type."""
        handler = get_handler('cleanup')
        assert handler == cleanup_handler

    def test_get_insertion_handler(self):
        """Should return insertion_handler for 'insertion' type."""
        handler = get_handler('insertion')
        assert handler == insertion_handler

    def test_get_quality_check_handler(self):
        """Should return quality_check_handler for 'quality_check' type."""
        handler = get_handler('quality_check')
        assert handler == quality_check_handler

    def test_get_unknown_handler_returns_none(self):
        """Should return None for unknown step type."""
        handler = get_handler('unknown_step_type')
        assert handler is None


class TestRegisterHandler:
    """Tests for register_handler function."""

    def test_register_custom_handler(self):
        """Should register a custom handler."""
        def custom_handler(step_name, step_config, context):
            return {'custom': True}

        register_handler('custom_type', custom_handler)

        assert get_handler('custom_type') == custom_handler

        # Cleanup
        del STEP_HANDLERS['custom_type']


class TestExecuteStep:
    """Tests for execute_step function."""

    def test_execute_step_missing_type_raises(self):
        """Should raise ValueError if step config missing 'type'."""
        with pytest.raises(ValueError, match="missing 'type'"):
            execute_step('test_step', {}, {})

    def test_execute_step_unknown_type_raises(self):
        """Should raise ValueError if no handler for step type."""
        with pytest.raises(ValueError, match="No handler registered"):
            execute_step('test_step', {'type': 'nonexistent'}, {})


class TestCleanupHandler:
    """Tests for cleanup_handler."""

    def test_cleanup_handler_calls_gemini_edit(self):
        """Should call _call_gemini_edit with cleanup prompt."""
        mock_visualizer = Mock()
        mock_image = Mock(spec=Image.Image)
        mock_clean_image = Mock(spec=Image.Image)
        mock_visualizer._call_gemini_edit.return_value = mock_clean_image

        mock_prompts = Mock()
        mock_prompts.get_cleanup_prompt.return_value = "Clean the image"

        context = {
            'visualizer': mock_visualizer,
            'image': mock_image,
            'prompts': mock_prompts,
        }

        result = cleanup_handler('cleanup', {'type': 'cleanup'}, context)

        mock_prompts.get_cleanup_prompt.assert_called_once()
        mock_visualizer._call_gemini_edit.assert_called_once_with(
            mock_image, "Clean the image", step_name='cleanup'
        )
        assert result['image'] == mock_clean_image
        assert result['clean_image'] == mock_clean_image


class TestInsertionHandler:
    """Tests for insertion_handler."""

    def test_insertion_skips_when_scope_disabled(self):
        """Should skip and return unchanged image when scope not enabled."""
        mock_image = Mock(spec=Image.Image)

        context = {
            'visualizer': Mock(),
            'image': mock_image,
            'prompts': Mock(),
            'scope': {'doors': False},
            'options': {},
        }
        step_config = {
            'type': 'insertion',
            'scope_key': 'doors',
            'feature_name': 'entry doors',
        }

        result = insertion_handler('doors', step_config, context)

        assert result['image'] == mock_image
        context['visualizer']._call_gemini_edit.assert_not_called()

    def test_insertion_executes_when_scope_enabled(self):
        """Should execute insertion when scope is enabled."""
        mock_visualizer = Mock()
        mock_image = Mock(spec=Image.Image)
        mock_result_image = Mock(spec=Image.Image)
        mock_visualizer._call_gemini_edit.return_value = mock_result_image

        mock_prompts = Mock()
        mock_prompts.get_insertion_prompt.return_value = "Install screens"

        context = {
            'visualizer': mock_visualizer,
            'image': mock_image,
            'prompts': mock_prompts,
            'scope': {'doors': True},
            'options': {'color': 'Black'},
        }
        step_config = {
            'type': 'insertion',
            'scope_key': 'doors',
            'feature_name': 'entry doors',
        }

        result = insertion_handler('doors', step_config, context)

        mock_prompts.get_insertion_prompt.assert_called_once_with(
            'entry doors', {'color': 'Black'}
        )
        assert result['image'] == mock_result_image


    def test_insertion_handler_uses_generic_interface(self):
        """insertion_handler must call get_insertion_prompt, not vertical-specific functions."""
        # Create mock prompts module with ONLY generic interface
        mock_prompts = MagicMock()
        mock_prompts.get_insertion_prompt = MagicMock(return_value="Test prompt")
        # Explicitly remove vertical-specific functions
        del mock_prompts.get_screen_insertion_prompt
        del mock_prompts.get_pool_insertion_prompt

        mock_visualizer = MagicMock()
        mock_visualizer._call_gemini_edit = MagicMock(return_value="result_image")

        context = {
            'visualizer': mock_visualizer,
            'image': 'test_image',
            'prompts': mock_prompts,
            'scope': {'windows': True},
            'options': {'color': 'Black'},
        }
        step_config = {
            'type': 'insertion',
            'feature_name': 'windows',
            'scope_key': 'windows',
        }

        result = insertion_handler('windows', step_config, context)

        # Verify generic interface was called
        mock_prompts.get_insertion_prompt.assert_called_once_with('windows', {'color': 'Black'})


class TestQualityCheckHandler:
    """Tests for quality_check_handler."""

    def test_quality_check_returns_score_and_reason(self):
        """Should return score and reason from Gemini JSON response."""
        mock_visualizer = Mock()
        mock_visualizer._call_gemini_json.return_value = {
            'score': 0.95,
            'reason': 'Quality looks good'
        }

        mock_prompts = Mock()
        mock_prompts.get_quality_check_prompt.return_value = "Check quality"

        mock_clean = Mock(spec=Image.Image)
        mock_final = Mock(spec=Image.Image)

        context = {
            'visualizer': mock_visualizer,
            'clean_image': mock_clean,
            'image': mock_final,
            'prompts': mock_prompts,
            'scope': {'doors': True},
        }

        result = quality_check_handler('quality_check', {}, context)

        assert result['score'] == 0.95
        assert result['reason'] == 'Quality looks good'
        mock_visualizer._call_gemini_json.assert_called_once()
