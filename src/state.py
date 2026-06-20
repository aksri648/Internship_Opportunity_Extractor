import json
import logging
import os

from .config import STATE_FILE

logger = logging.getLogger(__name__)


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("State file not found, creating empty state")
        return {}
    except json.JSONDecodeError:
        logger.warning("State file corrupted, resetting to empty state")
        return {}


def save_state(state: dict) -> None:
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except OSError as e:
        logger.error("Failed to save state: %s", e)
