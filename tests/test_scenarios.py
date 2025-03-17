import pytest

from pymock.app import create_app


@pytest.fixture
def client():
    endpoints_config = [
        {
            "path": "/hello",
            "method": "POST",  # Change from "GET" to "POST"
            "scenarios": [
                {
                    "scenario_name": "name is John",
                    "rules_data": [
                        {
                            "target": "body",
                            "prop": "$.name",
                            "op": "equals",
                            "value": "John",
                        }
                    ],
                    "response": {
                        "status": 200,
                        "data": {"greeting": "Hello John!"},
                    },
                },
                {
                    "scenario_name": "fallback",
                    "rules_data": [],
                    "response": {
                        "status": 400,
                        "data": {"error": "Not John"},
                    },
                },
            ],
        }
    ]
    app = create_app(endpoints_config)
    with app.test_client() as c:
        yield c


def test_scenario_john_body(client):
    resp = client.post("/hello", json={"name": "John"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["greeting"] == "Hello John!"


def test_scenario_not_john_body(client):
    resp = client.post("/hello", json={"name": "SomeoneElse"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Not John"
