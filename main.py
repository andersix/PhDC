# vim:tabstop=4:softtabstop=4:shiftwidth=4:textwidth=79:expandtab:autoindent:smartindent:fileformat=unix:

import signal
import logging

from src.utils.config               import Config
from src.hardware                   import ButtonConfig
from src.controllers.button_manager import ButtonManager
from src.display.manager            import DisplayManager

logger = logging.getLogger('DisplayController')

def main():
    """Pi-Hole Display Main"""
    try:
        # Initialize configuration
        config = Config()

        # Initialize display manager
        display = DisplayManager()

        # Create button manager with display
        manager = ButtonManager(display)

        # Check PADD session exists
        if not display.check_padd():
            logger.error("Failed to find PADD display session")
            return

        def button1_held(hold_time: float):
            """Button 1 hold - open Pi-hole update menu"""
            if not manager.is_menu_active():
                logger.debug("Selected Pi-Hole Menu")
                manager.pihole.show_menu(hold_time)

        def button1_pressed():
            """Button 1 press - cycle brightness or cancel menu"""
            if manager.is_menu_active():
                logger.debug("Button 1 pressed - cancelling confirmation")
                manager.cancel_confirmation()
                return
            try:
                manager.backlight.step_brightness()
                current_brightness = manager.backlight.get_brightness_percentage()
                logger.info(f"Brightness changed to {current_brightness}%")
            except Exception as e:
                logger.error(f"Error handling button 1 press: {str(e)}")

        def button2_held(hold_time: float):
            """Button 2 hold - open system control menu"""
            if not manager.is_menu_active():
                logger.debug("Selected System Menu")
                manager.system.show_menu(hold_time)

        def button2_pressed():
            """Button 2 press - confirm system update or gravity update"""
            if manager.system.is_waiting_for_confirmation():
                logger.debug("In system menu - confirming system update")
                manager.system.request_system_update()
            elif manager.pihole.is_waiting_for_confirmation():
                logger.debug("In Pi-hole menu - confirming Gravity update")
                manager.pihole.request_gravity_update()

        def button3_pressed():
            """Button 3 press - confirm system restart or Pi-hole update"""
            if manager.system.is_waiting_for_confirmation():
                logger.debug("In system menu - confirming restart")
                manager.system.request_reboot()
            elif manager.pihole.is_waiting_for_confirmation():
                logger.debug("In Pi-hole menu - confirming Pi-hole update")
                manager.pihole.request_pihole_update()

        def button4_pressed():
            """Button 4 press - confirm system shutdown or PADD update"""
            if manager.system.is_waiting_for_confirmation():
                logger.debug("In system menu - confirming shutdown")
                manager.system.request_shutdown()
            elif manager.pihole.is_waiting_for_confirmation():
                logger.debug("In Pi-hole menu - confirming PADD update")
                manager.pihole.request_padd_update()

        # Get button configurations from config
        button_configs = config.buttons

        # Configure and add buttons
        buttons_config = [
            (ButtonConfig(**button_configs['1']), button1_pressed, button1_held),
            (ButtonConfig(**button_configs['2']), button2_pressed, button2_held),
            (ButtonConfig(**button_configs['3']), button3_pressed, None),
            (ButtonConfig(**button_configs['4']), button4_pressed, None),
        ]

        # Add all buttons to the manager
        for btn_config, callback, hold_callback in buttons_config:
            manager.add_button(
                config=btn_config,
                callback=callback,
                hold_callback=hold_callback
            )

        logger.info("PiHole Display started successfully")

        # Set up signal handlers
        def cleanup_handler(signum, frame):
            """Handle cleanup on termination signals"""
            logger.info(f"Received signal {signum}, cleaning up")
            try:
                manager.cleanup()
            except NameError:
                logger.warning("Manager not initialized during cleanup")
            exit(0)

        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)

        # Wait for signals indefinitely
        signal.pause()

    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        raise
    finally:
        if 'manager' in locals():
            manager.cleanup()

if __name__ == "__main__":
    main()

