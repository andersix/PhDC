# src/utils/constants.py
from enum import Enum
from pathlib import Path

class ButtonFunction(Enum):
    """Enumeration of button functions"""
    BRIGHTNESS_SYSTEM = "brightness_system"  # Button 1: Brightness control and system operations
    UPDATE_SELECT = "update_select"          # Button 2: Update menu selection
    CONFIRM_1 = "confirm_1"                  # Button 3: First confirmation option
    CONFIRM_2 = "confirm_2"                  # Button 4: Second confirmation option

# Timing constants
CONFIRMATION_TIMEOUT = 30  # seconds to wait for user confirmation
FEEDBACK_DELAY = 3        # seconds to show feedback messages

# Button hold thresholds
SYSTEM_CONTROL_HOLD = 5.0  # seconds to hold for system control activation
UPDATE_SELECT_HOLD = 1.0   # seconds to hold for update selection

# PWM settings
PWM_FREQUENCY = 240  # Hz - matches config.yaml default
GAMMA_CORRECTION = 2.2  # Standard gamma correction value

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / 'config'
LOG_DIR = ROOT_DIR / 'log'

