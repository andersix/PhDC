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

    def show_gravity_update(self) -> bool:
        """
        Show gravity update check and wait for confirmation
        
        Returns:
            bool: True if display switched successfully, False otherwise
        """
        try:
            logger.debug("Switching to control window for gravity update")
            self.tmux.switch_window(self.control_window)
            
            # Clear screen and ensure we're at top
            self._clear_screen()
            
            # Show prompt
            logger.info("Displaying gravity update confirmation prompt")
            print("\n" * 2)  # Add some padding at top
            print("Pi-hole Gravity Update")
            print("----------------------")
            print("\nThis will update Pi-hole's gravity lists.")
            print("This process typically takes a few minutes.")
            print("\nPress Button 2 once to confirm update.")
            print("Waiting 30 seconds for confirmation...")
            print("\nPress any other button or wait 30 seconds to cancel.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in gravity update confirmation: {e}")
            return False

    def show_pihole_update(self) -> bool:
        """
        Show pihole update check and wait for confirmation
        
        Returns:
            bool: True if display switched and check completed successfully
        """
        try:
            logger.debug("Switching to control window for Pi-hole update")
            self.tmux.switch_window(self.control_window)
            
            # Clear screen and ensure we're at top
            self._clear_screen()
            
            # Show update check status
            logger.info("Checking for Pi-hole updates")
            print("\n" * 2)  # Add some padding at top
            print("Checking for Pi-hole Updates")
            print("---------------------------")
            
            # Run update check
            process = subprocess.Popen(
                ['sudo', 'pihole', '-up', '--check-only'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Show real-time output
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
            
            # Get final result
            returncode = process.wait()
            
            if returncode != 0:
                logger.error("Pi-hole update check failed")
                print("\nUpdate check failed!")
                time.sleep(FEEDBACK_DELAY)
                return False
                
            # Show confirmation prompt
            print("\nUpdates are available.")
            print("\nPress Button 3 once to confirm update.")
            print("Waiting 30 seconds for confirmation...")
            print("\nPress any other button or wait 30 seconds to cancel.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in update check: {e}")
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

