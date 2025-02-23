# src/pymock/server/exceptions.py


class ConfigError(Exception):
    """Raised when there is an error in the configuration."""


class RuleEvaluationError(Exception):
    """Raised when there is an error during rule evaluation."""


class TemplateError(Exception):
    """Raised when there is an error during template rendering."""
