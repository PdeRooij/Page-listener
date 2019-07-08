#!/usr/bin/env python

"""A simple python script template.
"""

"""
from __future__ import print_function
import os
import sys
import argparse


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile', help="Input file", type=argparse.FileType('r'))
    parser.add_argument('-o', '--outfile', help="Output file",
                        default=sys.stdout, type=argparse.FileType('w'))

    args = parser.parse_args(arguments)

    print(args)

"""

import csv
import requests					# Handle HTML stuff
from bs4 import BeautifulSoup	# Parse HTML stuff
from datetime import datetime	# Handle time stuff
import time						# Sleeping

"""
Definition of the bot that is going to listen to Q.
Every new song is posted to a Discord webhook.
"""
class QBot():
	
	# Initialise with components and urls
	def __init__(self):
		self.sessy = requests.Session()					# Initialise session
		self.soupy = BeautifulSoup						# For parsing responses
		self.url = "https://qmusic.nl/playlist/qmusic"	# Url to get
		self.sleepPeriod = 180							# By default, sleep for three minutes
		self.targets = []								# List of targets (to be read from targets.csv)
		self.message = 'Message'						# Message to post
	
	# Reads the targets.csv file and stores a list where every element is a target dictionary.
	# A target consists of a trigger, target and message.
	def readTargets(self, targetsCSV):
		# Open and read targets.csv
		with open(targetsCSV, 'r') as tfile:
			csvrows = csv.reader(tfile, delimiter = ';')
			
			# Skip header
			next(csvrows, None)
			
			# Store remaining rows as targets
			for row in csvrows:
				# Put row contents into dictionary
				rowDict = {'trigger': row[0], 'target': row[1], 'message': row[2]}
				# Print what was read
				print("Read target that is triggered by '{}', sends a notification to '{}' with message '{}'".format(\
				rowDict['trigger'], rowDict['target'], rowDict['message']))
				# Add the target to the internal targets
				self.targets.append({'trigger': row[0], 'target': row[1], 'message': row[2]})
	
	# Connect to the page
	# Since Q has a cookie wall, we need to bypass that first in order to call it normally for the rest of the session
	def connect(self):
		return self.sessy.get('https://qmusic.nl/privacy/accept?originalUrl=/playlist/qmusic&pwv=1&pws=functional%7Canalytics%7Ccontent_recommendation%7Ctargeted_advertising%7Csocial_media&days=3650&referrer=')
		
	# This function indefinitely lets the bot listen for new songs on Q.
	# If a new song is detected, post it to a webhook.
	def listenToQ(self):
		# Connect first and store response
		response = self.connect()
		# Set last to previous track, so at start the latest track is also printed
		lastTrack = self.soupy(response.content, 'html.parser').find_all('div', {'class': 'track'})[1]
		
		# Infinite listening loop
		while True:
			# Refresh page and get latest track
			latestTrack = self.soupy(self.sessy.get(self.url).content, 'html.parser').find('div', {'class': 'track'})
			
			# Check if the latest track is new
			if self.trackIsNew(lastTrack, latestTrack):
				# There is a new track, let the update function handle it
				self.handleUpdate(latestTrack)
				# Set this track as last one
				lastTrack = latestTrack
				
				# Reset sleeping period and sleep
				self.sleepPeriod = 180
				time.sleep(self.sleepPeriod)
			else:
				# No new track
				self.sleepPeriod = int(self.sleepPeriod / 3) + 10	# Set new sleeping period
				time.sleep(self.sleepPeriod)						# Sleep for that period
	
	# Determines whether a track is new (later time)
	def trackIsNew(self, prevTrack, curTrack):
		lastTime = datetime.strptime(prevTrack['data-date'], '%Y-%m-%d %H:%M:%S')
		curTime = datetime.strptime(curTrack['data-date'], '%Y-%m-%d %H:%M:%S')
		return curTime > lastTime
	
	# Logic to determine what to do after an update, based on given targets (triggers)
	# For Q, if a new track is recognised, it is printed and if it satisfies a trigger, a notification is posted
	def handleUpdate(self, track):
		# Extract relevant information
		trackTime = track.find('span', {'class': 'time'}).text
		title = track.find('span', {'class': 'track-name'}).text
		artist = track.find('span', {'class': 'artist-name'}).text
		img = track.find('img')['src']
		
		# Print the new track first
		self.printUpdate(trackTime, title, artist)
		
		# Check if the track satisfies a trigger
		for target in self.targets:
			# Loop through all targets and check if the track contains the trigger (case-insensitive)
			if any(target['trigger'].lower() in str(c).lower() for c in track.contents):
				# Trigger satisfied, post notification
				self.postNotification(target['target'], target['message'], trackTime, title, artist, img)
		
	# Prints an update to the console
	# For a track the time, song title and artist name is printed
	def printUpdate(self, trackTime, title, artist):
		message = 'Nieuw liedje:\nTijd: {}\nTitel: {}\nArtiest: {}'.format(trackTime, title, artist)
		print(message)
	
	# Posts a notification to a provided webhook (url)
	# For a track, the title becomes username, img becomes avatar and artist and time are included in the message
	def postNotification(self, hookURL, msgStart, trackTime, title, artist, cover):
		# Prepare message to display
		message = msgStart + '\nArtiest: {}\nTijd: {}'.format(artist, trackTime)
		# Prepare data to include in post request
		postContent = {'username': title, 'avatar_url': cover, 'content': message}
		# Then post
		self.sessy.post(hookURL, postContent)


# If executed, run bot function
if __name__ == '__main__':
    
	# Initialise bot
	bot = QBot()
	bot.readTargets('targets.csv')
	
	# Run bot until process kill (CTRL-C)
	bot.listenToQ()
	
	#sys.exit(main(sys.argv[1:]))