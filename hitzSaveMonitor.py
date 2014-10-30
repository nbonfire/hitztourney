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
import os, pprint

#FILENAME = 'SLUS_201.40_0.bin'
#DIRNAME = '/media/b432a63a-9163-4aa8-938f-d55faaf624f2/playstation2/VMC/'

FILENAME = 'hitzsave'
DIRNAME = 'C:\saves'

players = hitzSaveRead(os.path.join(DIRNAME,FILENAME))

'''def didPlay(newrecord,oldrecord):
	
	# Get the dictionary of the value differences from the old record to the new record
	stats = { key: value-oldrecord[key] for (key, value) in newrecord.iteritems() if key !='name'}
	stats['name']=oldrecord['name']
	

	return stats'''

class DictDiffer(object):
	"""
	Calculate the difference between two dictionaries as:
	(1) items added
	(2) items removed
	(3) keys same in both but changed values
	(4) keys same in both and unchanged values
	"""
	def __init__(self, current_dict, past_dict):
		self.current_dict, self.past_dict = current_dict, past_dict
		self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
		self.intersect = self.set_current.intersection(self.set_past)
	def added(self):
		return self.set_current - self.intersect 
	def removed(self):
		return self.set_past - self.intersect 
	def changed(self):
		return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
	def unchanged(self):
		return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])	

class SaveChangeEventHandler(FileSystemEventHandler):

	def on_modified(self, event):
		global FILENAME
		global players
		readytoread=1
		
		#test if the file is done being written to, if its not we should get an exception
		try:
			with open(os.path.join(DIRNAME,FILENAME),'wb') as fp:
				fp.close
		except:
			readytoread=0
			
		if readytoread:
			playednames = set()
			updatedplayers=[]
			winteam={'players':[],'score':0}
			loseteam={'players':[],'score':0}
			#pprint.pprint(players)
			print "*** NEW GAME ***"
		
			newplayers = hitzSaveRead(os.path.join(DIRNAME,FILENAME))
			#
			# compare new records to old records
			#
			#pprint.pprint(newplayers)
			d=DictDiffer(newplayers, players)
			if len(d.added())>0:
				print "New players: " + ' '.join(i for i in d.added())
			playednames = d.added().union(d.changed())
			if len(playednames)!= 6:
				print "somethings fucky, there weren't 6 players"
			else:
			
				for player in playednames:
					oldrecord = players[player]
					newrecord = newplayers[player]
					currentgamestatschanged = DictDiffer(newrecord, oldrecord).changed()
					playeroutput={'name':player,'assists':0, 'goals':0, 'hits':0, 'shots':0,
					'gamesPlayed':0,'consecutiveLosses':0,'wins':0}
					for key in currentgamestatschanged:
						playeroutput[key]+=newrecord[key]-oldrecord[key]
					pprint.pprint(playeroutput)


					if newrecord['wins']>oldrecord['wins']:
						winteam['players'].append(player)
						winteam['score']+=(newrecord['goals']-oldrecord['goals'])
					else:
						loseteam['players'].append(player)
						loseteam['score']+=(newrecord['goals']-oldrecord['goals'])
				print str(winteam['players'])+' beat '+str(loseteam['players'])+' : '+str(winteam['score'])+' - '+str(loseteam['score'])


		
		'''for player in newplayers:
			oldplayer = next((item for item in players if item['name'] ==player['name']),{'name':player['name'],'hits':0,'shots':0,'wins':0,'assists':0, 'gamesPlayed':0, 'goals':0,'consecutiveLosses':0})
			
			difference = didplay(player,oldplayer)
			if difference['gamesPlayed']>0:
				
				updatedplayers.append(difference)

		updatedplayers.sort(key=lambda player: player['gamesPlayed'])
		playedgame = [{'name':item['name'],'wins':item['wins']} for item in updatedplayers]
		if len(updatedplayers)!=6:
			print '\n*********\nERROR: number of updated players is not 6.\n\n ' +playedgame+'*********'
		else:
			print playedgame[0:3] + ' defeated ' + playedgame[3:6]
		#
		# update db/write to screen 
		#
		'''



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
