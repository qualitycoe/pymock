# pymock/logging_config.py
import logging


def setup_logging(logging_config: dict[str, str] | None) -> None:
    """Configures application-wide logging based on the provided dictionary."""
    if not logging_config:
        logging_config = {}

    level_str = logging_config.get("level", "INFO").upper()
    log_file = logging_config.get("file")

    # Convert string level to actual logging level constant
    level = getattr(logging, level_str, logging.INFO)

    # We can also ensure any existing root handlers are cleared
    # if you want to avoid duplicates:
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=level,
        filename=log_file,  # if None, logs go to console; if set, logs go to file
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    # OPTIONAL: If you want logs to go BOTH to file and console,
    # you can add a secondary StreamHandler. For example:
    if log_file:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s"))
        logging.getLogger().addHandler(console)
