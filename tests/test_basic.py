"""
Basic tests for the Family Rules Client application.
"""

import pytest


def test_basic_math():
    """Test that basic arithmetic works correctly."""
    assert 2 + 2 == 4


def test_string_operations():
    """Test basic string operations."""
    assert "hello" + " " + "world" == "hello world"


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert 2 in test_list


if __name__ == "__main__":
    pytest.main([__file__])
