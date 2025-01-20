from typing import Optional
import time
from gpiozero import PWMLED
from gpiozero.exc import GPIOZeroError, OutputDeviceBadValue
import logging
from ..utils.exceptions import BacklightError
from ..utils.config import Config

logger = logging.getLogger('DisplayController')

class DisplayBacklight:
    """Controls the display backlight brightness using PWM with error handling and gamma correction"""
    
    def __init__(self):
        """Initialize with configuration from config file"""
        config = Config().display.get('backlight', {})
        self.pin: int = config.get('pin', 18)
        self.gamma: float = config.get('gamma', 2.2)
        self.pwmf: int = config.get('pwm_frequency', 240)
        self.retry_attempts: int = config.get('retry_attempts', 3)
        
        self.led: Optional[PWMLED] = None
        self.current_step = 0
        
        # Define brightness levels (11 steps from 100% to 0%)
        self.brightness_levels = [
            1.0,    # 100%
            0.9,    # 90%
            0.8,    # 80%
            0.7,    # 70%
            0.6,    # 60%
            0.5,    # 50%
            0.4,    # 40%
            0.3,    # 30%
            0.2,    # 20%
            0.1,    # 10%
            0.0     # 0%
        ]
        
        self._initialize_pwm()

    def _initialize_pwm(self) -> None:
        """Initialize PWM with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Attempting to initialize PWM on pin {self.pin} (attempt {attempt + 1}/{self.retry_attempts})")
                self.led = PWMLED(
                    pin=self.pin, 
                    frequency=self.pwmf, 
                    initial_value=1.0
                )
                # Start at full brightness
                self.set_brightness(self.brightness_levels[0])
                logger.info("PWM initialization successful")
                break
            except GPIOZeroError as e:
                logger.error(f"PWM initialization attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_attempts - 1:
                    raise BacklightError(f"Failed to initialize PWM after {self.retry_attempts} attempts: {str(e)}")
                time.sleep(0.5)

    def apply_gamma(self, value: float) -> float:
        """Apply gamma correction to a brightness value"""
        return pow(value, self.gamma) if value > 0 else 0

    def set_brightness(self, raw_value: float) -> None:
        """Set brightness with gamma correction"""
        if not self.led:
            logger.error("Attempted to set brightness but PWM device not initialized")
            raise BacklightError("PWM device not initialized")
        
        try:
            # Apply gamma correction before setting the LED value
            corrected_value = self.apply_gamma(raw_value)
            self.led.value = corrected_value
            logger.debug(f"Set brightness raw:{raw_value:.3f} gamma-corrected:{corrected_value:.3f}")
        except OutputDeviceBadValue as e:
            logger.error(f"Failed to set brightness: {str(e)}")
            raise BacklightError(f"Invalid brightness value: {str(e)}")

    def step_brightness(self) -> None:
        """Step brightness down by 10%, cycling back to 100% after 0%"""
        if not self.led:
            logger.error("Attempted to step brightness but PWM device not initialized")
            raise BacklightError("PWM device not initialized")
        
        try:
            # Move to next brightness level
            self.current_step = (self.current_step + 1) % len(self.brightness_levels)
            # Set the new brightness from our levels list with gamma correction
            raw_value = self.brightness_levels[self.current_step]
            self.set_brightness(raw_value)
            logger.debug(f"Set brightness to {self.get_brightness_percentage()}%")
        except OutputDeviceBadValue as e:
            logger.error(f"Failed to set brightness: {str(e)}")
            raise BacklightError(f"Failed to step brightness: {str(e)}")

    def get_brightness_percentage(self) -> int:
        """Get current brightness as percentage (before gamma correction)"""
        if not self.led:
            logger.error("Attempted to get brightness but PWM device not initialized")
            raise BacklightError("PWM device not initialized")
        
        return int(self.brightness_levels[self.current_step] * 100)

    def cleanup(self) -> None:
        """Clean up LED resources"""
        if self.led:
            try:
                logger.info("Cleaning up PWM device")
                self.led.close()
            except Exception as e:
                logger.error(f"Error during PWM cleanup: {str(e)}")
                raise BacklightError(f"Failed to cleanup PWM device: {str(e)}")

