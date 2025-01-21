# vim: set ts=4 sw=4 sts=4 expandtab ai si ff=unix fileencoding=utf-8 textwidth=79:

import subprocess
import time
import logging
from typing import Optional
from ..utils.exceptions import DisplayError
from ..utils.config import Config
from .tmux import TMuxController

logger = logging.getLogger('DisplayController')

class DisplayManager:
    """Manages display output and PADD integration"""
    
    def __init__(self):
        """Initialize display manager with TMux controller"""
        self.tmux = TMuxController()
        config = Config().display.get('tmux', {})
        self.session_name = config.get('session_name', 'padd')
        self.padd_window = config.get('padd_window', 'padd')
        self.control_window = config.get('control_window', 'control')

    def check_padd(self) -> bool:
        """
        Verify PADD session exists and is running
        
        Returns:
            bool: True if session exists, False otherwise
        """
        try:
            logger.debug("Checking for PADD tmux session")
            result = subprocess.run(
                ['tmux', 'has-session', '-t', self.session_name],
                capture_output=True
            )
            
            if result.returncode != 0:
                logger.error("PADD tmux session not found")
                return False
                
            logger.debug("PADD tmux session found")
            return True
            
        except Exception as e:
            logger.error(f"Error checking PADD session: {e}")
            return False

    def show_update_selection(self) -> bool:
        """
        Show update selection screen
        
        Returns:
            bool: True if display switched successfully
        """
        try:
            logger.debug("Switching to control window for update selection")
            self.tmux.switch_window(self.control_window)
            
            self._clear_screen()
            
            print("\n" * 2)
            print("Pi-hole Update Selection")
            print("----------------------")
            print("\nChoose update type:")
            print("\nButton 3: Update Gravity Lists")
            print("- Updates Pi-hole's blocklists")
            print("- Takes a few minutes")
            print("- Safe to run anytime")
            print("\nButton 4: Update Pi-hole Core")
            print("- Updates Pi-hole software")
            print("- May take longer")
            print("- Best to run during off-hours")
            print("\nWaiting 30 seconds for selection...")
            print("Timer will cancel if no button is pressed.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error showing update selection: {e}")
            return False

    def show_system_control(self) -> bool:
        """
        Show system control options
        
        Returns:
            bool: True if display switched successfully
        """
        try:
            logger.debug("Switching to control window for system control")
            self.tmux.switch_window(self.control_window)
            
            self._clear_screen()
            
            print("\n" * 2)
            print("System Control Options")
            print("--------------------")
            print("\nWARNING: These actions will affect system power state!")
            print("\nChoose an option:")
            print("\nButton 3: Restart System")
            print("- Performs a clean system reboot")
            print("- All services will restart")
            print("- System will be unavailable briefly")
            print("\nButton 4: Shutdown System")
            print("- Performs a clean shutdown")
            print("- System will power off")
            print("- Requires physical power cycle to restart")
            print("\nWaiting 30 seconds for selection...")
            print("Timer will cancel if no button is pressed.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error showing system control: {e}")
            return False

    def switch_to_padd(self) -> None:
        """Switch back to PADD window"""
        try:
            logger.debug("Switching back to PADD window")
            self.tmux.switch_window(self.padd_window)
            logger.debug("Successfully switched to PADD window")
        except Exception as e:
            logger.error(f"Error switching to PADD window: {e}")
            raise DisplayError(f"Failed to switch to PADD window: {e}")

    def _clear_screen(self) -> None:
        """Clear screen and reset cursor position"""
        try:
            # Clear screen
            subprocess.run(['clear'], check=True)
            # Move cursor to top
            print("\033[H", end="")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to clear screen: {e}")
            raise DisplayError(f"Failed to clear screen: {e}")

    def execute_command(self, command: list[str]) -> tuple[int, str, str]:
        """
        Execute a command and capture its output
        
        Args:
            command: Command list to execute
            
        Returns:
            tuple containing (return_code, stdout, stderr)
        """
        try:
            logger.debug(f"Executing command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                logger.warning(f"Command returned non-zero exit code: {result.returncode}")
                logger.debug(f"stderr: {result.stderr}")
            return result.returncode, result.stdout, result.stderr
        except subprocess.SubprocessError as e:
            logger.error(f"Command execution failed: {e}")
            raise DisplayError(f"Command execution failed: {e}")

