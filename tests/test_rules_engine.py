# tests/test_rules_engine.py
import pytest
from flask import Request
from werkzeug.test import EnvironBuilder

from pymock.server.rules_engine import _apply_operator, _extract_property, evaluate_rules


@pytest.fixture
def mock_request():
    """Fixture for a mock Flask request."""
    builder = EnvironBuilder(
        method="GET",
        path="/test/123",
        query_string="key=123&num=42",
        headers={"X-Test": "value"},
        json={"data": "test"},
        environ_base={"HTTP_COOKIE": "session=abc"},
    )
    env = builder.get_environ()
    env["werkzeug.routing_map"] = {"test": {"id": "123"}}  # Simulate route params
    req = Request(env)
    req.view_args = {"id": "123"}  # Set route params
    return req


def test_evaluate_rules_match(mock_request):
    """Test rule evaluation with a matching condition."""
    rules = [
        {
            "conditions": [{"target": "method", "operator": "equals", "value": "GET"}],
            "response": {"status": 200, "data": {"msg": "Success"}},
        }
    ]
    response = evaluate_rules(rules, mock_request)
    assert response == {"status": 200, "data": {"msg": "Success"}}


def test_evaluate_rules_no_match(mock_request):
    """Test rule evaluation with no matching condition."""
    rules = [{"conditions": [{"target": "method", "operator": "equals", "value": "POST"}], "response": {"status": 200}}]
    response = evaluate_rules(rules, mock_request)
    assert response is None


def test_evaluate_rules_invalid_target(mock_request):
    """Test rule evaluation with invalid target."""
    rules = [{"conditions": [{"target": "invalid", "operator": "equals", "value": "GET"}], "response": {"status": 200}}]
    response = evaluate_rules(rules, mock_request)
    assert response is None


def test_evaluate_rules_invert(mock_request):
    """Test rule evaluation with inverted condition."""
    rules = [
        {
            "conditions": [{"target": "method", "operator": "equals", "value": "POST", "invert": True}],
            "response": {"status": 200},
        }
    ]
    response = evaluate_rules(rules, mock_request)
    assert response == {"status": 200}


def test_apply_operator_equals():
    """Test equals operator."""
    assert _apply_operator("test", "equals", "test") is True
    assert _apply_operator("test", "equals", "other") is False


def test_apply_operator_regex():
    """Test regex operator."""
    assert _apply_operator("hello123", "regex", r"\w+\d+") is True
    assert _apply_operator("hello", "regex", r"\d+") is False


# tests/test_rules_engine.py (partial update)
def test_apply_operator_regex_case_insensitive():
    """Test case-insensitive regex operator."""
    from pymock.server.rules_engine import _compile_regex

    _compile_regex.cache_clear()  # Clear LRU cache to avoid stale results
    assert _apply_operator("HELLO123", "regex(i)", r"hello\d+") is True
    assert _apply_operator("hello456", "regex(i)", r"HELLO\d+") is True  # Adjusted to include digits


def test_apply_operator_null():
    """Test null operator."""
    assert _apply_operator(None, "null", None) is True
    assert _apply_operator("value", "null", None) is False


def test_apply_operator_empty_array():
    """Test empty array operator."""
    assert _apply_operator([], "empty array", None) is True
    assert _apply_operator([1, 2], "empty array", None) is False


def test_apply_operator_array_includes():
    """Test array includes operator."""
    assert _apply_operator([1, 2, 3], "array includes", 2) is True
    assert _apply_operator([1, 3], "array includes", 2) is False


def test_apply_operator_valid_json_schema():
    """Test valid JSON schema operator."""
    schema = {"type": "object", "properties": {"data": {"type": "string"}}}
    assert _apply_operator({"data": "test"}, "valid JSON schema", schema) is True
    assert _apply_operator({"data": 123}, "valid JSON schema", schema) is False


def test_extract_property_params(mock_request):
    """Test extracting query params."""
    assert _extract_property(mock_request, "params", "key") == "123"


def test_extract_property_path(mock_request):
    """Test extracting path."""
    assert _extract_property(mock_request, "path", None) == "/test/123"


def test_extract_property_headers(mock_request):
    """Test extracting headers."""
    assert _extract_property(mock_request, "headers", "X-Test") == "value"


def test_extract_property_body(mock_request):
    """Test extracting JSON body."""
    assert _extract_property(mock_request, "body", "data") == "test"


def test_extract_property_number(mock_request):
    """Test extracting number from params."""
    assert _extract_property(mock_request, "number", "num") == 42.0


def test_extract_property_cookies(mock_request):
    """Test extracting cookies."""
    assert _extract_property(mock_request, "cookies", "session") == "abc"


def test_extract_property_route_params(mock_request):
    """Test extracting route params."""
    assert _extract_property(mock_request, "route_params", "id") == "123"


def test_extract_property_jsonpath(mock_request):
    """Test extracting with JSONPath."""
    assert _extract_property(mock_request, "body", "$.data") == ["test"]


def test_extract_property_global_variable(mock_request):
    """Test extracting global variable (not implemented)."""
    assert _extract_property(mock_request, "global_variable", "var") is None


def test_extract_property_data_bucket(mock_request):
    """Test extracting data bucket (not implemented)."""
    assert _extract_property(mock_request, "data_bucket", "bucket") is None


def test_extract_property_invalid(mock_request):
    """Test extracting invalid target."""
    assert _extract_property(mock_request, "unknown", "key") is None
