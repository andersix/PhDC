# PiHole Display Controller

A Python application for controlling a PiHole instance running on a Raspberry Pi with an Adafruit 2.8" PiTFT Plus display. This application manages display brightness, PiHole updates, and system controls through hardware buttons.

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- Adafruit 2.8" PiTFT Plus (capacitive touch)
- 4 GPIO buttons configured on pins:
  - Button 1 (GPIO17): Display brightness control
  - Button 2 (GPIO22): PiHole gravity update
  - Button 3 (GPIO23): PiHole system update
  - Button 4 (GPIO27): System control (reboot/shutdown)

## Software Requirements

- Raspberry Pi OS
- Python 3.9+
- PiHole installed and configured
- PADD monitoring script installed
- tmux

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/pihole_display.git
cd pihole_display






Configuration
Configuration is managed through config/config.yaml. Key configuration options include:

Display backlight settings (PIN, PWM frequency, gamma correction)
Button configurations (pins, hold times, functions)
TMux session settings
Logging configuration

Usage
Button Functions

Button 1 (GPIO17):

Press to cycle display brightness (100% to 0% in 10% steps)
Gamma correction applied for smooth transitions


Button 2 (GPIO22):

Hold for 1 second to initiate gravity update
Press again to confirm update within 30 seconds
Real-time update progress displayed


Button 3 (GPIO23):

Hold for 2 seconds to check for PiHole updates
Press again to confirm update within 30 seconds
Real-time update progress displayed


Button 4 (GPIO27):

Hold 2-5 seconds and release for system reboot
Hold 5+ seconds and release for system shutdown



Display Windows
The application uses tmux to manage two windows:

Main window: Displays PADD monitoring interface
Control window: Shows update progress and confirmation prompts

Logging
Logs are stored in the log directory with automatic rotation:

Maximum file size: 1MB
Keeps last 5 log files
Includes debug information and error tracking

Error Handling
The application includes comprehensive error handling for:

Hardware initialization failures
Button press/hold events
Update processes
Display management
System operations

Support
For issues and feature requests, please create an issue in the GitHub repository.


