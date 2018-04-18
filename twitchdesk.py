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
INTERVAL = 120
DEBUG = False

uri = 'https://api.twitch.tv/helix/streams'
rawData = []
channelList = {}


# == Functions

def notify(title, text="", icon=""):
    subprocess.Popen(["notify-send", "-i", icon, title, text])


def error(msg):
    print("ERROR: " + msg)
    if DEBUG:
        notify("ERROR", msg)
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


def update():
    print("update")
    oldList = dict(channelList)
    try:
        liveChannels = requests.get(uri, headers=HEADERS).json()
    except requests.exceptions.HTTPError as err:
        error(err)

    if liveChannels["data"]:
        for liveChannel in liveChannels["data"]:
            desc = liveChannel["title"]
            name = liveChannel["thumbnail_url"].split("live_user_")[1].split("-{width}")[0]
            viewerCount = liveChannel["viewer_count"]
            channelList[name] = True

            try:
                liveProfile = requests.get("https://api.twitch.tv/helix/users?login=" + name, headers=HEADERS).json()["data"][0]
            except requests.exceptions.HTTPError as err:
                error(err)

            displayName = liveProfile["display_name"]
            thumb = liveProfile["profile_image_url"]

            if not download(thumb, "thumb/" + name + ".png"):
                error("Could not download profile image from Twitch!")

            if not oldList[name]:
                notify(displayName + " is now online on Twitch!", desc + "\nViewers: " + str(viewerCount), HERE + "/thumb/" + name + ".png")
    else:
        error("Twitch API returned no data!")


# == Main Body

if os.path.exists("id.txt"):   # Reads key from id.txt if no errors
    try:
        keyFile = open("id.txt", "rb")
        KEY = keyFile.read().decode().replace("\n","")
        HEADERS = {'Accept' : 'application/vnd.twitchtv.v5+json', 'Client-ID': KEY}
        keyFile.close()
    except IOError as e:
        error("IOError: " + e)
else:   # Display error and create new file if id.txt doesn't exist
    with open("id.txt", "w"): pass
    error("Please add a Twitch Client ID to your id.txt file!")


if os.path.exists("channels.txt"):
    try:
        channelFile = open("channels.txt", "rb")
        rawChannelList = channelFile.read().decode().split("\n")
        channelFile.close()
    except IOError as e:
        print("IOError: " + e)
else:
    with open("channels.txt", "w"): pass
    error("A channel.txt file was not found, so one was created.")

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

while True:
    update()
    print("Waiting " + str(INTERVAL) + " seconds")
    time.sleep(INTERVAL)
