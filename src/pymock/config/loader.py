# src/pymock/config/loader.py
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from pymock.config.validator import validate_config
from pymock.constants.schemas import CONFIG_SCHEMA
from pymock.server.exceptions import ConfigError

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Manages loading and caching of YAML configuration files."""

    @staticmethod
    @lru_cache(maxsize=1)
    def get_config(config_path: str) -> dict[str, Any]:
        """
        Returns the singleton configuration, loading it from the provided path if not cached.

        Args:
            config_path: Path to the main YAML configuration file.

        Returns:
            The loaded configuration dictionary.

        Raises:
            ConfigError: If loading or validation fails.
        """
        return ConfigLoader._load_config(config_path)

    @staticmethod
    def _load_config(config_path: str) -> dict[str, Any]:
        """
        Loads and validates the YAML config, applies env overrides, and scans endpoint dirs.

        Args:
            config_path: Path to the main YAML configuration file.

        Returns:
            The fully processed configuration dictionary.

        Raises:
            ConfigError: If file access, parsing, or validation fails.
        """
        try:
            config_file = Path(config_path)
            with config_file.open(encoding="utf-8") as file:
                config = yaml.safe_load(file)  # Remove 'or {}' to let errors propagate
                if config is None:
                    config = {}

            if not isinstance(config, dict):
                msg = f"Config at '{config_path}' must be a dictionary, got {type(config)}"
                raise ConfigError(msg)

            validate_config(config, CONFIG_SCHEMA)
            config = ConfigLoader._apply_env_overrides(config)
            endpoints_path = config.get("endpoints_path", [])
            config["endpoints"] = ConfigLoader._scan_endpoint_dirs(endpoints_path)
            return config

        except (yaml.YAMLError, ConfigError, OSError) as e:
            logger.error("Failed to load config from '%s': %s", config_path, e, exc_info=True)
            msg = f"Configuration error at '{config_path}': {e!s}"
            raise ConfigError(msg) from e

    @staticmethod
    def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
        """
        Applies environment variable overrides to the configuration.

        Args:
            config: The base configuration dictionary to modify.

        Returns:
            The updated configuration with environment overrides applied.
        """
        # Ensure server key exists, but don't override existing values with defaults
        if "server" not in config:
            config["server"] = {}

        # Apply env overrides, overwriting YAML values if present
        if env_host := os.environ.get("PYMOCK__SERVER__HOST"):
            config["server"]["host"] = env_host

        if env_port := os.environ.get("PYMOCK__SERVER__PORT"):
            try:
                config["server"]["port"] = int(env_port)
            except ValueError:
                logger.warning("Invalid port value '%s' from env, ignoring", env_port)

        if env_debug := os.environ.get("PYMOCK__DEBUG"):
            # Convert string to bool
            config["debug"] = env_debug.lower() == "true"

        if env_paths := os.environ.get("PYMOCK__SERVER__ENDPOINTS_PATH"):
            config["endpoints_path"] = [p.strip() for p in env_paths.split(",")]

        return config

    @staticmethod
    def _scan_endpoint_dirs(endpoint_dirs: list[str]) -> list[dict[str, Any]]:
        """
        Scans directories recursively for endpoint YAML files.

        Args:
            endpoint_dirs: List of directory paths to scan.

        Returns:
            List of endpoint configurations from YAML files.
        """
        endpoints: list[dict[str, Any]] = []

        for dir_path in map(Path, endpoint_dirs):
            if not dir_path.exists():
                logger.warning("Endpoints directory '%s' does not exist", dir_path)
                continue

            for file_path in dir_path.rglob("*.yaml"):
                try:
                    with file_path.open(encoding="utf-8") as file:
                        endpoint_config = yaml.safe_load(file)
                        if isinstance(endpoint_config, dict) and endpoint_config:
                            endpoints.append(endpoint_config)
                        elif endpoint_config is not None:
                            logger.warning("Skipping non-dict config in '%s'", file_path)
                except yaml.YAMLError as e:
                    logger.error("Failed to parse endpoint file '%s': %s", file_path, e)

        return endpoints


# Module-level convenience function
def get_config(config_path: str) -> dict[str, Any]:
    """Wrapper for ConfigLoader.get_config, maintaining original API."""
    return ConfigLoader.get_config(config_path)
