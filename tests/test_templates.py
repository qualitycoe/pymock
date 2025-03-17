import pytest

from pymock.server.exceptions import TemplateError
from pymock.server.templates.handler import TemplateHandler


@pytest.fixture
def temp_template(tmp_path):
    """Fixture creating a temporary Jinja2 template directory with a valid template."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    template_file = templates_dir / "test.html"
    with template_file.open("w", encoding="utf-8") as f:
        f.write("Hello {{ name }}!")
    return templates_dir, "test.html"


def test_render_template(temp_template):
    """Test rendering a valid template."""
    templates_dir, template_name = temp_template
    data = {"name": "World"}
    result = TemplateHandler.render(template_name, data, templates_dir)
    assert result == "Hello World!"


def test_template_not_found(temp_template):
    """Test rendering a non-existent template."""
    templates_dir, _ = temp_template
    with pytest.raises(TemplateError, match="Failed to render template 'missing.html'"):
        TemplateHandler.render("missing.html", {}, templates_dir)


def test_render_template_syntax_error(tmp_path):
    """Test rendering with template syntax error."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    error_template = templates_dir / "error.html"
    with error_template.open("w", encoding="utf-8") as f:
        f.write("{% invalid_syntax %}")  # Invalid tag syntax
    with pytest.raises(
        TemplateError,
        match=r"Failed to render template 'error.html':.*Encountered unknown tag 'invalid_syntax'",
    ):
        TemplateHandler.render("error.html", {}, templates_dir)


def test_render_template_empty_data(temp_template):
    """Test rendering with empty data."""
    templates_dir, template_name = temp_template
    result = TemplateHandler.render(template_name, {}, templates_dir)
    assert result == "Hello !"
