"""Test Roofs prompts module."""
import pytest
from api.tenants.roofs import prompts


def test_get_cleanup_prompt():
    result = prompts.get_cleanup_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_insertion_prompt():
    result = prompts.get_insertion_prompt('roof', {
        'roof_material': 'asphalt_shingle',
        'roof_color': 'charcoal'
    })
    assert isinstance(result, str)
    assert 'asphalt' in result.lower()


def test_get_quality_check_prompt():
    result = prompts.get_quality_check_prompt({'roof': True})
    assert isinstance(result, str)
    assert len(result) > 0
