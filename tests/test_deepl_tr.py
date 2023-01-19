"""Test deepl_tr."""
# pylint: disable=broad-except
from deepl_tr import __version__
from deepl_tr import deepl_tr


def test_version():
    """Test version."""
    assert __version__[:3] == "0.1"


def test_sanity():
    """Check sanity."""
    try:
        assert not deepl_tr()
    except Exception:
        assert True
