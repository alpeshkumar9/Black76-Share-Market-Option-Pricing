"""
    Config file containing some basic setup of a logger and Settings file.
"""
import logging
import sys
from pathlib import Path
from functools import lru_cache
from pydantic import BaseSettings

# Define constants
CWD = Path(__file__).parent
BASE_DIR = CWD.parent
ENV = BASE_DIR.joinpath(".env")

APP_NAME = "Share Market API"
APP_VERSION = "0.0.1"

DATE_FORMAT = "%d-%b-%y %H:%M:%S"
LOGGER_FORMAT = '{asctime:<2} :: {levelname:<8} :: {name:<22} :: {funcName:<30} :: line {lineno:>4}  {message}'


class Settings(BaseSettings):
    """
    Returns a Settings object based on values from the .env file.
    """
    TESTING: bool = False
    LOG_LEVEL: str = logging.INFO

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings(_env_file=ENV)


# Set logging level overrides for specific loggers
logging_overrides = {
    'httpx': logging.WARNING,
    'asyncio': logging.WARNING,
    'urllib3': logging.WARNING
}

# Set up root logger
root_logger = logging.getLogger(APP_NAME)

# Configure logging


def configure_logging():
    """
    Configures logging settings based on values from the Settings object.
    """
    # Get settings from .env file
    settings = get_settings()

    # Set logging level from settings
    logging_level = settings.LOG_LEVEL

    # Set up log message formatting
    handler_format = logging.Formatter(
        LOGGER_FORMAT, style="{", datefmt=DATE_FORMAT)
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("logs/logs.log")

    # Apply formatting to log message handlers
    stdout_handler.setFormatter(handler_format)
    file_handler.setFormatter(handler_format)

    # Add log message handlers to root logger
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)

    # Set logging levels for specific loggers
    for log_name, log_level in logging_overrides.items():
        logger = logging.getLogger(log_name)

        # To override the default severity of logging
        logger.setLevel(log_level)

    # Log a message if running in testing mode
    if settings.TESTING:
        root_logger.info(f"Running in TESTING mode. {logging_level=}")


configure_logging()

# Get logger instance


def get_logger(module: str = None) -> logging.Logger:
    """
    Returns a logger instance for the specified module or the root logger.
    """
    global root_logger

    if module is None:
        return root_logger
    return root_logger.getChild(module)
