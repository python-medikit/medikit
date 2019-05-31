from medikit.utils import is_identifier


def test_is_identifier():
    assert is_identifier("") is False
    assert is_identifier("foo") is True
    assert is_identifier("foo_bar") is True
    assert is_identifier("foo bar") is False
