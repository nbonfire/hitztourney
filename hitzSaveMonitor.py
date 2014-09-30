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

class SaveChangeEventHandler(FileSystemEventHandler):

	def on_modified(self, event):
		global FILENAME
		global players
		newplayers = hitzSaveRead(FILENAME)
		#
		# compare newplayers to players
		#
		pairs = zip(newplayers,players)
		differences = [(x,y) for x,y in pairs if x!= y]
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