"""Test Windows prompts module."""
import pytest
from api.tenants.windows import prompts


def test_get_cleanup_prompt():
    result = prompts.get_cleanup_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_insertion_prompt():
    result = prompts.get_insertion_prompt('windows', {
        'window_type': 'double_hung',
        'frame_color': 'white',
        'glass_type': 'clear'
    })
    assert isinstance(result, str)
    assert 'double_hung' in result.lower() or 'double hung' in result.lower()


def test_get_quality_check_prompt():
    result = prompts.get_quality_check_prompt({'windows': True})
    assert isinstance(result, str)
    assert len(result) > 0
