# Pi-hole Display

## Introduction
The Pi-hole Display Controller is a Python application designed to run on a Raspberry Pi with an attached LCD display. It provides a user interface for monitoring Pi-hole statistics and performing system maintenance tasks through physical button controls. The application works in conjunction with the Pi-hole Admin Display Dashboard (PADD) to provide both visual feedback and control capabilities.


This is a python module and companion systemd service file,
performing useful functions using the four built-in buttons
on the PiTFT 2.8" Plus 320x240 TFT display panel PCB.

I use this display on a running Pi-Hole to display the Pi-Hole status.
The buttons are used for things like dimming the display, updating, and
restarting or shuting down the Pi for maintenance, etc.

<img src="https://github.com/andersix/pitft_buttons/blob/main/doc/img/PiHole_TFT_buttons.jpg" style=" width:480px; " >

## Use

The code in pitft_buttons.py determines what each button's function is.

The PiTFT 2.8" display has four buttons on GPIO 17, 22, 23, and 27.
In the python code, they are button0, button1, button2, and button3 respectively.
  
#### Button Functions (From top to bottom)

* Button 0, top-most button (GPIO 17):
  - Dim display backlight by 1/8th of full brightness for each press until display reaches "off" state.
    - When in the "off" state, the next button press turns display backlight back to full brightness.
      The PiTFT backlight LEDs are connected to GPIO 18. Brightness is set by PWM to this GPIO. The PWM is gamma-corrected so the 1/8th steps "look good".

* Button 1 (GPIO 22):
  - Run the Pi-Hole system updater
    - Press and hold button for one second when you see the display showing "Updates are available".
      The update function checks to see if an update is needed, and does nothing
      if the PiHole is already up-to-date.
      Release button when the display begins flashing, indicating the the updater is checking and/or running.
      Results are logged in syslog, so use journalctl, and/or check /var/log/messages, for results.

* Button 2 (GPIO 23):
  - Run the Pi-Hole gravity database updater
    - Press and hold button for one second when you have added or changed Ad-lists and need to update Pi-Hole DBs.
      Release the button when the display begins flashing, indicating the gravity updater is running.
      Results are logged in syslog, so use journalctl, and/or check /var/log/messages, for results.

* Button 3 (GPIO 27):
  - Restart or Shutdown
    - To Restart Pi, press and hold for more than 2 seconds, but less than 5 seconds.
    - To Shutdown Pi, press and hold for more than 5 seconds.
    - NOTE: The display will "blink" to indicate what will happen when you release button.
            When you see:
      * one blink, releasing button will restart Pi
      * a second blink, releasing button will shutdown Pi


## Requirements

### Hardware

* A Raspberry Pi (tested on a model 3B and 3B+)

* Display and enclosure---modify/customize enclosure as you prefer, this is what I did:
  - Adafruit PiTFT Plus 320x240 2.8" TFT (assembled with four buttons on the side.)
    - https://www.adafruit.com/product/2423
  - Faceplate and Buttons Pack for 2.8" PiTFTs
    - https://www.adafruit.com/product/2807
  - Pi Model B+ / Pi 2 / Pi 3 - Case Base and Faceplate Pack - Clear - for 2.8" PiTFT
    - https://www.adafruit.com/product/3062

<img src="https://github.com/andersix/pitft_buttons/blob/main/doc/img/PiTFT_buttons_parts.jpg" style=" width:480px; " >



### Software

* Raspberry Pi OS Lite
  - Tested on: "Raspbian GNU/Linux 10 (buster)"
  - https://www.raspberrypi.org/software/operating-systems/

* Python 3

* git

* Adafruit Raspberry Pi Installer scripts
  - https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi

* Pi-Hole (optional, but this is what I'm using it for)
  - padd.sh for status display

* python3-gpiozero package
  - Tested on Version: 1.5.1, or later
  - Homepage: http://gpiozero.readthedocs.io/

* pitft_buttons
  - this repository!

## Installation

### Hardware

#### PiTFT Plus 2.8" TFT connected to Pi 40-pin GPIO connector

<img src="https://github.com/andersix/pitft_buttons/blob/main/doc/img/PiTFT_plugin.jpg" style=" width:480px; " >

### Software

#### PiHole
* Install PiHole and get it up and running for your network
  - https://docs.pi-hole.net/main/basic-install/
* If you already have PiHole running, move along...

#### pip3
If you don't have pip3, install it with
```
sudo apt install python3-pip
```

#### Git
If you don't have git, install it with
```
sudo apt install git
```

#### GitPython
If you don't have git python, install it with
```
sudo pip3 install GitPython
```

#### gpiozero
If you don't have gpiozero, install it with
```
sudo apt install python3-gpiozero
```
or
```
sudo pip3 install gpiozero
```
#### Get pitft buttons (this repository)
```
cd ~
git clone https://github.com/andersix/pitft_buttons.git
```

#### pigpio
If you don't have pigpio, install it with
```
sudo apt install pigpio
```
* enter ```sudo raspi-config``` on the command line, and enable Remote GPIO.
  - select "3 Interface Options", then "P8 Remote GPIO", then "Yes" to enable.
  - select OK then Finish to exit raspi-config
* link the pigiod.service file to the systemd directory
  - ```cd ~/pitft_buttons```
  - ```sudo ln -s /home/pi/pitft_buttons/pigpiod.service /etc/systemd/system/```
* enable and start the gpio service
  - ```sudo systemctl enable pigpiod```
  - ```sudo systemctl start pigpiod```
  - NOTE: starting and enabling the pigpiod service will not allow remote connections unless configured accordingly, but that's OK since we're only using it locally.

#### Get the Adafruit installer scripts for the PiTFT:
```
cd ~
sudo pip3 install --upgrade adafruit-python-shell click==7.0
sudo apt-get install -y git
git clone https://github.com/adafruit/Raspberry-Pi-Installer-Scripts.git
cd Raspberry-Pi-Installer-Scripts
```

#### Pick the appropriate installer
I'm using the PiTFT 2.8 Capacitive, so am using:
```
sudo python3 adafruit-pitft.py --display=28c --rotation=90 --install-type=console
```
* for other displays, or details, check here:
  - https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install-2
  
#### Reboot and return to here
Once the PiTFT script is installed, reboot your Pi, and return to the next step below.

#### Change the console font
* Edit the /boot/cmdline.txt file and to the end of the line, after "rootwait", add:
```
fbcon=map:10 fbcon=font:VGA8x8
```
Save the file, and it should have
```
$ cat /boot/cmdline.txt
console=serial0,115200 console=tty1 root=PARTUUID=XXXXXXXX-XX rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait fbcon=map:10 fbcon=font:VGA8x8
```
(NOTE: don't change the value for the PARTUUID in your cmdline.txt file)

##### Improve console font
Run the command
```
sudo dpkg-reconfigure console-setup
```
and go select the following options to get Terminus 6x12
* Encoding:
  - UTF-8
* Character set to support:
  - Guess optimal character set
* Font for the console:
  - Terminus
* Font size:
  - 6x12 (framebuffer only)

#### Install padd.sh
I'm using this for PiHole status display, so let's use padd.sh
```
cd ~
git clone https://github.com/pi-hole/PADD.git
```
Then have padd.sh launch at boot time:

Edit the pi users ~/.bashrc and at the bottom put:
```
# Run PADD
# If we're on the PiTFT screen (ssh is xterm)
if [ "$TERM" == "linux" ] ; then
  while :
  do
    ./PADD/padd.sh
    sleep 1
  done
fi
```

#### Reboot and return to here
After this reboot, the dipslay should show the PADD status screen for your PiHole.

Now let's get the buttons code working:

#### Link pitft buttons script and systemd service
```
cd ~/pitft_buttons
chmod +x pitft_buttons.py
sudo ln -s ~/pitft_buttons/pitft_buttons.py /usr/local/bin/.
sudo ln -s ~/pitft_buttons/pitft_buttons.service /etc/systemd/system/.
sudo systemctl enable pitft_buttons.service
sudo systemctl start pitft_buttons.service
```
That's it. The buttons should be working as described above. If you have issues, see the Troubleshooting section.

## Troubleshooting

* Check the status of the GPIOD service with the command:
  ```
  $ sudo systemctl status pigpiod.service
  ```
  - This should produce output similar to:
    ```
    ● pigpiod.service - Pigpio daemon
       Loaded: loaded (/home/pi/pitft_buttons/pigpiod.service; enabled; vendor preset: enabled)
       Active: active (running) since Fri 2022-05-13 16:18:03 MDT; 15h ago
      Process: 497 ExecStart=/usr/bin/pigpiod -m -n localhost (code=exited, status=0/SUCCESS)
     Main PID: 512 (pigpiod)
        Tasks: 5 (limit: 1716)
       CGroup: /system.slice/pigpiod.service
               └─512 /usr/bin/pigpiod -m -n localhost
    ```

* Check the status of the PITFT program at any time with the command:
  ```
  sudo systemctl status pitft_buttons.service
  ```
  - This should produce output similar to:
    ```
    ● pitft_buttons.service - PiTFT GPIO buttons
       Loaded: loaded (/home/pi/PiTFT28_buttons/pitft_buttons.service; enabled; vendor preset: enabled)
       Active: active (running) since Wed 2020-12-02 21:33:39 MST; 21h ago
     Main PID: 609 (python3)
        Tasks: 5 (limit: 1601)
       CGroup: /system.slice/pitft_buttons.service
               └─609 /usr/bin/python3 /usr/local/bin/pitft_buttons.py
    ```
You should have "Active: active (running)".
If not check
 * for syntax errors in python code, if you modified it.
 * python file location
 * python and/or service file permissions
 * check journald logs using ```journalctl``` for an errors involving this script

## Updates
* **2022-5-09**
  Now using the pigpio factory. Why? I was annoyed that the PWMLED would _flash_, or _glitch_ the display backlight randomly when dimmed. By changing to the pigpio factory, this annoying glitch goes away (if you can think of a better way, let me know, but this works.)
  - To get this update, you will need to install and start the pigpio service as described above in the Software, [pigpio section](#pigpio)
  - Script now uses [Git Python](#GitPython) to pull updates for PADD, so install that if you don't already have it. Also make sure your PADD is a clone from the pi-hole repo, see [PADD section](#install-paddsh).
  - also updated buttons 1 and 2 to press-and-hold for 1 second

* When there are updates to this project, and you want them, just pull them.
  ```
  cd ~/pitft_buttons
  git pull
  sudo systemctl stop pitft_buttons.service
  sudo systemctl start pitft_buttons.service
  ```

## Modifications and Improvements

Submit pull requests. Go for it. You can do it.
