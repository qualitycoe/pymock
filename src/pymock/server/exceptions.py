class ConfigError(Exception):
    """Raised when there is an error in the configuration."""


class RuleEvaluationError(Exception):
    """Raised when an error occurs during rule evaluation."""


class TemplateError(Exception):
    """Raised when an error occurs during template rendering."""


class TemplateNotFoundError(Exception):
    """Raised when template is not found."""


class RuleValidationError(Exception):
    """Base exception for rule validation errors."""


class UnsupportedOperatorError(RuleValidationError):
    """Exception raised when an unsupported operator is used for a target."""

    def __init__(self, target: str, op: str, supported_operators: set[str]):
        super().__init__(
            f"Unsupported operator '{op}' for target '{target}'. "
            f"Supported operators: {', '.join(map(str, supported_operators))}"
        )
