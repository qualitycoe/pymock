# pymock/logging_config.py
import logging


def setup_logging(debug: bool = False) -> None:  # noqa: FBT001, FBT002
    """Configures application-wide logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
