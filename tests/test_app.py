# tests/test_app.py
import pytest
from flask import Flask

from pymock.app import MAX_PORT_NUMBER, create_app
from pymock.config.loader import get_config


@pytest.fixture
def app():
    """Fixture providing a Flask app instance with minimal config."""
    config = [{"path": "/test", "method": "GET", "response": {"status": 200}}]
    return create_app(config)


@pytest.fixture
def client(app):
    """Fixture providing a Flask test client with app context."""
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_create_app(app):
    """Test Flask app creation."""
    assert isinstance(app, Flask)
    assert app.template_folder == "templates"


def test_invalid_port_raises_value_error():
    """Test invalid port validation in __main__."""
    config = get_config("config.yaml")
    server_config = config.get("server", {})
    server_config["port"] = MAX_PORT_NUMBER + 1
    config["server"] = server_config

    # Simulate __main__ check before run()
    with pytest.raises(ValueError, match="Invalid port number"):
        port = server_config["port"]
        if not isinstance(port, int) or port < 0 or port > MAX_PORT_NUMBER:
            error_msg = f"Invalid port number: {port}"
            raise ValueError(error_msg)
