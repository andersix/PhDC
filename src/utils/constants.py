# src/utils/constants.py
from enum import Enum
from pathlib import Path

class ButtonFunction(Enum):
    BRIGHTNESS = "brightness"
    GRAVITY = "gravity"
    UPDATE = "update"
    SYSTEM = "system"

# Timing constants
CONFIRMATION_TIMEOUT = 30  # seconds
FEEDBACK_DELAY = 3        # seconds for user feedback messages

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'
LOG_DIR = ROOT_DIR / 'log'

