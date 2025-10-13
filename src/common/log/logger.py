import os

from dotenv import load_dotenv
from loguru import logger as loguru_logger

load_dotenv()

DEFAULT_LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level: <8}</level> [{extra[name]}]: <level>{message}</level>\n"
)


def get_logger(name: str = None):
    """Get a configured Loguru logger instance."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    log_file_path = os.getenv("LOG_FILE_PATH", "app.log")
    loguru_logger.remove()

    loguru_logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format=DEFAULT_LOGGER_FORMAT,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    if log_to_file:
        loguru_logger.add(
            log_file_path,
            rotation="5 MB",
            retention=3,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} {level: <8} [{extra[name]}]: {message}",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

    # Bind logger with name for context
    return loguru_logger.bind(name=name or "root")
