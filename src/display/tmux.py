# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:smartindent:fileformat=unix:

from pathlib import Path
import subprocess
import logging
from ..utils.exceptions import DisplayError
from ..utils.config import Config
from ..utils.constants import PADD_SCRIPT_PATH

logger = logging.getLogger('DisplayController')

class TMuxController:
    """Manages tmux sessions and windows"""

    def __init__(self):
        """Initialize TMux controller with configuration"""
        self.config = Config().display.get('tmux', {})
        self.padd_path = PADD_SCRIPT_PATH
        self.session_name = self.config.get('session_name', 'display')
        self._verify_tmux_available()

    def _verify_tmux_available(self) -> None:
        """Verify tmux is installed and available"""
        try:
            subprocess.run(['tmux', '-V'], capture_output=True, check=True)
            logger.debug("Tmux is available")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            error_msg = "Tmux is not available on the system"
            logger.critical(error_msg)
            raise DisplayError(error_msg)

    def _run_tmux_command(self, command: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a tmux command with proper error handling

        Args:
            command: List of command components
            check: Whether to raise on non-zero exit

        Returns:
            CompletedProcess instance

        Raises:
            DisplayError: If command fails and check is True
        """
        try:
            full_command = ['tmux'] + command
            logger.debug(f"Running tmux command: {' '.join(full_command)}")
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.SubprocessError as e:
            error_msg = f"Tmux command failed: {str(e)}"
            logger.error(error_msg)
            if check:
                raise DisplayError(error_msg)
            return e.returncode

    def create_session(self) -> bool:
        """
        Create a new tmux session with proper windows

        Returns:
            bool: True if session created or already exists
        """
        try:
            # Check if session already exists
            if self.has_session():
                logger.debug(f"Session {self.session_name} already exists")
                return True

            logger.info(f"Creating new tmux session: {self.session_name}")

            # Create new session with PADD
            self._run_tmux_command([
                'new-session',
                '-d',  # Create in detached state
                '-s', self.session_name,  # Session name
                '-n', 'padd',  # Initial window name
                str(self.padd_path)  # PADD script
            ])

            # Disable status line
            self._run_tmux_command([
                'set-option',
                '-t', self.session_name,
                'status', 'off'
            ])

            # Create control window
            self._run_tmux_command([
                'new-window',
                '-t', f'{self.session_name}:1',
                '-n', 'control'
            ])

            # Switch back to PADD window
            self._run_tmux_command([
                'select-window',
                '-t', f'{self.session_name}:padd'
            ])

            logger.info(f"Successfully created tmux session: {self.session_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create tmux session: {str(e)}")
            raise DisplayError(f"Failed to create tmux session: {str(e)}")

    def send_command(self, target: str, command: str) -> bool:
        """
        Send a command to a tmux session/window

        Args:
            target: Target session:window
            command: Command to send

        Returns:
            bool: True if command sent successfully
        """
        try:
            if not self.has_session():
                logger.error("Cannot send command - session doesn't exist")
                return False

            self._run_tmux_command([
                'send-keys',
                '-t', target,
                command, 'Enter'
            ])
            return True

        except Exception as e:
            logger.error(f"Failed to send command to {target}: {str(e)}")
            return False

    def switch_window(self, window_name: str) -> None:
        """
        Switch to specified window with verification

        Args:
            window_name: Name of window to switch to

        Raises:
            DisplayError: If switch fails or window doesn't exist
        """
        try:
            # Verify window exists
            result = self._run_tmux_command(
                ['list-windows', '-t', self.session_name],
                check=False
            )

            if result.returncode != 0 or not any(
                window_name in line for line in result.stdout.splitlines()
            ):
                raise DisplayError(f"Window {window_name} not found")

            # Perform switch
            self._run_tmux_command([
                'select-window',
                '-t', f'{self.session_name}:{window_name}'
            ])

            # Verify switch
            current = self._run_tmux_command([
                'display-message',
                '-p', '#W'  # Current window name
            ])

            if current.stdout.strip() != window_name:
                raise DisplayError("Window switch verification failed")

            logger.debug(f"Successfully switched to window: {window_name}")

        except Exception as e:
            error_msg = f"Failed to switch to window {window_name}: {str(e)}"
            logger.error(error_msg)
            raise DisplayError(error_msg)

    def has_session(self) -> bool:
        """
        Check if session exists with improved error handling

        Returns:
            bool: True if session exists
        """
        try:
            result = self._run_tmux_command(
                ['has-session', '-t', self.session_name],
                check=False
            )
            exists = result.returncode == 0
            logger.debug(f"Session {self.session_name} exists: {exists}")
            return exists
        except Exception:
            logger.error(f"Error checking session {self.session_name}")
            return False


