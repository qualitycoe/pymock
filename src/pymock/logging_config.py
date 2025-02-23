# src/pymock/logging_config.py
import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configures application-wide logging."""
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
