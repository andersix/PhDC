#!/bin/bash

# If we're on the PiTFT screen (ssh is xterm)
if [ "$TERM" == "linux" ] ; then
    # Create or attach to tmux session
    if ! tmux has-session -t padd 2>/dev/null; then
        # Create new session with first window running PADD
        tmux new-session -d -s padd -n padd '/home/pi/PADD/padd.sh'
        
        # Disable status line
        tmux set-option -t padd status off
        
        # Create second window for Python app
        tmux new-window -t padd:1 -n control '/usr/bin/python3 /home/pi/pihole_display/main.py'
        
        # Select PADD window as default
        tmux select-window -t padd:padd
    fi
    
    # Attach to session if we're on tty1
    if [ "$(tty)" == "/dev/tty1" ]; then
        exec tmux attach-session -t padd
    fi
fi

