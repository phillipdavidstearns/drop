# Drop

## A Custom Strobe Light Control System

A multi-part system built for the Raspberry Pi, to control modified strobe light kits produced by Chaney Electronics and sold by Electronics Goldmine. Control of an array of strobe lights is done over wifi via web application interface.

### Software components include:

1. [rpi-cd4094](https://github.com/phillipdavidstearns/rpi-cd4094) - An API for controlling CD4094 CMOS 8-bit serial to parallel bus registers.
1. A web application powered by Tornado to provide a GUI control interface powered by Bootstrap.
1. StrobeController - A class that brings together Registers, Counters and Operations to do some interesting (hopefully) things.

### Hardware:

1. Raspberry Pi 3 B+
1. PAU05 - USB WiFi Dongle
1. Strobe trigger/driver circuit
1. Chaney Electronics Strobe Light Kit
1. Custom circuit to allow for +5v pulse triggering of the strobe

#### IGBT Resources:

* [The Insulated Gate Bipolar Transistor (IGBT): A Practical Guide](https://www.build-electronic-circuits.com/igbt-insulated-gate-bipolar-transistor/)
* [IGBT Tutorial](https://www.microchip.com/content/dam/mchp/documents/PSDS/ApplicationNotes/ApplicationNotes/APT0201.pdf)
* [IGBT-basic know-how
IGBT: how does an Insulated Gate Bipolar Transistor work?](https://www.infineon.com/dgdl/Infineon-IGBT_basics_how_does_an_IGBT_work-AdditionalTechnicalInformation-v01_00-EN.pdf?fileId=5546d462700c0ae60170675ed665777f&da=t)
* [IGBT Application Note](https://www.renesas.com/us/en/document/apn/igbt-application-note)

Parts:

* [https://www.mouser.com/datasheet/2/698/REN_r07ds0750ej0100_rjp5001app_DST_20120426-1999273.pdf](https://www.mouser.com/datasheet/2/698/REN_r07ds0750ej0100_rjp5001app_DST_20120426-1999273.pdf)

#### Strobe Circuits:

* [DIY IGBT CONTROLLED 1000WS FLASH UNIT](https://madengineer.ch/blog/2015/08/01/diy-igbt-controlled-1000ws-flash-unit/)
* [FORUM POST: familiar with IGBT? how to use it in a strobe flash circuit?](https://forum.allaboutcircuits.com/threads/familiar-with-igbt-how-to-use-it-in-a-strobe-flash-circuit.5000/)
* [Xenon Strobe Light](https://sound-au.com/project65.htm) - Uses SCR but maybe could be modifed to use IGBT
* [Xenon Strobe Light Control Circuit(s)](https://www.homemade-circuits.com/xenon-strobe-light-control-circuit/)

#### Filtering Trigger Pulses to Thumps:

* [Designing a simple analog kick drum from scratch](https://www.youtube.com/watch?v=yz37Yz315eU)
* [Bridged T Oscillator for Percussion Sounds](https://www.youtube.com/watch?v=C122iDdtnww)
* [Bridged T Electronic Drum Circuit Again](https://www.youtube.com/watch?v=H_ULyfDKN8k)
* [Bridged T Peak Filter - LTSpice Simulation and Audio Tryout](https://www.youtube.com/watch?v=YnnWWfptilM)

## Setup

### Prepare an SD card for the Raspberry Pi using Raspberry Pi Imager

1. Raspi OS Lite
1. Use your favorite configuration for SSH access

### Install Software

1. `sudo apt-get update`
1. `sudo apt-get install -y git python3-pip pigpio python3-pigpio tornado python3-decouple`
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

### Setup WiFi Direct

These steps require the use of a USB WiFi dongle capable of AP mode. The Panda PAU05 WiFi USB dongle does this for about $10.

1. `sudo apt-get install -y dhcpcd hostapd dnsmasq netfilter-persistent iptables-persistent`
1. `sudo systemctl unmask hostapd`
1. `sudo systemctl enable hostapd`
1. `sudo nano /etc/dhcpcd.conf` and add to the end:

```
interface wlan1
    static ip_address=10.10.10.1/24
    nohook wpa_supplicant
```

1. `sudo nano /etc/sysctl.d/routed-ap.conf` to enable packet forwarding

```
net.ipv4.ip_forward=1
```

1. Setup packet routing

```
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save
```

1. `sudo nano /etc/NetworkManager/NetworkManager.conf`


```
[keyfile]
unmanaged-devices=interface-name:wlan1
```

1. make a copy of the default config file: `sudo cp /etc/dnsmasq.conf{,.bak}`
1. configure dnsmasq: `sudo nano /etc/dnsmasq.conf`

```
interface=wlan1
dhcp-range=10.10.10.5,10.10.10.250,255.255.255.0,24h
domain=wlan
address=/gw.wlan/10.10.10.1
# Specify the default route
dhcp-option=3,10.10.10.1
# Specify the DNS server address
dhcp-option=6,10.10.10.1
# Set the DHCP server to authoritative mode.
dhcp-authoritative
```
1. enable wifi just in case `sudo rfkill unblock wlan`
1. `sudo nano /etc/hostapd/hostapd.conf`

```
country_code=US
interface=wlan1
driver=nl80211
ieee80211n=1
wmm_enabled=0
ssid=DropControllerDirect
hw_mode=g
channel=5
macaddr_acl=0
ignore_broadcast_ssid=0

# WPA Authentication
auth_algs=1
wpa=2
wpa_passphrase=A_Super_Secret_Password
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
```

1. Reboot and activate AP with `sudo systemctl start hostapd.service`

## Controls

1. Connect to the WiFi network you setup in the steps above.
1. Navigate to `drop.local` in a browser.

### Register Settings

This system is built around an simple 8-bit register. These controls allow you to set and perform basic manipulations to the register. In order for changes to be updated and pushed to the strobes, the `run` button in the **Timing Control** section must be active.

* `reset` - sets all the register bits to `0`
* `invert` - inverts each bit in the register
* `random` - randomizes all bits in the register
* 8x checks are use to set the state of the register. All check states are pushed on the change of any check.
* `set` - pushes the state of the checks to the register for next update

### Linear Feedback Shift Register Settings (LFSR)

* `enable` - turns this feature on/off. when enabled, any change to the above settings updates all settings to the current state displayed by the gui.
* `direction` - dropdown sets the direction of the shift register
* `flip` - changes the direction of the register to opposite of the direction drop down.

**Taps**

* `enable` - whck checked, updates to the `Q` settings are made live.
* `Q` - selected a register bit, addressed 0-7, to be XOR'd with other enabled Taps and Mod sources and fed into the register.
* `randomize` - randomizes the `Q` value

**Mod**

* `enable` - whck checked, updates to the `Q` and `source` settings are made live.
* `source` - dropdown selects a counter division to use
* `Q` - selected a counter bit, addressed 0-7.
* `randomize` - randomizes the `Q` value

### Strobe Settings

* `update`
* `live`
* `enable`

**Invert**

Inverts the register on each on/off transistion.

* `on` - the amount of transitions until the invert toggles to the on state. 
* `off` - the amount of transitions until the invert toggles to the off state.
* `invert` - enables this section of the strobe mode

**Mute**

Toggles the output enable on each on/off transistion.

* `on` - the amount of transitions to remain enabled. 
* `off` - the amount of transitions to remain disabled.
* `mute` - enables this section of the strobe mode


### Timing Controls

* `duration` - set the duration of each trigger
* `current` - fetches the current duration running and applies it to the gui

...to be continued...

