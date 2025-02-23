# src/pymock/server/routes.py
from collections.abc import Callable

from flask import Blueprint, Response, jsonify, make_response, request

from pymock.server.cache import cache
from pymock.server.rules_engine import evaluate_rules
from pymock.server.templates.handler import render_template


def create_endpoint_blueprint(endpoints_config: list[dict]) -> Blueprint:
    """
    Creates a Flask blueprint for endpoints defined in the config.

    Args:
        endpoints_config: List of endpoint configurations with path, method, and optional rules/template.

    Returns:
        A configured Flask Blueprint with dynamic routes.
    """
    mock_bp = Blueprint("mock_blueprint", __name__)

    def _make_cache_key(*args, **kwargs) -> str:  # noqa : ARG001
        """Generates a cache key based on request path and query parameters."""
        # Ignore args/kwargs; use request context for consistency
        query_params = "&".join(f"{k}={v}" for k, v in sorted(request.args.items()))
        return f"{request.path}?{query_params}"

    def _create_route_handler(rules: list[dict], template_name: str | None) -> Callable[[], Response]:
        """Factory function to create cached route handlers."""

        @cache.cached(timeout=60, make_cache_key=_make_cache_key)
        def route_handler(**kwargs) -> Response:  # noqa : ARG001
            """
            Handles requests, evaluates rules, and returns a response.

            Args:
                **kwargs: Route parameters (e.g., 'name' from '/greet/<name>').

            Returns:
                Flask Response with rendered template or JSON data.
            """
            matched_response = evaluate_rules(rules, request)
            if matched_response is None:
                return make_response(jsonify({"error": "No matching rule found"}), 404)

            status_code = matched_response.get("status", 200)
            data = matched_response.get("data", {})

            return (
                make_response(render_template(template_name, data), status_code)
                if template_name
                else make_response(jsonify(data), status_code)
            )

        return route_handler

    for endpoint in endpoints_config:
        path = endpoint["path"]
        method = endpoint["method"].upper()
        template_name = endpoint.get("template")
        rules = endpoint.get("rules", [])

        # Validate endpoint config
        if not isinstance(path, str) or not isinstance(method, str):
            msg = f"Invalid endpoint config: path={path}, method={method}"
            raise ValueError(msg)

        mock_bp.add_url_rule(
            path,
            endpoint=f"{method}-{path}",
            view_func=_create_route_handler(rules, template_name),
            methods=[method],
        )

    return mock_bp
