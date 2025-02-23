# src/pymock/cli.py
import argparse
import sys

from pymock.app import create_app
from pymock.config.loader import get_config
from pymock.server.cache import cache
from pymock.server.templates.handler import TemplateHandler


def clear_all_caches(app=None) -> None:
    """
    Clears all caches used by PyMock.

    Args:
        app: Optional Flask app instance; if provided, ensures cache is initialized.
    """
    # If app is provided and cache isn't initialized, bind it
    if app is not None and cache.app is None:
        cache.init_app(app)

    # Clear Flask-Caching cache if initialized
    if cache.app is not None and cache.cache is not None:
        cache.clear()
        print("Flask-Caching cache cleared.")  # noqa: T201
    else:
        print("Flask-Caching cache not initialized; skipping.")  # noqa: T201

    # Clear Jinja2 template cache
    TemplateHandler.clear_cache()
    print("Jinja2 template cache cleared.")  # noqa: T201


def run_server(config_path: str, clear_cache: bool = False) -> None:  # noqa: FBT001, FBT002
    """
    Runs the PyMock server with the specified configuration file.

    Args:
        config_path: Path to the YAML configuration file.
        clear_cache: If True, clears all caches before starting the server.
    """
    config = get_config(config_path)
    endpoints_config = config.get("endpoints", [])
    server_config = config.get("server", {})

    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 5000)

    app = create_app(endpoints_config)

    if clear_cache:
        clear_all_caches(app)

    app.run(host=host, port=port, debug=True, threaded=True)


def main() -> None:
    """Parses command-line arguments and starts the PyMock server."""
    parser = argparse.ArgumentParser(
        description="PyMock: A versatile mock API server.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "config",
        type=str,
        help="Path to the configuration YAML file",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all caches (Flask-Caching and Jinja2 templates) before running",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="PyMock 0.1.0",  # Replace with dynamic version if needed
    )

    args = parser.parse_args()
    try:
        run_server(args.config, clear_cache=args.clear_cache)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
