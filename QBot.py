#!/usr/bin/env python

from qmusic import Qmusic   # Q-music API wrapper

import csv                  # Reading targets
import requests             # Handle HTML stuff
import time                 # Sleeping
import traceback            # Print caught exceptions


class QBot:
    """
    Definition of the bot that is going to listen to Q.
    A new song satisfying a target is posted to a Discord webhook.
    Targets and webhooks are defined in targets.csv
    """

    def __init__(self):
        """
        Initialise with components and urls
        """
        # Listener preparation
        self.sessy = requests.Session()  # Initialise session
        self.qapi = Qmusic()  # Initialise Q-music API wrapper
        self.channel = self.qapi.get_channel()  # Tune in to regular channel
        self.latestCode = ''  # Selector code of last track
        self.sleepPeriod = 180  # By default, sleep for three minutes
        self.targets = []  # List of targets (to be read from targets.csv)
        self.message = 'Message'  # Message to post

    def readTargets(self, targetsCSV):
        """
        Reads the targets.csv file and stores a list where every element is a target dictionary.
        A target consists of a trigger, target and message.

        Args:
            targetsCSV (str): Location of the .csv file that contains the targets.
        """
        # Open and read targets.csv
        with open(targetsCSV, 'r') as tfile:
            csvrows = csv.reader(tfile, delimiter=';')

            # Skip header
            next(csvrows, None)

            # Store remaining rows as targets
            for row in csvrows:
                # Put row contents into dictionary
                rowDict = {'trigger': row[0], 'target': row[1], 'message': row[2]}
                # Print what was read
                print("Read target that is triggered by '{}', sends a notification to '{}' with message '{}'".format( \
                    rowDict['trigger'], rowDict['target'], rowDict['message']))
                # Add the target to the internal targets
                self.targets.append({'trigger': row[0], 'target': row[1], 'message': row[2]})

    def listenToQ(self):
        """
        This function indefinitely lets the bot listen for new songs on Q.
        If a new song is detected, post it to a webhook.
        """
        # Infinite listening loop
        while True:
            # Refresh page and get latest track
            latestTrack = self.channel.current_song()

            # Check if the latest track is new
            if self.trackIsNew(latestTrack):
                # There is a new track, let the update function handle it
                self.handleUpdate(latestTrack)

                # Reset sleeping period and sleep
                self.sleepPeriod = 180
                time.sleep(self.sleepPeriod)
            else:
                # No new track
                self.sleepPeriod = int(self.sleepPeriod / 3) + 10  # Set new sleeping period
                time.sleep(self.sleepPeriod)  # Sleep for that period

    def trackIsNew(self, curTrack):
        """
        Determines whether a track is new (different code).

        Args:
            curTrack (qmusic.Song): Track to compare (whether it is different from the last).

        Returns:
            bool: Whether or not curTrack is different from the last.
        """
        return curTrack.selector_code() != self.latestCode

    def handleUpdate(self, track):
        """
        Logic to determine what to do after an update, based on given targets (triggers).
        For Q, if a new track is recognised, it is printed and if it satisfies a trigger, a notification is posted.

        Args:
            track (qmusic.Song): Latest song.
        """
        # Extract relevant information
        self.latestCode = track.selector_code()
        title = track.title()
        artist = track.artist().name_all_artist().title()
        playtime = track.played_at().time().isoformat()

        # Print the new track first
        self.printUpdate(playtime, title, artist)

        # Check if the track satisfies a trigger
        for target in self.targets:
            # Loop through all targets and check if the track contains the trigger (case-insensitive)
            if target['trigger'].lower() in title.lower() + ' ' + artist.lower():
                # Trigger satisfied, post notification
                self.postNotification(target['target'], target['message'], track.thumbnail_url(),
                                      playtime, title, artist)

    def printUpdate(self, trackTime, title, artist):
        """
        Prints an update to the console.
        For a track the time, song title and artist name is printed.

        Args:
            trackTime (str): Time song was started (hh:mm:ss).
            title (str): Title of the song.
            artist (str): Artist(s) of the song.
        """
        message = 'Nieuw liedje:\nTijd: {}\nTitel: {}\nArtiest: {}'.format(trackTime, title, artist)
        print(message)

    def postNotification(self, hookURL, msgStart, thumbnail, trackTime, title, artist):
        """
        Posts a notification to a provided webhook (url).
        For a track, the title becomes username, thumbnail the avatar,
        artist and time are included in the message.

        Args:
            hookURL (str): URL to post to.
            msgStart (str): Text to start a message with.
            thumbnail (str): URL of thumbnail image.
            trackTime (str): Time at which the track was started (hh:mm:ss).
            title (str): Title of a track.
            artist (str): Artist(s) of a track.
        """
        # Prepare message to display
        message = msgStart + '\nArtiest: {}\nTijd: {}'.format(artist, trackTime)
        # Prepare data to include in post request
        postContent = {'username': title, 'avatar_url': thumbnail, 'content': message}
        # Then post
        self.sessy.post(hookURL, postContent)


# If executed, run bot function
if __name__ == '__main__':

    # Initialise bot
    bot = QBot()
    bot.readTargets('targets.csv')

    # Run bot until process kill (CTRL-C)
    while True:
        # Keep listening, even if an error occurs, just restart
        try:
            bot.listenToQ()
        except Exception as error:
            # Print exception, try to send a notification and restart in 10 seconds
            print(traceback.format_exc() + '\nListener crashed, re-establishing connection...')
            try:
                # Try to send a notification to the first target
                bot.sessy.post(bot.targets[0]['target'],
                               {'content': bot.targets[0]['message'] + '\nError! Opnieuw verbinding aan het maken...'})
            except Exception as postErr:
                # Unable to post notification, really time to restart
                print(traceback.format_exc() + '\nCould not send notification of failure either :(...')
                continue
            time.sleep(10)  # Wait 10 seconds before restarting
            continue
