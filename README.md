# TwitchDesk

TwitchDesk is a program written in Python 3.6 which uses the Twitch API to automatically
notify a desktop user when a Twitch channel goes live. TwitchDesk runs in the background and will poll the API periodically for updates. Note that you will need a registered Twitch application with a Client ID to use this application.


## Basic Usage
To run TwitchDesk, run:
`./twitchdesk.py`
on the startup of your system.

## Setup
A file must be created in the main directory, called `id.txt`.
This file must include only one line, which is a valid Client ID
from a registered Twitch application. (This process is easier than it sounds)

On the first launch, slimeshot will create a file named `id.txt` if it doesn't exist.


## Dependencies
### Packages
-   python3
-   python3-pip (to install Python libs)

### Python Libs
-   request

## Installation

All packages shown above can be installed using the package manager relevent to your distro.
On Debain based systems this would be achieved by running:

`sudo apt-get install python3 python3-pip`

"request" listed must be installed using pip. This can be done by running:

`pip3 install request`
