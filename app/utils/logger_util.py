from loguru import logger
import sys
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")
logger.add(LOG_FILE, rotation="1 day", retention="7 days", compression="zip")


def log_info(message: str):
    logger.info(message)


def log_warning(message: str):
    logger.warning(message)


def log_error(message: str):
    logger.error(message)


def log_debug(message: str):
    logger.debug(message)


def log_exception(message: str):
    logger.exception(message)
