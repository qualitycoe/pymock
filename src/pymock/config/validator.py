# src/pymock/config/validator.py
import logging

from jsonschema import ValidationError, validate

from pymock.server.exceptions import ConfigError

logger = logging.getLogger(__name__)


def validate_config(config: dict, schema: dict) -> None:
    """
    Validates the configuration against a predefined schema.
    """
    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        logger.error("Invalid Configuration: %s", e, exc_info=True)
        error_message = "Configuration error: " + str(e)
        raise ConfigError(error_message) from e
