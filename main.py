# vim: set ts=4 sw=4 sts=4 expandtab ai si ff=unix fileencoding=utf-8 textwidth=79:

import time
import logging
from src.utils.config import Config
from src.models import ButtonConfig
from src.controllers.button_manager import ButtonManager
from src.display.manager import DisplayManager

logger = logging.getLogger('DisplayController')

def main():
    """Main application entry point"""
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

        def button1_pressed():
            """Handle button 1 press - control display brightness"""
            if manager.pihole._waiting_for_confirmation:
                manager.pihole.cancel_update()
                return
            try:
                manager.backlight.step_brightness()
                current_brightness = manager.backlight.get_brightness_percentage()
                logger.info(f"Brightness changed to {current_brightness}%")
            except Exception as e:
                logger.error(f"Error handling button 1 press: {str(e)}")
        
        def button2_held(hold_time: float):
            """Handle button 2 hold - delegate to PiHole controller"""
            if not manager.pihole._waiting_for_confirmation:
                manager.pihole.handle_button2_held(hold_time)

        def button2_pressed():
            """Handle button 2 press - gravity update confirmation"""
            if manager.pihole._waiting_for_confirmation:
                manager.pihole.handle_button2_press()

        def button3_held(hold_time: float):
            """Handle button 3 hold - delegate to PiHole controller"""
            if not manager.pihole._waiting_for_confirmation:
                manager.pihole.handle_button3_held(hold_time)

        def button3_pressed():
            """Handle button 3 press - Pi-hole update confirmation"""
            if manager.pihole._waiting_for_confirmation:
                manager.pihole.handle_button3_press()

        def button4_held(hold_time: float):
            """Handle button 4 hold - system control (reboot/shutdown)"""
            if manager.pihole._waiting_for_confirmation:
                manager.pihole.cancel_update()
                return
            manager.system.handle_button4_held(hold_time)

        # Get button configurations from config
        button_configs = config.buttons
        
        # Configure and add buttons
        buttons_config = [
            (ButtonConfig(**button_configs['1']), button1_pressed, None),
            (ButtonConfig(**button_configs['2']), button2_pressed, button2_held),
            (ButtonConfig(**button_configs['3']), button3_pressed, button3_held),
            (ButtonConfig(**button_configs['4']), None, button4_held),
        ]
        
        # Add all buttons to the manager
        for config, callback, hold_callback in buttons_config:
            manager.add_button(
                config=config,
                callback=callback,
                hold_callback=hold_callback
            )
        
        logger.info("Application started successfully")
        
        # Keep the program running
        while True:
            time.sleep(1)  # Just keep main thread alive, no active polling needed
            
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        raise
    finally:
        if 'manager' in locals():
            manager.cleanup()

if __name__ == "__main__":
    main()
