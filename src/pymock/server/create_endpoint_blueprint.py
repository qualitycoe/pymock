# src/pymock/server/create_endpoint_blueprint.py

import base64
import hashlib
import logging
import os
import random
import uuid
from collections.abc import Callable

from faker import Faker
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

    fake = Faker()

    mock_bp = Blueprint("mock_blueprint", __name__)
    jinja_env = Environment(autoescape=True)
    jinja_env.globals["fake"] = fake
    jinja_env.globals["random"] = random
    jinja_env.globals["b64encode"] = base64.b64encode
    jinja_env.globals["b64decode"] = base64.b64decode
    jinja_env.globals["hashlib"] = hashlib
    jinja_env.globals["env"] = os.environ
    jinja_env.globals["uuid4"] = uuid.uuid4

    for endpoint in endpoints_config:
        _register_endpoint_with_blueprint(mock_bp, endpoint, jinja_env)

    logger.debug("Finished creating blueprint with all endpoints registered.")
    return mock_bp


def _register_endpoint_with_blueprint(mock_bp: Blueprint, endpoint: dict, jinja_env: Environment):
    """
    Registers an endpoint with the given Blueprint.
    """
    path = endpoint["path"]
    method = endpoint["method"].upper()
    scenario_configs = endpoint.get("scenarios", [])

    logger.debug("Registering endpoint: %s %s", method, path)
    logger.debug("Scenarios for endpoint %s: %s", path, scenario_configs)

    scenario_list = _create_scenarios_from_config(scenario_configs)
    route_handler = _create_scenario_based_route_handler(scenario_list, jinja_env)

    mock_bp.add_url_rule(
        path,
        endpoint=f"{method}-{path}",
        view_func=route_handler,
        methods=[method],
    )

    logger.debug("Endpoint %s %s registered successfully.", method, path)


def _create_scenarios_from_config(scenario_configs: list[dict]) -> list[Scenario]:
    """
    Builds a list of Scenario objects from the given scenario configurations.
    """
    logger.debug("Building scenario list from configurations.")
    scenario_list = [
        Scenario(
            scenario_name=sc.get("scenario_name", "Unnamed"),
            rules=sc.get("rules", []),
            response=sc.get("response", {}),
        )
        for sc in scenario_configs
    ]
    logger.debug("Scenario list built with %d scenarios.", len(scenario_list))
    return scenario_list


def _create_scenario_based_route_handler(scenarios: list[Scenario], jinja_env: Environment) -> Callable[..., Response]:
    """
    Creates a route handler that checks each scenario in order, returning the first that matches.
    """
    logger.debug("Creating route handler for scenarios.")

    def route_handler(**kwargs) -> Response:
        logger.debug("Route handler invoked with kwargs: %s", kwargs)
        request_obj = Request()
        request_data = request_obj.to_dict()

        logger.debug("Request data: %s", request_data)

        jinja_env.globals["request"] = request_obj

        for scenario in scenarios:
            logger.debug("Checking scenario: %s", scenario.scenario_name)
            if scenario.evaluate(request_data):
                logger.debug("Scenario matched: %s", scenario.scenario_name)
                return _generate_response_for_matched_scenario(scenario, jinja_env, kwargs)
            else:
                logger.debug("Scenario did not match: %s", scenario.scenario_name)

        logger.debug("No scenario matched for the request.")
        return make_response(jsonify({"error": "No matching scenario"}), 404)

    logger.debug("Route handler created successfully.")
    return route_handler


def _generate_response_for_matched_scenario(scenario: Scenario, jinja_env: Environment, kwargs: dict) -> Response:
    """
    Handles the response for a matched scenario.
    """
    logger.debug("Handling response for matched scenario: %s", scenario.scenario_name)
    scenario_resp = scenario.get_response()
    status_code = scenario_resp.get("status", 200)
    data = scenario_resp.get("data", {})
    template_name = scenario_resp.get("template")

    logger.debug("Scenario response: %s", scenario_resp)
    logger.debug("Rendering data with Jinja2 expressions.")
    rendered_data = _render_jinja_expressions_in_data(data, jinja_env)

    if template_name:
        logger.debug("Using template for response: %s", template_name)
        template_data = {**rendered_data, **kwargs}
        rendered_content = TemplateHandler.render(template_name, template_data)
        logger.debug("Template rendered successfully.")
        return make_response(rendered_content, status_code)
    else:
        logger.debug("Returning JSON response.")
        return make_response(jsonify(rendered_data), status_code)


def _render_jinja_expressions_in_data(data: dict, jinja_env: Environment) -> dict:
    """
    Renders Jinja2 expressions in dictionary string values.
    """
    logger.debug("Rendering data: %s", data)
    rendered_data = {}
    for key, value in data.items():
        if isinstance(value, str) and "{{" in value:
            logger.debug("Rendering Jinja2 expression for key: %s", key)
            rendered_data[key] = _render_and_parse_jinja_value(value, jinja_env)
        else:
            rendered_data[key] = value
    logger.debug("Rendered data: %s", rendered_data)
    return rendered_data


def _render_and_parse_jinja_value(value: str, jinja_env: Environment):
    """
    Renders a Jinja2 expression and optionally converts it to a list if it looks like one.
    """
    logger.debug("Rendering Jinja2 value: %s", value)
    template = jinja_env.from_string(value)
    rendered_value = template.render(request=request)
    if rendered_value.startswith("[") and rendered_value.endswith("]"):
        logger.debug("Rendered value looks like a list: %s", rendered_value)
        try:
            import ast

            parsed_value = ast.literal_eval(rendered_value)
            logger.debug("Successfully parsed rendered value as a list: %s", parsed_value)
            return parsed_value
        except (ValueError, SyntaxError) as e:
            logger.debug("Failed to parse rendered value as a list: %s", e)
            return rendered_value
    logger.debug("Rendered value: %s", rendered_value)
    return rendered_value
