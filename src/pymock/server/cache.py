# src/pymock/server/cache.py
from typing import Any

from flask import Flask
from flask_caching import Cache

# Default cache configuration
DEFAULT_CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",  # In-memory cache, suitable for single-process apps
    "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes default timeout (in seconds)
}

# Initialize cache instance
cache = Cache(config=DEFAULT_CACHE_CONFIG)


def init_cache(app: Flask, custom_config: dict[str, Any] | None = None) -> None:
    """
    Initializes the cache for the Flask app with optional custom configuration.

    Args:
        app: The Flask application instance to bind the cache to.
        custom_config: Optional dictionary to override default cache settings.

    Examples:
        >>> from flask import Flask
        >>> app = Flask(__name__)
        >>> init_cache(app)  # Uses default SimpleCache
        >>> init_cache(app, {"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": "redis://localhost:6379"})
    """
    final_config = DEFAULT_CACHE_CONFIG.copy()
    if custom_config:
        final_config.update(custom_config)
    cache.init_app(app, config=final_config)
