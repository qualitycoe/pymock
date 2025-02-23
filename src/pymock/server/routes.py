from collections.abc import Callable

from flask import Blueprint, Response, jsonify, make_response, request
from jinja2 import Environment

from pymock.server.cache import cache
from pymock.server.rules_engine import evaluate_rules
from pymock.server.templates.handler import render_template


def create_endpoint_blueprint(endpoints_config: list[dict]) -> Blueprint:
    mock_bp = Blueprint("mock_blueprint", __name__)
    jinja_env = Environment(autoescape=True)

    def _make_cache_key(*args, **kwargs) -> str:
        query_params = "&".join(f"{k}={v}" for k, v in sorted(request.args.items()))
        return f"{request.path}?{query_params}"

    def _render_data(data: dict) -> dict:
        """Renders Jinja2 expressions in dictionary values."""
        rendered_data = {}
        for key, value in data.items():
            if isinstance(value, str) and "{{" in value:
                template = jinja_env.from_string(value)
                rendered_data[key] = template.render(request=request)
            else:
                rendered_data[key] = value
        return rendered_data

    def _create_route_handler(rules: list[dict], template_name: str | None) -> Callable[[], Response]:
        @cache.cached(timeout=60, make_cache_key=_make_cache_key)
        def route_handler(**kwargs) -> Response:
            matched_response = evaluate_rules(rules, request)
            if matched_response is None:
                return make_response(jsonify({"error": "No matching rule found"}), 404)

            status_code = matched_response.get("status", 200)
            data = matched_response.get("data", {})
            rendered_data = _render_data(data)

            if template_name:
                template_data = {**rendered_data, **kwargs}
                return make_response(render_template(template_name, template_data), status_code)
            return make_response(jsonify(rendered_data), status_code)

        return route_handler

    for endpoint in endpoints_config:
        path = endpoint["path"]
        method = endpoint["method"].upper()
        template_name = endpoint.get("template")
        rules = endpoint.get("rules", [])

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
