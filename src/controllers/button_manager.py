# vim: set ts=4 sw=4 sts=4 expandtab ai si ff=unix fileencoding=utf-8 textwidth=79:

from typing import List, Callable, Optional
import logging
from ..utils.exceptions import ButtonError
from ..utils.config import Config
from ..models import ButtonConfig
from ..hardware.button import ButtonHandler
from ..display.backlight import DisplayBacklight
from ..services.pihole import PiHole
from ..services.system import SystemOs
from ..display.manager import DisplayManager

logger = logging.getLogger('DisplayController')

class ButtonManager:
    """Manages multiple button instances and their associated controllers"""
    
    def __init__(self, display_manager: DisplayManager):
        """
        Initialize button manager and controllers
        
        Args:
            display_manager: DisplayManager instance for display control
        """
        self.buttons: List[ButtonHandler] = []
        try:
            logger.info("Initializing ButtonManager and controllers")
            self.backlight = DisplayBacklight()
            self.display = display_manager
            self.pihole = PiHole(display_manager=self.display, backlight=self.backlight)
            self.system = SystemOs()
        except Exception as e:
            error_msg = f"Failed to initialize controllers: {str(e)}"
            logger.critical(error_msg)
            raise ButtonError(error_msg)

    def add_button(self, 
                  config: ButtonConfig, 
                  callback: Optional[Callable[[], None]] = None,
                  hold_callback: Optional[Callable[[float], None]] = None) -> None:
        """
        Add a new button to manage
        
        Args:
            config: ButtonConfig object for the new button
            callback: Optional function to call when button is pressed
            hold_callback: Optional function to call when button is held
            
        Raises:
            ButtonError: If button initialization fails
        """
        try:
            button = ButtonHandler(
                config=config,
                callback=callback,
                hold_callback=hold_callback
            )
            self.buttons.append(button)
            logger.info(f"Added button on pin {config.pin}")
        except Exception as e:
            error_msg = f"Failed to add button on pin {config.pin} {type(config.pin)}: {str(e)}"
            logger.error(error_msg)
            raise ButtonError(error_msg)

    def cleanup(self) -> None:
        """Clean up all managed resources"""
        logger.info("Starting cleanup of ButtonManager")
        for button in self.buttons:
            button.cleanup()
        self.backlight.cleanup()
        self.pihole.cleanup()
        self.system.cleanup()
        logger.info("Cleanup completed")

