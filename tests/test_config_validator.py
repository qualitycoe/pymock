# tests/test_config_validator.py
import pytest

from pymock.config.validator import validate_config
from pymock.constants.schemas import CONFIG_SCHEMA
from pymock.server.exceptions import ConfigError


def test_valid_config():
    """Test validating a valid config."""
    config = {"server": {"host": "localhost", "port": 8080}, "endpoints_path": ["endpoints"]}
    validate_config(config, CONFIG_SCHEMA)  # Should not raise


def test_invalid_config():
    """Test validating an invalid config."""
    config = {"server": {"host": "localhost", "port": "invalid"}, "endpoints_path": []}
    with pytest.raises(ConfigError, match="Configuration error"):
        validate_config(config, CONFIG_SCHEMA)
