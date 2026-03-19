import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logger
logger = logging.getLogger("ssc")
logger.setLevel(logging.INFO)

# File handler with rotation
handler = RotatingFileHandler("logs/ssc.log", maxBytes=10485760, backupCount=10)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_action(action: str, user_id: int = None, details: str = ""):
    """Log user actions"""
    msg = f"Action: {action}"
    if user_id:
        msg += f" | User: {user_id}"
    if details:
        msg += f" | Details: {details}"
    logger.info(msg)


def log_error(
    error: str,
    user_id: int = None,
    exception: Exception = None,
    details: str = "",
):
    """Log errors"""
    msg = f"Error: {error}"
    if user_id:
        msg += f" | User: {user_id}"
    if details:
        msg += f" | Details: {details}"
    if exception:
        msg += f" | Exception: {str(exception)}"
    logger.error(msg)
