# Introduction
This library enables streaming, in real time, of Intellivue patient monitor data from a Rasperry Pi to a Desktop Computer. The Raspberry Pi handles the serial connection with the monitor itself, simply collecting and sending the data over a grpc connection.

This is a powerful solution as it allows for hardware decoupling of monitor data collection and processing.

The python code that processes the data is computationally expensive, whereas the collection (and subsequent serialization and transmission) of the source data is relatively much simpler.

GRPC enables collection of serial data using a small device suited to the task of hardware I/O, that then streams it to a larger one, where the further processing and can be done (streaming to a web service for display on a portal, for instance (: ).

The beauty is that the devices, one collecting and the other processing, do not have to be in the same place, much less the same network. Multiple collection devices can be set up to stream to the same central device, limited only by its processing power and open ports.

The initial testing and development of this solution was done on a LAN for purposes of verification and simplicity, and that is what will be referenced below. Further work will be required to industrialize and de-centralize the collector-processor connection, but the Proof-of-Concept is functioning to allow this future development.

## Pre-requisites, setup
A router + internet connection (internet connection is only for setup)
A computer running \*nix shell (intellivue-grpc was tested using Ubuntu 18.04)
A Raspberry Pi (herein RPi) (latest model is best, 3+, for perfomance reasons)
    ( In theory, any micro-computer running Linux will work, as long as it has a serial [RS232] interface and internet connectivity)
These instructions will refer to the tested devices/environment, for simplicity's sake, and because that is where functionality was verified

For reference, the specs of the devices tested on are below:
Desktop - 
OS: Ubuntu 18.04.3 LTS (bionic) 64 bit
CPU: Intel Core i7-7700K CPU @ 4.20GHz × 8 
Memory: 32 GB

RPi -
Model: 3 B+ 2017
OS: Raspbian Release 10 (buster)
CPU: ARM Cortex-A53 model 4 1.4Ghz x 4
Memory: 1GB

Monitor:
Model: Intellivue MP50
Part Number: M8004A
Sw-Rev: H.14.41
HW-Rev: A.00.12
- find Sw and Hw rev under Main Setup > Revisions > Product
Serial Card: 

The instructions will also assume the following, and the requisite setup steps, without describing them in detail as it may be out of scope and there are also many ways to fulfill the requirements

1. The RPi can connect to the internet
2. The RPi can be connected to the same router as the computer (will be required for grpc functionality) 
3. A RS232 to USB cable (for connecting Intellivue monitor to RPi) (instructions for setup of cable separate, requires cable + serial connector)
4. Not required, but recommended that the RPi has ssh access enabled. This will prevent the desktop client from potentially affecting functionality when the collection is running.

## Steps to Set Up Environment
The intellivue code requires a python 2.7.16+ environment with certain packages installed. In the ideal scenario both computer and RPi have python 2.7.16+ as the base python. (i.e. python --version shows Python 2.7.16). However in reality, this is not often the case. The RPi can be easily controlled, wiped, and replaced, but with desktop environments the same cannot be said.

Thus, there are two recommended sets of instructions - one for the RPi and the other for the computer. I highly recommend following the desktop steps for even other projects, and wish I had known about it before I started down the long and frustrating rabbit hole that is python environments. It may make your life easier at most, and at the least will allow testing of this project without spending hours resolving python issues.

1. Device enivronment setup
#### RPi setup
For GRPC Purposes, the Raspberry Pi is a static and dedicated device, so setup will only need to be run once and there will be no other python environments, besides the grpc one, necessary. If the Raspbian OS version Buster is used, then the system python version defaults to 2.7.16, which is enough for the code to run. Thus, to setup the Python environment on the RPi, run (assuming fresh install):

```
cd ~

# Basic setup
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install setserial
sudo apt-get install python-pip
sudo apt-get install python-numpy python-scipy python-matplotlib

# python package setup
git clone https://github.com/brarm/intellivue.git
cd intellivue
git checkout feature/grpc
pip install -U -r intellivue/requirements.txt

# virtualenv setup
echo PATH="/home/pi/.local/bin:$PATH" >> ~/.bashrc
source ~/.bashrc
mkdir ~/envs
mkvirtualenv --system-site-packages ~/envs/intell-grpc/
echo "WORKON\_HOME=/home/pi/envs" >> ~/.profile
echo "source /home/pi/.local/bin/virtualenvwrapper.sh" >> ~/.profile
```

### Desktop Setup
These steps have been tested on Ubuntu, with with python verion=2.x

```
# Install pyenv
# ref - https://github.com/pyenv/pyenv-installer
curl https://pyenv.run | bash

echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc

# will also likely need to get dependencies for running pyenv install
sudo apt-get update -yq
sudo apt-get install -yq make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# Check that pyenv install worked with
pyenv --version

# If installed ok, run
pyenv update
pyenv install 2.7.16    # This may take a while, don't be worried. It's building the selected python version from source

# install pip, if not already
sudo apt install python-pip

# Install pipenv
pip install --upgrade pip
pip install --user pipenv

# Clone intellivue repo and install required packages into a new pipenv
git clone https://github.com/brarm/intellivue
cd intellivue
git checkout feature/grpc
pipenv --python 2.7.16      # Creates a virutal environment, using the python installed with pyenv above as the base python. Also creates a Pipfile from requirements.txt
pipenv shell                # starts a subshell in your current, inside the virtual environment
pipenv install              # Install all necessary packages. These will only be available in this virtual environment, so no need to worry about package versions affecting system packages or the like

# confirm packages installed in virtual environment with
pip list

# should match the contents of 
cat requirements.txt

# leave the virtual environment anytime with
exit

# enter it again by doing a
cd intellivue
pipenv shell
```

2. Plug the serial cable in. (Serial end to back of Intellivue Monitor, USB to RPi
3. Confirm connection with the following
```
ls -alF /sys/class/tty/ttyUSB\*
```

The number after USB will differ based on the controller that the Serial-to-USB manufacturer uses. For the tested adapter, the device maps to ttyUSB0

Can further confirm the serial device with
```
ls /dev/serial/by-id
```

Which should show a device like usb-FTDI_FT232R_USB_UART

Note down the specific device port (like ttyUSB0) as it will be used later on

4. Now, connect the RPi to the same router as the computer, if not already
Initial testing was done using a dedicated, 'airgapped', router, again for simplicity and also to mitigate any potential transmission aberrations that might have been introduced over an actual router serving 20-odd home devices and with settings configured by the ISP. 

5. Note down the local IP addresses of both devices, for which ```ifconfig``` comes in handy. You will need the 'inet' value of the network the device is currently using.
For instance, the RPi is using wlan0, and the inet address is ```192.168.1.5```
The desktop, connected to the same router, is using wlp4s0, and the inet address is ```192.168.1.3```

To verify connectivity between the devices, can run:
From the desktop
```
desktop $: ping <address of RPi>
# eg 
desktop $: ping 192.168.1.5
# which outputs something like
PING 192.168.1.5 (192.168.1.5) 56(84) bytes of data.
64 bytes from 192.168.1.5: icmp_seq=1 ttl=64 time=1033 ms
64 bytes from 192.168.1.5: icmp_seq=2 ttl=64 time=17.9 ms
64 bytes from 192.168.1.5: icmp_seq=3 ttl=64 time=6.41 ms
```
and from the RPi:
```
raspberrypi $: ping <address of desktop>
# eg
raspberrypi $: ping 192.168.1.3
# which outputs something similar to the first ping command
```

6. After verifying that both devices can ping each other do the following
### On the desktop
- Find the file intellivue/TelemetryStream/client.py
- In that file, change the variable ```address``` at the top of the file to = '<address of raspberry pi>
Using above context, the line would look like
```
address = '192.168.1.5'
```

Ensure also that the ```port``` value in client.py matches the port value in
~/intellivue/TelemetryStream/server.py on the RPi


on the RPi run
```
workon intell-grpc
python ~/intellivue/TelemetryStream/server.py
```

Then, on the desktop, run:
```
python PhilipsTelemetryStream.py --values Pleth 128 ECG 256 --port /dev/<serial device port>
```
using the serial device port from the RPi 
Following the example context, this would looke like
```
python PhilipsTelemetryStream.py --values Pleth 128 ECG 256 --port /dev ttyUSB0
```

The monitor waveform values should begin printing to your desktop screen


