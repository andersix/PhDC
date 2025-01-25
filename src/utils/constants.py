# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:smartindent:fileformat=unix:

from enum import Enum
from .config import Config

class ButtonFunction(Enum):
    """Enumeration of button functions"""
    BRIGHTNESS_SYSTEM = "brightness_system"
    UPDATE_SELECT = "update_select"
    CONFIRM_1 = "confirm_1"
    CONFIRM_2 = "confirm_2"

# Load config
config = Config()
timing_config = config.timing
paths_config = config.paths

# Timing constants
CONFIRMATION_TIMEOUT = timing_config.get('confirmation_timeout', 30)
FEEDBACK_DELAY = timing_config.get('feedback_delay', 3)

# Button hold thresholds
button_config = config.buttons
SYSTEM_CONTROL_HOLD = float(button_config['1'].get('hold_time', 5.0))
UPDATE_SELECT_HOLD = float(button_config['2'].get('hold_time', 1.0))

# Default paths
DEFAULT_PADD_SCRIPT = "/home/pi/PADD/padd.sh"
DEFAULT_PYTHON_PATH = "/usr/bin/python3"
DEFAULT_MAIN_SCRIPT = "/home/pi/pihole_display/main.py"

# Configured paths
PADD_SCRIPT_PATH = paths_config.get('padd_script', DEFAULT_PADD_SCRIPT)
PYTHON_PATH = paths_config.get('python_path', DEFAULT_PYTHON_PATH)
MAIN_SCRIPT_PATH = paths_config.get('main_script', DEFAULT_MAIN_SCRIPT)

