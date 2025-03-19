# src/pymock/cli.py
import argparse
import sys

from pymock.app import create_app
from pymock.config.loader import get_config
from pymock.logging_config import setup_logging


def run_server(config_path: str) -> None:
    config = get_config(config_path)
    debug_mode = config.get("debug", False)  # <-- read the 'debug' key
    setup_logging(debug=debug_mode)

    endpoints_config = config.get("endpoints", [])
    server_config = config.get("server", {})

    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 5000)

    app = create_app(endpoints_config)
    app.run(host=host, port=port, debug=debug_mode, threaded=True)


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
        run_server(args.config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
