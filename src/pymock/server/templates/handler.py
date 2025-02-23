# src/pymock/server/templates/handler.py
from pathlib import Path
from typing import Any

from flask import request
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from pymock.server.exceptions import TemplateError


class TemplateHandler:
    """Manages Jinja2 template environment and rendering."""

    _env: Environment | None = None

    @classmethod
    def _get_env(cls, templates_dir: str | Path = "templates") -> Environment:
        """
        Lazily initializes and returns a Jinja2 Environment singleton.

        Args:
            templates_dir: Directory path containing Jinja2 templates (default: "templates").

        Returns:
            A configured Jinja2 Environment instance.
        """
        if cls._env is None:
            cls._env = Environment(
                loader=FileSystemLoader(templates_dir),
                autoescape=True,
                lstrip_blocks=True,
                trim_blocks=True,
            )
        return cls._env

    @classmethod
    def render(cls, template_name: str, data: dict[str, Any], templates_dir: str | Path = "templates") -> str:
        """
        Renders a Jinja2 template with the provided data.

        Args:
            template_name: Name of the template file (e.g., "index.html").
            data: Dictionary of variables to pass to the template.
            templates_dir: Directory path containing templates (default: "templates").

        Returns:
            Rendered template as a string.

        Raises:
            TemplateError: If the template cannot be found or rendering fails.
        """
        try:
            env = cls._get_env(templates_dir)
            template = env.get_template(template_name)
            template_data = {**data, "request": request}
            return template.render(**template_data)
        except TemplateNotFound as e:
            msg = "Template '{}' not found in '{}'"
            raise TemplateError(msg.format(template_name, templates_dir)) from e
        except Exception as e:
            msg = "Failed to render template '{}': {}"
            raise TemplateError(msg.format(template_name, str(e))) from e

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clears the Jinja2 template cache to reload templates from disk.
        Useful for development or when templates change dynamically.
        """
        env = cls._env
        if env is not None and env.cache is not None:
            env.cache.clear()


# Module-level convenience functions
def render_template(template_name: str, data: dict[str, Any], templates_dir: str | Path = "templates") -> str:
    """Wrapper for TemplateHandler.render, maintaining original API."""
    return TemplateHandler.render(template_name, data, templates_dir)


def clear_template_cache() -> None:
    """Wrapper for TemplateHandler.clear_cache, maintaining original API."""
    TemplateHandler.clear_cache()
