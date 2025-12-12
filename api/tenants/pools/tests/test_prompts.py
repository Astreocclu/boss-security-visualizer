"""Test Pools prompts module has generic interface."""
import pytest
from api.tenants.pools import prompts


def test_get_insertion_prompt_exists():
    """Pools prompts must expose get_insertion_prompt for pipeline_registry."""
    assert hasattr(prompts, 'get_insertion_prompt')
    assert callable(prompts.get_insertion_prompt)


def test_get_insertion_prompt_returns_string():
    """get_insertion_prompt must return a prompt string."""
    result = prompts.get_insertion_prompt('pool', {'pool_shape': 'rectangle'})
    assert isinstance(result, str)
    assert len(result) > 0
