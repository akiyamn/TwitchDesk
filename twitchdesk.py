#!/usr/bin/python3
import requests
import sys
import os
import subprocess
import time


# == Variables

KEY = ""
HEADERS = ""
HERE = os.path.dirname(os.path.realpath(__file__))
INTERVAL = 180
DEBUG = False

uri = 'https://api.twitch.tv/helix/streams'
rawData = []
channelList = {}


# == Functions

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
    if not os.path.isfile(filename):
        dlResponse = requests.get(url)
        if dlResponse.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(dlResponse.content)
                print("Downloading " + url + " to " + filename)
            return True
        else:
            return False
    else:
        print("Reading from " + filename)
        return True


def readFile(filename):
    if os.path.exists(filename):
        try:
            file = open(filename, "r")
            output = file.read()
            file.close()
            return output
        except IOError as e:
            error("IOError: " + e)
    else:   # Display error and create new file if doesn't exist
        with open(filename, "w"): pass
        return ""



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

            try:
                liveProfile = requests.get("https://api.twitch.tv/helix/users?login=" + name, headers=HEADERS).json()["data"][0]
            except requests.exceptions.RequestException as err:
                error(str(err))

            displayName = liveProfile["display_name"]
            thumb = liveProfile["profile_image_url"]

            if not download(thumb, "thumb/" + name + ".png"):
                error("Could not download profile image from Twitch!")

            if not oldList[name]:
                notify(displayName + " is now online on Twitch!", desc + "\nViewers: " + str(viewerCount), HERE + "/thumb/" + name + ".png")


# == Main Body

KEY = readFile("id.txt").replace("\n","")
if KEY:
    HEADERS = {'Accept' : 'application/vnd.twitchtv.v5+json', 'Client-ID': KEY}
else:
    error("Please add a Twitch Client ID to your id.txt file! Aborting...")

rawChannelList = readFile("channels.txt").split("\n")
if not rawChannelList:
    error("A channel.txt file was not found, so one was created. Aborting...")


if not os.path.exists("thumb"):
    os.makedirs("thumb")

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
