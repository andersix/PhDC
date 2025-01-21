# vim: set ts=4 sw=4 sts=4 expandtab ai si ff=unix fileencoding=utf-8 textwidth=79:

import subprocess
import time
import logging
from threading import Timer
from typing import Optional
from ..utils.exceptions import ServiceError
from ..utils.constants import CONFIRMATION_TIMEOUT, FEEDBACK_DELAY
from ..display.backlight import DisplayBacklight
from ..display.manager import DisplayManager

logger = logging.getLogger('DisplayController')

class PiHole:
    """Manages PiHole operations"""
    
    def __init__(self, display_manager: DisplayManager, backlight: Optional[DisplayBacklight] = None):
        """
        Initialize PiHole controller
        
        Args:
            display_manager: DisplayManager instance for output control
            backlight: Optional DisplayBacklight instance for visual feedback
        """
        try:
            self.display = display_manager
            self.backlight = backlight
            self._waiting_for_confirmation = False
            self._confirmation_timer: Optional[Timer] = None
            logger.info("Initializing PiHole controller")
        except Exception as e:
            logger.error(f"Failed to initialize PiHole controller: {str(e)}")
            raise ServiceError(f"Failed to initialize PiHole controller: {str(e)}")

    def _start_confirmation_timer(self) -> None:
        """Start confirmation timeout timer"""
        if self._confirmation_timer:
            self._confirmation_timer.cancel()
        self._confirmation_timer = Timer(CONFIRMATION_TIMEOUT, self._handle_timeout)
        self._confirmation_timer.start()
        logger.debug("Started confirmation timer")

    def _handle_timeout(self) -> None:
        """Handle confirmation timeout"""
        if self._waiting_for_confirmation:
            logger.info("Update selection timeout - cancelling")
            self.cancel_update()

    def _clear_confirmation_state(self) -> None:
        """Clear all confirmation state"""
        if self._confirmation_timer:
            self._confirmation_timer.cancel()
            self._confirmation_timer = None
        self._waiting_for_confirmation = False
        logger.debug("Cleared confirmation state")

    def cancel_update(self) -> None:
        """Cancel any pending update confirmation"""
        if self._waiting_for_confirmation:
            logger.info("Update cancelled")
            print("\nUpdate cancelled")
            self._clear_confirmation_state()
            time.sleep(FEEDBACK_DELAY)
            self.display.switch_to_padd()

    def handle_button2_held(self, hold_time: float) -> None:
        """Handle button 2 hold event for showing update selection"""
        logger.info(f"Button 2 held for {hold_time:.1f} seconds")
        
        if hold_time >= 1.0:
            logger.info("Showing update selection")
            self._waiting_for_confirmation = True
            self._start_confirmation_timer()
            if not self.display.show_update_selection():
                logger.error("Failed to show update selection screen")
                self.cancel_update()

    def handle_button3_press(self) -> None:
        """Handle button 3 press for gravity update confirmation"""
        if self._waiting_for_confirmation:
            logger.info("Gravity update selected")
            self._clear_confirmation_state()
            self.update_gravity()

    def handle_button4_press(self) -> None:
        """Handle button 4 press for pihole update confirmation"""
        if self._waiting_for_confirmation:
            logger.info("Pi-hole update selected")
            self._clear_confirmation_state()
            self.update_pihole()

    def update_gravity(self) -> None:
        """Execute gravity update after confirmation"""
        logger.info("Starting gravity update")
        try:
            process = subprocess.Popen(
                ['sudo', 'pihole', '-g'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
            
            returncode = process.wait()
            
            if returncode == 0:
                logger.info("Gravity update completed successfully")
                print("\nGravity update completed successfully")
            else:
                logger.error("Gravity update failed")
                print("\nGravity update failed")
                
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to update gravity: {str(e)}")
            print(f"\nError: Failed to update gravity: {str(e)}")
            raise ServiceError(f"Failed to update gravity: {str(e)}")
        finally:
            time.sleep(FEEDBACK_DELAY)
            self.display.switch_to_padd()

    def update_pihole(self) -> None:
        """Execute Pi-hole update after confirmation"""
        logger.info("Starting Pi-hole update")
        try:
            process = subprocess.Popen(
                ['sudo', 'pihole', '-up'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
            
            returncode = process.wait()
            
            if returncode == 0:
                logger.info("Pi-hole update completed successfully")
                print("\nPi-hole update completed successfully")
            else:
                logger.error("Pi-hole update failed")
                print("\nPi-hole update failed")
                
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to update Pi-hole: {str(e)}")
            print(f"\nError: Failed to update Pi-hole: {str(e)}")
            raise ServiceError(f"Failed to update Pi-hole: {str(e)}")
        finally:
            time.sleep(FEEDBACK_DELAY)
            self.display.switch_to_padd()

    def cleanup(self) -> None:
        """Clean up PiHole resources"""
        try:
            self._clear_confirmation_state()
            logger.info("Cleaned up PiHole controller")
        except Exception as e:
            logger.error(f"Error during PiHole cleanup: {str(e)}")

