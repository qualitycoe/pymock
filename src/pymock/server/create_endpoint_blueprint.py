# src/pymock/server/create_endpoint_blueprint.py

import logging
from collections.abc import Callable

from flask import Blueprint, Response, jsonify, make_response, request
from jinja2 import Environment
from ruleenginex.scenario import Scenario

from pymock.server.request import Request
from pymock.server.templates.handler import TemplateHandler

logger = logging.getLogger(__name__)


def create_endpoint_blueprint(endpoints_config: list[dict]) -> Blueprint:
    """
    Creates a Flask Blueprint with dynamic endpoints. Each endpoint can define multiple
    scenarios, and the first scenario whose rules match is chosen. Also supports:
      - Inline Jinja2 expressions in the 'data' portion of responses
      - Caching with a custom key function
    """

    logger.debug("Loading endpoints config: %s", endpoints_config)

    mock_bp = Blueprint("mock_blueprint", __name__)
    jinja_env = Environment(autoescape=True)  # For inline `{{}}` expressions

    def _render_data(data: dict) -> dict:
        """
        Render Jinja2 expressions in dictionary string values.
        If the rendered result looks like a list (e.g. "[1, 2, 3]"), try parsing it as a list.
        """
        rendered_data = {}
        for key, value in data.items():
            if isinstance(value, str) and "{{" in value:
                template = jinja_env.from_string(value)
                rendered_value = template.render(request=request)
                # Optionally convert "[...]" to a list
                if rendered_value.startswith("[") and rendered_value.endswith("]"):
                    try:
                        import ast

                        rendered_data[key] = ast.literal_eval(rendered_value)
                    except (ValueError, SyntaxError):
                        rendered_data[key] = rendered_value
                else:
                    rendered_data[key] = rendered_value
            else:
                rendered_data[key] = value
        return rendered_data

    def route_handler_factory(scenarios: list[Scenario]) -> Callable[..., Response]:
        """
        Creates a route handler that:
          1. Checks each scenario in order, returning the first that matches.
          2. Renders inline Jinja2 in 'data'.
          3. Optionally uses a Jinja2 template (if 'template' is defined in scenario response).
          4. Returns JSON or rendered template response.
        """

        def route_handler(**kwargs) -> Response:
            request_obj = Request()
            request_data = request_obj.to_dict()

            for scenario in scenarios:
                logger.debug("Checking scenario: %s", scenario.scenario_name)
                if scenario.evaluate(request_data):
                    logger.debug("Scenario matched: %s", scenario.scenario_name)
                    scenario_resp = scenario.get_response()
                    status_code = scenario_resp.get("status", 200)
                    data = scenario_resp.get("data", {})
                    template_name = scenario_resp.get("template")

                    # Render dynamic expressions in 'data'
                    rendered_data = _render_data(data)

                    if template_name:
                        # If a Jinja2 template is specified, use TemplateHandler
                        template_data = {**rendered_data, **kwargs}
                        rendered_content = TemplateHandler.render(template_name, template_data)
                        return make_response(rendered_content, status_code)
                    else:
                        # Otherwise, return JSON
                        return make_response(jsonify(rendered_data), status_code)

            # If no scenario matched, return 404 or a default
            return make_response(jsonify({"error": "No matching scenario"}), 404)

        return route_handler

    # Loop over each endpoint in the config and build a route with scenario-based logic
    for endpoint in endpoints_config:
        path = endpoint["path"]
        method = endpoint["method"].upper()
        scenario_configs = endpoint.get("scenarios", [])

        # Build list of Scenario objects
        scenario_list = [
            Scenario(
                scenario_name=sc.get("scenario_name", "Unnamed"),
                rules=sc.get("rules", []),
                response=sc.get("response", {}),
            )
            for sc in scenario_configs
        ]

        # Register each endpoint with the scenario-based route handler
        mock_bp.add_url_rule(
            path,
            endpoint=f"{method}-{path}",
            view_func=route_handler_factory(scenario_list),
            methods=[method],
        )

    return mock_bp
