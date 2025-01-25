#!/bin/bash

# Source configuration
if [ -f /home/pi/pihole_display/config/config.yaml ]; then
    # Using default values if not found in config
    PADD_SCRIPT=${PADD_SCRIPT:-"/home/pi/PADD/padd.sh"}
    PYTHON_PATH=${PYTHON_PATH:-"/usr/bin/python3"}
    MAIN_SCRIPT=${MAIN_SCRIPT:-"/home/pi/pihole_display/main.py"}
fi

# If we're on the PiTFT screen (ssh is xterm)
if [ "$TERM" == "linux" ] ; then
    # Create or attach to tmux session
    if ! tmux has-session -t display 2>/dev/null; then
        # Create new session with first window running PADD
        tmux new-session -d -s display -n padd "${PADD_SCRIPT}"
        
        # Disable status line
        tmux set-option -t display status off
        
        # Create second window for Python app
        tmux new-window -t display:1 -n control "${PYTHON_PATH} ${MAIN_SCRIPT}"
        
        # Select PADD window as default
        tmux select-window -t display:padd
    fi
    
    # Attach to session if we're on tty1
    if [ "$(tty)" == "/dev/tty1" ]; then
        exec tmux attach-session -t display
    fi
fi

