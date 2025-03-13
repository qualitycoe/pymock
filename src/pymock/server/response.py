from flask import Response as Flask_Response
from flask import jsonify, make_response


class Response:
    """Represents an HTTP response with structured data."""

    def __init__(self, status_code=200, headers=None, body=None, content_type="application/json"):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body
        self.content_type = content_type

    def to_flask_response(self) -> Flask_Response:
        """Converts to a Flask Response object."""
        response = make_response(jsonify(self.body), self.status_code)
        for key, value in self.headers.items():
            response.headers[key] = value
        return response
