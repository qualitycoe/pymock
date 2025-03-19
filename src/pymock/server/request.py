# src/pymock/server/request.py
import logging

from flask import request

logger = logging.getLogger(__name__)


class Request:
    """Extracts and stores details from an incoming Flask request."""

    def __init__(self):
        self.method = request.method
        self.url = request.url
        self.path = request.path
        self.headers = dict(request.headers)
        self.params = dict(request.args)
        self.body = self._get_body()
        self.cookies = dict(request.cookies)
        self.remote_addr = request.remote_addr
        self.content_type = request.content_type
        logger.debug("Captured Request: method=%s, path=%s, query_params=%s", self.method, self.path, self.params)

    def _get_body(self):
        if request.is_json:
            return request.get_json()
        elif request.form:
            return dict(request.form)
        elif request.data:
            return request.data.decode("utf-8")
        return None

    def to_dict(self):
        data = {
            "method": self.method,
            "url": self.url,
            "path": self.path,
            "headers": self.headers,
            "params": self.params,
            "body": self.body,
            "cookies": self.cookies,
            "remote_addr": self.remote_addr,
            "content_type": self.content_type,
        }

        logger.debug("Request.to_dict => %s", data)

        return data
