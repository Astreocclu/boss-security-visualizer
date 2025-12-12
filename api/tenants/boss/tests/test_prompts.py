"""Test Boss prompts module has generic interface."""
import pytest
from api.tenants.boss import prompts


def test_get_insertion_prompt_exists():
    """Boss prompts must expose get_insertion_prompt for pipeline_registry."""
    assert hasattr(prompts, 'get_insertion_prompt')
    assert callable(prompts.get_insertion_prompt)


def test_get_insertion_prompt_returns_string():
    """get_insertion_prompt must return a prompt string."""
    result = prompts.get_insertion_prompt('windows', {'color': 'Black'})
    assert isinstance(result, str)
    assert len(result) > 0
