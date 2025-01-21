# src/utils/constants.py
from enum import Enum
from pathlib import Path

class ButtonFunction(Enum):
    """Enumeration of button functions"""
    BRIGHTNESS_SYSTEM = "brightness_system"
    UPDATE_SELECT = "update_select"
    CONFIRM_1 = "confirm_1"  # First confirmation option in either mode
    CONFIRM_2 = "confirm_2"  # Second confirmation option in either mode

# Timing constants
CONFIRMATION_TIMEOUT = 30  # seconds
FEEDBACK_DELAY = 3        # seconds for user feedback messages

# Hold time thresholds
SYSTEM_CONTROL_HOLD = 5.0  # seconds for system control activation
UPDATE_SELECT_HOLD = 1.0   # seconds for update selection activation

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'
LOG_DIR = ROOT_DIR / 'log'

