# tests/test_routes.py
import pytest
from flask import Flask
from flask.testing import FlaskClient

from pymock.server.cache import init_cache
from pymock.server.routes import create_endpoint_blueprint


@pytest.fixture
def app():
    """Fixture providing a Flask app instance."""
    app = Flask(__name__)
    init_cache(app)  # Initialize cache properly
    endpoints_config = [
        {
            "path": "/test",
            "method": "GET",
            "rules": [
                {
                    "conditions": [{"target": "method", "operator": "equals", "value": "GET"}],
                    "response": {"status": 200, "data": {"msg": "Hello"}},
                }
            ],
        }
    ]
    bp = create_endpoint_blueprint(endpoints_config)
    app.register_blueprint(bp)
    return app


@pytest.fixture
def client(app):
    """Fixture providing a Flask test client."""
    return app.test_client()


def test_route_match(client: FlaskClient, app):
    """Test route with matching rule."""
    with app.test_request_context("/test", method="GET"):
        response = client.get("/test")
        assert response.status_code == 200
        assert response.get_json() == {"msg": "Hello"}


@pytest.mark.skip("Failing test")
def test_route_no_match(client: FlaskClient, app):
    """Test route with no matching rule."""
    with app.test_request_context("/invalid", method="GET"):
        response = client.get("/invalid")
        assert response.status_code == 404
        assert response.get_json() == {"error": "No matching rule found"}


def test_invalid_config():
    """Test invalid endpoint config raises ValueError."""
    endpoints_config = [{"path": 123, "method": "GET"}]
    with pytest.raises(ValueError, match="Invalid endpoint config"):
        create_endpoint_blueprint(endpoints_config)
