# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:fileformat=unix:
import subprocess
import logging
from ..utils.exceptions import ServiceError
from ..utils.constants import FEEDBACK_DELAY

logger = logging.getLogger('DisplayController')

class SystemOs:
    """Manages system-level operations like reboot and shutdown"""
    
    def __init__(self):
        """Initialize SystemOs controller"""
        try:
            logger.info("Initializing SystemOs controller")
        except Exception as e:
            logger.error(f"Failed to initialize SystemOs controller: {str(e)}")
            raise ServiceError(f"Failed to initialize SystemOs controller: {str(e)}")

    def reboot_system(self) -> None:
        """Handle system reboot command"""
        logger.info("SystemOs: Initiating system reboot")
        try:
            subprocess.run(['sudo', 'reboot'], check=True)
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to reboot system: {str(e)}")
            raise ServiceError(f"Failed to reboot system: {str(e)}")

    def shutdown_system(self) -> None:
        """Handle system shutdown command"""
        logger.info("SystemOs: Initiating system shutdown")
        try:
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to shutdown system: {str(e)}")
            raise ServiceError(f"Failed to shutdown system: {str(e)}")

    def handle_button4_held(self, hold_time: float) -> None:
        """
        Handle button 4 hold event based on hold duration
        
        Args:
            hold_time: Duration in seconds that the button was held
        """
        logger.info(f"Button 4 released after {hold_time:.1f} seconds")
        
        if hold_time < 2.0:
            return
        elif hold_time >= 5.0:
            logger.info("Hold time >= 5 seconds - initiating shutdown")
            self.shutdown_system()
        else:  # Between 2 and 5 seconds
            logger.info("Hold time >= 2 seconds - initiating reboot")
            self.reboot_system()

    def cleanup(self) -> None:
        """Clean up SystemOs resources if needed"""
        try:
            logger.info("Cleaning up SystemOs controller")
        except Exception as e:
            logger.error(f"Error during SystemOs cleanup: {str(e)}")

