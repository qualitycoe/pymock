# tests/test_config_loader.py

import pytest
import yaml

from pymock.config.loader import ConfigLoader, get_config
from pymock.server.exceptions import ConfigError


@pytest.fixture
def temp_config(tmp_path):
    """Fixture creating a temporary config file."""
    config_data = {"server": {"host": "localhost", "port": 8080}, "endpoints_path": [str(tmp_path / "endpoints")]}
    config_file = tmp_path / "config.yaml"
    with config_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config_data, f)
    return str(config_file)


@pytest.fixture
def temp_endpoint(tmp_path):
    """Fixture creating a temporary endpoint file."""
    endpoint_dir = tmp_path / "endpoints"
    endpoint_dir.mkdir()
    endpoint_file = endpoint_dir / "test.yaml"
    endpoint_data = {"path": "/test", "method": "GET", "response": {"status": 200}}
    with endpoint_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(endpoint_data, f)
    return endpoint_file


def test_get_config(temp_config):
    """Test loading a valid config with endpoints."""
    config = get_config(temp_config)
    assert config["server"] == {"host": "localhost", "port": 8080}
    assert len(config["endpoints"]) == 1
    assert config["endpoints"][0]["path"] == "/test"


def test_config_loader_invalid_file():
    """Test loading a non-existent config file."""
    with pytest.raises(ConfigError, match="Configuration error"):
        ConfigLoader._load_config("nonexistent.yaml")  # pylint: disable=protected-access


def test_env_overrides(temp_config, monkeypatch):
    """Test environment variable overrides."""
    monkeypatch.setenv("mytool__SERVER__HOST", "test.host")
    monkeypatch.setenv("mytool__SERVER__PORT", "9090")
    config = get_config(temp_config)
    assert config["server"]["host"] == "test.host"
    assert config["server"]["port"] == 9090


def test_invalid_yaml(temp_config):
    """Test loading invalid YAML."""
    with open(temp_config, "w", encoding="utf-8") as f:
        f.write("invalid: yaml: content")
    with pytest.raises(ConfigError, match="Configuration error"):
        get_config(temp_config)


def test_invalid_port_env(temp_config, monkeypatch):
    """Test invalid port environment variable."""
    monkeypatch.setenv("mytool__SERVER__PORT", "invalid")
    config = get_config(temp_config)
    assert config["server"]["port"] == 8080  # Should keep YAML value


def test_empty_endpoints_dir(temp_config):
    """Test config with empty endpoints directory."""
    config = get_config(temp_config)
    assert config["endpoints"] == []  # No endpoints found


def test_logging_invalid_yaml(temp_config):
    """Test logging of invalid YAML."""
    with open(temp_config, "w", encoding="utf-8") as f:
        f.write("invalid: yaml: content")
    with pytest.raises(ConfigError, match="Configuration error.*mapping values are not allowed"):
        get_config(temp_config)


def test_invalid_schema(temp_config):
    """Test invalid schema raises ConfigError."""
    with open(temp_config, "w", encoding="utf-8") as f:
        yaml.dump({"invalid_key": "value"}, f)
    with pytest.raises(ConfigError, match="Configuration error"):
        get_config(temp_config)
