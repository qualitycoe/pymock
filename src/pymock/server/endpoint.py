from typing import Any

from flask import Blueprint
from ruleenginex.scenario import Scenario

from pymock.server.request import Request
from pymock.server.response import Response


class Endpoint:
    """Represents an API endpoint with multiple scenarios."""

    def __init__(self, path: str, method: str, scenarios_data: list[dict], default_response: dict[str, Any]):
        self.path = path
        self.method = method.upper()
        self.scenarios = [Scenario(**scenario) for scenario in scenarios_data]
        self.default_response = default_response

    def evaluate_scenarios(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """Finds and returns the first matching scenario response, or the default response."""
        for scenario in self.scenarios:
            if scenario.evaluate(request_data):
                return scenario.get_response()
        return self.default_response

    def register_route(self, blueprint: Blueprint):
        """Registers this endpoint in a Flask Blueprint."""

        def route_handler():
            request_obj = Request()
            request_data = request_obj.to_dict()
            matched_response = self.evaluate_scenarios(request_data)

            return Response(
                status_code=matched_response["status"],
                body=matched_response["data"],
                headers=matched_response.get("headers", {}),
            ).to_flask_response()

        blueprint.add_url_rule(
            self.path, endpoint=f"{self.method}-{self.path}", view_func=route_handler, methods=[self.method]
        )
