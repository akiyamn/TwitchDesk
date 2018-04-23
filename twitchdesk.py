#!/usr/bin/python3
import requests
import sys
import os
import subprocess
import time

# == Variables

__version__ = "1.0.0"

KEY = ""
HEADERS = ""
HERE = os.path.dirname(os.path.realpath(__file__))
INTERVAL = 180
DEBUG = False
SOUND = True

uri = 'https://api.twitch.tv/helix/streams'
rawData = []
channelList = {}

try:
    from playsound import playsound
except ImportError as e:
    from dummy_playsound import *
    print("WARNING: playsound module not found, sound will not play.")
    SOUND = False


# == Functions

def absPath(path):
    return HERE +  "/" + path


def notify(title, text="", icon="", ):
    subprocess.Popen(["notify-send", "-i", icon, title, text])
    if DEBUG:
        print(title + "\n" + text)


def error(msg):
    if DEBUG:
        notify("ERROR", msg)
    else:
        print("ERROR: " + msg)
    sys.exit(1)


def download(url, filename):
    path = absPath(filename)
    if not os.path.isfile(path):
        dlResponse = requests.get(url)
        if dlResponse.status_code == 200:
            with open(path, 'wb') as f:
                f.write(dlResponse.content)
                print("Downloading " + url + " to " + path)
            return True
        else:
            return False
    else:
        print("Reading from " + path)
        return True


def readFile(filename):
    path = absPath(filename)
    if os.path.exists(path):
        try:
            file = open(path, "r")
            output = file.read()
            print(path)
            file.close()
            return output
        except IOError as e:
            error("IOError: " + e)
    else:   # Display error and create new file if doesn't exist
        with open(filename, "w"): pass
        return ""


def sound(file):
    if not SOUND:
        return
    playsound(absPath(file))


def update():
    print("Update")
    oldList = dict(channelList)
    try:
        r = requests.get(uri, headers=HEADERS)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        error(str(err))
    liveChannels = r.json()

    if liveChannels["data"]:
        for liveChannel in liveChannels["data"]:
            desc = liveChannel["title"]
            name = liveChannel["thumbnail_url"].split("live_user_")[1].split("-{width}")[0]
            viewerCount = liveChannel["viewer_count"]
            channelList[name] = True

            if not oldList[name]:
                try:
                    liveProfile = requests.get("https://api.twitch.tv/helix/users?login=" + name, headers=HEADERS).json()["data"][0]
                except requests.exceptions.RequestException as err:
                    error(str(err))

                displayName = liveProfile["display_name"]
                thumb = liveProfile["profile_image_url"]

                if not download(thumb, "thumbs/" + name + ".png"):
                    error("Could not download profile image from Twitch!")

                notify(displayName + " is now online on Twitch!", desc + "\nViewers: " + str(viewerCount), HERE + "/thumbs/" + name + ".png")
                sound("notify.wav")


# == Main Body

KEY = readFile("id.txt").replace("\n","")

if KEY:
    HEADERS = {'Accept' : 'application/vnd.twitchtv.v5+json', 'Client-ID': KEY}
else:
    error("Please add a Twitch Client ID to your id.txt file! Aborting...\n")

rawChannelList = readFile("channels.txt").split("\n")
if not rawChannelList:
    error("A channel.txt file was not found, so one was created. Aborting...")

thumbDir = absPath("thumbs")
if not os.path.exists(thumbDir):
    os.makedirs(thumbDir)

for channel in rawChannelList:
    if channel != "":
        channelList[channel] = False

if len(channelList) == 0:
    error("Channel.txt file is empty!")

seperator = "?"
i = 0
for channel in channelList:
    if i != 0:
        seperator = "&"
    uri += seperator + "user_login=" + channel
    i += 1

# == Main Loop

escape = False
while not escape:
    try:
        update()
        print("Waiting " + str(INTERVAL) + " seconds...")
        time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nExitting...")
        escape = True
