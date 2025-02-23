import argparse
import sys

from pymock.app import create_app
from pymock.config.loader import get_config


def run_server(config_path: str) -> None:
    """
    Runs the PyMock server with the specified configuration file.

    Args:
        config_path: Path to the YAML configuration file.
    """
    config = get_config(config_path)
    endpoints_config = config.get("endpoints", [])
    server_config = config.get("server", {})

    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 5000)

    app = create_app(endpoints_config)
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
        "--version",
        action="version",
        version="PyMock 0.1.0",  # Replace with dynamic version if available
    )

    args = parser.parse_args()
    try:
        run_server(args.config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
