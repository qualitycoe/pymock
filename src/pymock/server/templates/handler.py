# src/pymock/server/templates/handler.py
from jinja2 import Environment, FileSystemLoader

from pymock.server.exceptions import TemplateError


class TemplateHandler:
    """Manages Jinja2 template environment and rendering."""

    _env = None

    @classmethod
    def _get_env(cls, templates_dir="templates"):
        if cls._env is None:
            cls._env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
        return cls._env

    @classmethod
    def render(cls, template_name: str, data: dict, templates_dir="templates") -> str:
        try:
            env = cls._get_env(templates_dir)
            template = env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            # B904 + EM102 fix: assign error message before raising
            msg = f"Failed to render template '{template_name}': {e}"
            raise TemplateError(msg) from e
