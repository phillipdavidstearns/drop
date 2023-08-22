# Drop

## A Custom Strobe Light Control System

A multi-part system built for the Raspberry Pi, to control modified strobe light kits produced by Chaney Electronics and sold by Electronics Goldmine.

### Software components include:

1. [rpi-cd4094](https://github.com/phillipdavidstearns/rpi-cd4094) - An API for controlling CD4094 CMOS 8-bit serial to parallel bus registers.
1. A web application powered by Tornado to provide a GUI control interface.
1. StrobeController - A class that brings together Registers, Counters and Operations to do some interesting (hopefully) things.

### Hardware:

1. Raspberry Pi 3 B+
1. Strobe trigger/driver circuit
1. Chaney Electronics Strobe Light Kit
1. Custom circuit to allow for +5v pulse triggering of the strobe

## Setup

### Prepare an SD card for the Raspberry Pi using Raspberry Pi Imager

1. Raspi OS Lite
1. Use your favorite configuration for SSH access

### Install Software

1. `sudo apt-get update`
1. `sudo apt-get install -y dnsmaq hostapd git python3-pip pigpio python3-pigpio tornado`
1. Navigate to the install directory `cd /usr/local/src`
1. `sudo git clone https://github.com/phillipdavidstearns/drop.git`
1. `sudo git clone https://github.com/phillipdavidstearns/rpi-cd4094.git`
1. `python3 -m pip install -e ./rpi-cd4094`
1. `sudo cp ./drop/drop.service /lib/systemd/system/`
1. You can do all this from the user's home directory, but you'll need to symlink to make the systemd service work `sudo ln -s /home/user/drop /usr/local/src/drop`
1. `sudo systemctl daemon-reload` get systemd to take in the changes
1. `sudo systemctl start pigpiod` fire up the pigpio server daemon
1. `sudo systemctl start drop` start the controller
1. `sudo systemctl status drop` check on it
1. `sudo systemctl enable drop` start on boot if it all looks good
