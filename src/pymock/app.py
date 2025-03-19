# src/pymock/app.py
from typing import Any

from flask import Flask

from pymock.config.loader import get_config
from pymock.server.create_endpoint_blueprint import create_endpoint_blueprint

MAX_PORT_NUMBER = 65535  # Maximum valid TCP/UDP port number


def create_app(endpoint_configs: list[dict[str, Any]]) -> Flask:
    """
    Factory function to create and configure the Flask application.

    Args:
        endpoint_configs: List of endpoint configurations for routing.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__, template_folder="templates")
    blueprint = create_endpoint_blueprint(endpoint_configs)
    app.register_blueprint(blueprint)
    return app


if __name__ == "__main__":
    config = get_config("config.yaml")
    endpoints_config = config.get("endpoints", [])
    server_config = config.get("server", {})

    host = server_config.get("host", "127.0.0.1")
    port = server_config.get("port", 5000)
    if not isinstance(port, int) or port < 0 or port > MAX_PORT_NUMBER:
        error_msg = f"Invalid port number: {port}"
        raise ValueError(error_msg)

    app = create_app(endpoints_config)
    app.run(host=host, port=port, debug=False, threaded=True)
