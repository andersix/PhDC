# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:smartindent:fileformat=unix:

import time
from typing import Callable, Optional
from gpiozero import Button as GPIOButton
from gpiozero.exc import GPIOZeroError
import logging
from ..utils.exceptions import ButtonError
from ..models import ButtonConfig

logger = logging.getLogger('DisplayController')

class ButtonHandler:
    """
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
        """
        try:
            self._hold_start: Optional[float] = None
            self.function = config.function

            self.button = GPIOButton(
                pin=config.pin,
                pull_up=config.pull_up,
                bounce_time=config.bounce_time,
                hold_time=config.hold_time,
                hold_repeat=config.hold_repeat
            )

            self._setup_callbacks(callback, hold_callback)

            logger.info(f"Initialized {self.function} button on pin {config.pin}")

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
        self._press_callback = press_callback
        self._hold_callback = hold_callback

        if hold_callback:
            def on_press():
                self._hold_start = time.time()
                logger.debug(f"{self.function} button pressed at {self._hold_start}")
                if self._press_callback:  # Call press callback if it exists
                    self._press_callback()

            self.button.when_pressed = on_press
            self.button.when_released = self._on_release
        elif press_callback:
            self.button.when_pressed = press_callback

    def _on_release(self) -> None:
        """Handle button release and calculate hold duration"""
        if self._hold_start is not None and self._hold_callback:
            hold_duration = time.time() - self._hold_start
            logger.debug(f"{self.function} button released after {hold_duration:.2f}s")
            self._hold_callback(hold_duration)
        self._hold_start = None

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

