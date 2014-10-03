#
# hitzSaveMonitor.py
#
# Monitors the hitz save file and reads in the data, detecting changes.
#
# 1.) Perform an initial read to establish a baseline
# 2.) Set up an observer on the directory containing the save
# 3.) Set up an eventHandler to get a new read to compare to the baseline values
# 4.) Compare to find who played in a game. Should be able to tell from "wins" 
#     increasing or "consecutivelosses" changing any direction.
# 5.) Log the result
#

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import  FileSystemEventHandler
from hitzSaveRead import hitzSaveRead

FILENAME = 'hitzsave'
DIRNAME = 'saves'
players = hitzSaveRead(FILENAME)

def didPlay(newrecord,oldrecord):
	
	# Get the dictionary of the value differences from the old record to the new record
	stats = { key: value-oldrecord[key] for (key, value) in newrecord.iteritems() if key !='name'}
	stats['name']=oldrecord['name']
	

	return stats
	

class SaveChangeEventHandler(FileSystemEventHandler):

	def on_modified(self, event):
		global FILENAME
		global players
		updatedplayers = []
		newplayers = hitzSaveRead(FILENAME)
		#
		# compare new records to old records
		#

		for player in newplayers:
			oldplayer = next((item for item in players if item['name'] ==player['name']),{'name':player['name'],'hits':0,'shots':0,'wins':0,'assists':0, 'gamesPlayed':0, 'goals':0,'consecutiveLosses':0})
			
			difference = didplay(player,oldplayer)
			if difference['gamesPlayed']>0:
				
				updatedplayers.append(difference)

		updatedplayers.sort(key=lambda player: player['gamesPlayed'])
		playedgame = [{'name':item['name'],'wins':item['wins']} for item in updatedplayers]
		if len(updatedplayers)!=6:
			print '\nERROR: number of updated players is not 6.\n\n ' +playedgame
		else:
			print playedgame[0:3] + ' defeated ' + playedgame[3:6]
		#
		# update db/write to screen 
		#




		players = newplayers


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO,
		format= '%(asctime)s - %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S')
	path = DIRNAME
	event_handler = SaveChangeEventHandler()
	observer = Observer()
	observer.schedule(event_handler, path)
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()