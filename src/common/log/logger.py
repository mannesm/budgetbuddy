import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.

    Configures logging based on environment variables. Supports logging
    to console and/or file with rotation.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        ```python
        logger = get_logger(__name__)
        logger.info("Hello, world!")
        ```
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
        log_file_path = os.getenv("LOG_FILE_PATH", "app.log")

        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s")

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_to_file:
            file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False

    return logger
