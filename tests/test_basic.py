"""
Basic test to verify pytest setup is working correctly.
"""

def test_basic_setup():
    """Test that pytest is working correctly."""
    assert True

def test_math():
    """Test basic math operations."""
    assert 2 + 2 == 4
    assert 10 - 5 == 5
    assert 3 * 4 == 12

def test_string_operations():
    """Test string operations."""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11
    assert "world" in text
