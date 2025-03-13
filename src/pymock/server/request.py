# src/pymock/server/request.py
from flask import request


class Request:
    """Extracts and stores details from an incoming Flask request."""

    def __init__(self):
        self.method = request.method
        self.url = request.url
        self.path = request.path
        self.headers = dict(request.headers)
        self.query_params = dict(request.args)
        self.body = self._get_body()
        self.cookies = dict(request.cookies)
        self.remote_addr = request.remote_addr
        self.content_type = request.content_type

    def _get_body(self):
        if request.is_json:
            return request.get_json()
        elif request.form:
            return dict(request.form)
        elif request.data:
            return request.data.decode("utf-8")
        return None

    def to_dict(self):
        return {
            "method": self.method,
            "url": self.url,
            "path": self.path,
            "headers": self.headers,
            "query_params": self.query_params,
            "body": self.body,
            "cookies": self.cookies,
            "remote_addr": self.remote_addr,
            "content_type": self.content_type,
        }
