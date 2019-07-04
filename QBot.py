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

import requests					# Handle HTML stuff
from bs4 import BeautifulSoup	# Parse HTML stuff
from datetime import datetime	# Handle time stuff
import time						# Sleeping and more time

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
		self.target = None								# Webhook (url) to post message to
		self.message = 'Message'						# Message to post
	
	# Connect to the page
	# Since Q has a cookie wall, we need to bypass that first in order to call it normally for the rest of the session
	def connect(self):
		return self.sessy.get('https://qmusic.nl/privacy/accept?originalUrl=/playlist/qmusic&pwv=1&pws=functional%7Canalytics%7Ccontent_recommendation%7Ctargeted_advertising%7Csocial_media&days=3650&referrer=')
		
	# This function indefinitely lets the bot listen for new songs on Q.
	# If a new song is detected, post it to a webhook.
	def listenToQ(self):
		# Connect first and store response
		response = self.connect()
		# Initialise variables
		lastTrack = self.soupy(response.content, 'html.parser').find('div', {'class': 'track'})
		lastTime = datetime.strptime(lastTrack['data-date'], '%Y-%m-%d %H:%M:%S')
		# Post current track
		self.postNotification(lastTrack)
		
		# Infinite listening loop
		while True:
			# Refresh page and get latest track
			latestTrack = self.soupy(self.sessy.get(self.url).content, 'html.parser').find('div', {'class': 'track'})
			
			# Check if the latest track is new
			if self.trackIsNew(lastTrack, latestTrack):
				# There is a new track
				# Post information
				self.postNotification(latestTrack)
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
	
	def postNotification(self, track):
		# Print first
		message = 'Nieuw liedje:\nTijd: {}\nTitel: {}\nArtiest: {}'.format(track.find('span', {'class': 'time'}).text, track.find('span', {'class': 'track-name'}).text, track.find('span', {'class': 'artist-name'}).text)
		print(message)
		# Then post
		self.sessy.post(self.target, {'content': message})


# If executed, run bot function
if __name__ == '__main__':
    
	# Initialise bot
	bot = QBot()
	#bot.connect()
	
	# Set bot target from file
	with open('targets.txt', 'r') as targetsFile:
		[bot.target, bot.message] = targetsFile.read().splitlines()
	
	# Run bot until process kill (CTRL-C)
	bot.listenToQ()
	
	#sys.exit(main(sys.argv[1:]))