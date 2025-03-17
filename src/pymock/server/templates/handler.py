# src/pymock/server/templates/handler.py
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from pymock.server.exceptions import TemplateError, TemplateNotFoundError


class TemplateHandler:
    """Manages Jinja2 template environment and rendering."""

    _env = None

    @classmethod
    def _get_env(cls, templates_dir="templates"):
        if cls._env is None:
            cls._env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
        return cls._env

    @classmethod
    def render(cls, template_name: str, data: dict, templates_dir="templates", *, autoescape=True) -> str:
        try:
            env = Environment(loader=FileSystemLoader(templates_dir), autoescape=autoescape)  # noqa: S701
            template = env.get_template(template_name)
            return template.render(**data)
        except TemplateNotFound as e:
            msg = f"Failed to render template '{template_name}': {e}"
            raise TemplateNotFoundError(msg) from e
        except Exception as e:
            msg = f"Failed to render template '{template_name}': {e}"
            raise TemplateError(msg) from e
