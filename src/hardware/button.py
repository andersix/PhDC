# vim: set ts=4 sw=4 sts=4 expandtab ai si ff=unix fileencoding=utf-8 textwidth=79:

import time
from typing import Callable, Optional
from gpiozero import Button as GPIOButton
from gpiozero.exc import GPIOZeroError
import logging
from ..utils.exceptions import ButtonError
from ..utils.config import Config
from ..models import ButtonConfig

logger = logging.getLogger('DisplayController')

class ButtonHandler:
    """
    A class to handle button input using gpiozero Button
    
    This class provides a wrapper around GPIOZero's Button class,
    adding support for hold duration tracking and custom callbacks.
    """
    
    def __init__(self, 
                 config: ButtonConfig, 
                 callback: Optional[Callable[[], None]] = None,
                 hold_callback: Optional[Callable[[float], None]] = None):
        """
        Initialize the button handler.
        
        Args:
            config: ButtonConfig object containing pin and setup information
            callback: Optional function to call when button is pressed
            hold_callback: Optional function to call when button is released after hold
            
        Raises:
            ButtonError: If initialization fails
        """
        try:
            self._hold_start: Optional[float] = None
            
            self.button = GPIOButton(
                pin=config.pin,
                pull_up=config.pull_up,
                bounce_time=config.bounce_time,
                hold_time=config.hold_time,
                hold_repeat=config.hold_repeat
            )
            
            # Set up callbacks
            self._setup_callbacks(callback, hold_callback)
                
            logger.info(f"Initialized button on pin {config.pin}")
            
        except GPIOZeroError as e:
            error_msg = f"Failed to initialize button on pin {config.pin}: {str(e)}"
            logger.error(error_msg)
            raise ButtonError(error_msg)

    def _setup_callbacks(self, 
                        press_callback: Optional[Callable[[], None]],
                        hold_callback: Optional[Callable[[float], None]]) -> None:
        """
        Set up button callbacks
        
        Args:
            press_callback: Function to call on button press
            hold_callback: Function to call on button hold release
        """
        if press_callback and not hold_callback:
            self.button.when_pressed = press_callback
        
        if hold_callback:
            # Set up hold duration tracking
            self.button.when_pressed = self._on_press
            self.button.when_released = lambda: self._on_release(hold_callback)

    def _on_press(self) -> None:
        """Store the time when button is pressed"""
        self._hold_start = time.time()
        logger.debug(f"Button press recorded at {self._hold_start}")

    def _on_release(self, callback: Callable[[float], None]) -> None:
        """
        Calculate hold duration and call the callback when button is released
        
        Args:
            callback: Function to call with the hold duration
        """
        if self._hold_start is not None:
            hold_duration = time.time() - self._hold_start
            logger.debug(f"Button released after {hold_duration:.2f} seconds")
            self._hold_start = None
            callback(hold_duration)

    def cleanup(self) -> None:
        """
        Clean up button resources
        
        This method ensures proper cleanup of GPIO resources
        """
        try:
            if hasattr(self, 'button') and self.button is not None:
                pin_number = self.button.pin.number
                self.button.close()
                logger.debug(f"Cleaned up button on pin {pin_number}")
            else:
                logger.debug("No button to clean up")
        except Exception as e:
            error_msg = f"Error during button cleanup: {str(e)}"
            logger.error(error_msg)
            raise ButtonError(error_msg)

