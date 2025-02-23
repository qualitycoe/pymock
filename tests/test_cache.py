# tests/test_cache.py
import pytest
from flask import Flask

from pymock.server.cache import cache, init_cache


@pytest.fixture
def app():
    """Fixture providing a Flask app instance."""
    return Flask(__name__)


def test_init_cache_default(app):
    """Test initializing cache with default config."""
    init_cache(app)
    assert "cache" in app.extensions
    # Verify SimpleCache behavior: it should cache values
    key = "test_key"
    cache.set(key, "test_value")
    assert cache.get(key) == "test_value"


def test_init_cache_custom(app):
    """Test initializing cache with custom config (null cache)."""
    custom_config = {"CACHE_TYPE": "null"}
    init_cache(app, custom_config)
    assert "cache" in app.extensions
    # Verify NullCache behavior: it should not cache
    key = "test_key"
    cache.set(key, "test_value")
    assert cache.get(key) is None
