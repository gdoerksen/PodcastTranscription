import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import gmtime
from typing import Optional

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LOG_SAVE_DIR = Path.cwd() / "logs" #TODO change this
# LOG_SAVE_DIR = Path("/var/log/")
DEFAULT_LOG_NAME = "log.log"
MAX_LOG_SIZE = 1024 * 1024 * 10  # 10 MiB


def pretty_print_bytes(data: bytes) -> str:
    """Pretty prints bytes in hex format."""
    return " ".join(f"{a:02x}{b:02x}" for a, b in zip(data[0::2], data[1::2]))


def configure_logging(
    # logger: logging.Logger,
    filename: Optional[str] = None,
    log_to_file: bool = False,
    verbose: bool = False,
):
    """Configures logs for Ant Simulator. Set log_to_console true to only long to console."""

    log_level = logging.DEBUG if verbose else logging.INFO
    log_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    log_formatter.converter = gmtime

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[console_handler],
    )
    logging.getLogger("").addHandler(console_handler)
    logging.addLevelName(logging.DEBUG, "[DEBUG]")
    logging.addLevelName(logging.INFO, "[INFO] ")
    logging.addLevelName(logging.WARNING, "[WARN] ")
    logging.addLevelName(logging.ERROR, "[ERROR]")
    logging.addLevelName(logging.CRITICAL, "[CRIT] ")

    if log_to_file:
        try:
            LOG_SAVE_DIR.mkdir(parents=True, exist_ok=True)
            log_path = LOG_SAVE_DIR / filename if filename else DEFAULT_LOG_NAME
            file_handler = RotatingFileHandler(
                log_path, maxBytes=MAX_LOG_SIZE, encoding="utf-8", backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(log_formatter)
            logging.getLogger("").addHandler(file_handler)
        except PermissionError as e:
            logging.getLogger("").exception(e)
            logging.getLogger("").error(
                "Could not create log file. Logging to console only."
            )
