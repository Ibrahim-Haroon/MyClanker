import sys
import logging
from src.util.env import Env


def setup_logging():
    """
    Configure logging with a single stream. If DEBUG=True, show all levels.
    If False, show only INFO and above.
    """
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    debug_enabled = str(Env()["DEBUG"]).lower() == "true"
    root_logger.setLevel(logging.DEBUG if debug_enabled else logging.INFO)
    console_handler.setLevel(logging.DEBUG if debug_enabled else logging.INFO)
    root_logger.addHandler(console_handler)

    return root_logger
