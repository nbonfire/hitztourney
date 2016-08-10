import cherrypy
from cherrypy.process import wspbus, plugins
from mako.template import Template
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import json
import os, os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
import itertools
from pubsub import pub  
from sortedcollection import *
from model import *
import math


defaultGamesList = list()
NextUID=0
#
# WEBSOCKET CHERRYPY PLUGIN
#
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

SUBSCRIBERS = set()

class Publisher(WebSocket):
	#events = {'gettop10games':generateGamePossibilities}
	def __init__(self, *args, **kw):
		WebSocket.__init__(self, *args, **kw)
		print str(self) + "connected"
		SUBSCRIBERS.add(self)
		global NextUID
		NextUID = NextUID + 1
		UID = NextUID
		

	def closed(self, code, reason=None):
		SUBSCRIBERS.remove(self)
	
	def sendToMe(self, event, message):#event, message):
		#print event
		#print message
		self.send(json.dumps({'event':event, 'data':message}))

	# I commented this out because until I figure how to get a session into the Publisher class, I'll just use ajax 
	# to trigger the "generateGamePossibilities" 
	def received_message(self, message):
		#print "received_message %s" % str(message)
		pythonmessage = json.loads(str(message))

		eventname = pythonmessage['event']
		eventdata = pythonmessage['data']

		if eventname == 'subscribe':
			pub.subscribe(self.sendToMe, str(eventdata))
			print "%s triggered successfully with data %s" % (eventname, eventdata)
		elif eventname =='getUID':
			self.send(json.dumps({'event':'getUID', 'data':self.UID}))
		else:
			print "\nevent %s not found. Data: %s \n From message: %s\n" % eventname, str(eventdata), str(message)

			
	#for conn in SUBSCRIBERS:
	#    conn.send(json.dumps({"event":'leaderboard', 'data':returnString}))

"""
Round Robin Schedule:

matchup = [];
players = ["Adi","Bader","Ced","Gio","James","Jeff","Jesse","Jon","Kent","Koplow","Magoo","Nick","Rosen","Sean","White Rob","Ziplox"];

rankedOrder=[];
playerList = [];
nextMatchIndex = 0


for index, player in enumerate(players):
  playerList.append({"name":player,"id":int(index),"wins":0,"games":0,"average":0.000});
tv=["Samsung","Sony"]
if len(players)==14:
	#(8 1 12 v 13 11 7) (9 14 6 v 4 3 2) (5 10)
	matchup.append( {"home":[8,1,12],"away":[13,11,7],"bye":[5,10],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[9,14,6],"away":[4,3,2],"bye":[5,10],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(9 2 13 v 14 12 8) (10 1 7 v 5 4 3) (6 11)
	matchup.append( {"home":[9,2,13],"away":[14,12,8],"bye":[6,11],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[10,1,7],"away":[5,4,3],"bye":[6,11],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(10 3 14 v 1 13 9) (11 2 8 v 6 5 4) (7 12)
	matchup.append( {"home":[10,3,14],"away":[1,13,9],"bye":[7,12],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[11,2,8],"away":[6,5,4],"bye":[7,12],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(11 4 1 v 2 14 10) (12 3 9 v 7 6 5) (8 13)
	matchup.append( {"home":[11,4,1],"away":[2,14,10],"bye":[8,13],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[12,3,9],"away":[7,6,5],"bye":[8,13],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(12 5 2 v 3 1 11) (13 4 10 v 8 7 6) (9 14)
	matchup.append( {"home":[12,5,2],"away":[3,1,11],"bye":[9,14],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[13,4,10],"away":[8,7,6],"bye":[9,14],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(13 6 3 v 4 2 12) (14 5 11 v 9 8 7) (10 1)
	matchup.append( {"home":[13,6,3],"away":[4,2,12],"bye":[10,1],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[14,5,11],"away":[9,8,7],"bye":[10,1],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(14 7 4 v 5 3 13) (1 6 12 v 10 9 8) (11 2)
	matchup.append( {"home":[14,7,4],"away":[5,3,13],"bye":[11,2],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[1,6,12],"away":[10,9,8],"bye":[11,2],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(1 8 5 v 6 4 14) (2 7 13 v 11 10 9) (12 3)
	matchup.append( {"home":[1,8,5],"away":[6,4,14],"bye":[12,3],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[2,7,13],"away":[11,10,9],"bye":[12,3],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(2 9 6 v 7 5 1) (3 8 14 v 12 11 10) (13 4)
	matchup.append( {"home":[2,9,6],"away":[7,5,1],"bye":[13,4],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[3,8,14],"away":[12,11,10],"bye":[13,4],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(3 10 7 v 8 6 2) (4 9 1 v 13 12 11) (14 5)
	matchup.append( {"home":[3,10,7],"away":[8,6,2],"bye":[14,5],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[4,9,1],"away":[13,12,11],"bye":[14,5],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(4 11 8 v 9 7 3) (5 10 2 v 14 13 12) (1 6)
	matchup.append( {"home":[4,11,8],"away":[9,7,3],"bye":[1,6],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[5,10,2],"away":[14,13,12],"bye":[1,6],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(5 12 9 v 10 8 4) (6 11 3 v 1 14 13) (2 7)
	matchup.append( {"home":[5,12,9],"away":[10,8,4],"bye":[2,7],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[6,11,3],"away":[1,14,13],"bye":[2,7],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(6 13 10 v 11 9 5) (7 12 4 v 2 1 14) (3 8)
	matchup.append( {"home":[6,13,10],"away":[11,9,5],"bye":[3,8],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[7,12,4],"away":[2,1,14],"bye":[3,8],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(7 14 11 v 12 10 6) (8 13 5 v 3 2 1) (4 9)
	matchup.append( {"home":[7,14,11],"away":[12,10,6],"bye":[4,9],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[8,13,5],"away":[3,2,1],"bye":[4,9],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
if len(players)==15:
	#(2 10 8 v 14 1 5)  (15 12 9 v 11 3 7)  (13 6 4)
	matchup.append( {"home":[2,10,8],"away":[14,1,5],"bye":[13,6,4],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[15,12,9],"away":[11,3,7],"bye":[13,6,4],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(3 6 9 v 15 2 1)  (11 13 10 v 12 4 8)  (14 7 5)
	matchup.append( {"home":[3,6,9],"away":[15,2,1],"bye":[14,7,5],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[11,13,10],"away":[12,4,8],"bye":[14,7,5],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(4 7 10 v 11 3 2)  (12 14 6 v 13 5 9)  (15 8 1)
	matchup.append( {"home":[4,7,10],"away":[11,3,2],"bye":[15,8,1],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[12,14,6],"away":[13,5,9],"bye":[15,8,1],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(5 8 6 v 12 4 3)  (13 15 7 v 14 1 10)  (11 9 2)
	matchup.append( {"home":[5,8,6],"away":[12,4,3],"bye":[11,9,2],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[13,15,7],"away":[14,1,10],"bye":[11,9,2],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(1 9 7 v 13 5 4)  (14 11 8 v 15 2 6)  (12 10 3)
	matchup.append( {"home":[1,9,7],"away":[13,5,4],"bye":[12,10,3],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[14,11,8],"away":[15,2,6],"bye":[12,10,3],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(7 11 6 v 10 1 5)  (4 15 9 v 2 14 12)  (3 13 8)
	matchup.append( {"home":[7,11,6],"away":[10,1,5],"bye":[3,13,8],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[4,15,9],"away":[2,14,12],"bye":[3,13,8],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(8 12 7 v 6 2 1)  (5 11 10 v 3 15 13)  (4 14 9)
	matchup.append( {"home":[8,12,7],"away":[6,2,1],"bye":[4,14,9],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[5,11,10],"away":[3,15,13],"bye":[4,14,9],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(9 13 8 v 7 3 2)  (1 12 6 v 4 11 14)  (5 15 10)
	matchup.append( {"home":[9,13,8],"away":[7,3,2],"bye":[5,15,10],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[1,12,6],"away":[4,11,14],"bye":[5,15,10],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(10 14 9 v 8 4 3)  (2 13 7 v 5 12 15)  (1 11 6)
	matchup.append( {"home":[10,14,9],"away":[8,4,3],"bye":[1,11,6],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[2,13,7],"away":[5,12,15],"bye":[1,11,6],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(6 15 10 v 9 5 4)  (3 14 8 v 1 13 11)  (2 12 7)
	matchup.append( {"home":[6,15,10],"away":[9,5,4],"bye":[2,12,7],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[3,14,8],"away":[1,13,11],"bye":[2,12,7],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(8 15 1 v 12 9 10)  (13 2 14 v 6 3 5)  (11 4 7)
	matchup.append( {"home":[8,15,1],"away":[12,9,10],"bye":[11,4,7],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[13,2,14],"away":[6,3,5],"bye":[11,4,7],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(9 11 2 v 13 10 6)  (14 3 15 v 7 4 1)  (12 5 8)
	matchup.append( {"home":[9,11,2],"away":[13,10,6],"bye":[12,5,8],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[14,3,15],"away":[7,4,1],"bye":[12,5,8],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(10 12 3 v 14 6 7)  (15 4 11 v 8 5 2)  (13 1 9)
	matchup.append( {"home":[10,12,3],"away":[14,6,7],"bye":[13,1,9],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[15,4,11],"away":[8,5,2],"bye":[13,1,9],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(6 13 4 v 15 7 8)  (11 5 12 v 9 1 3)  (14 2 10)
	matchup.append( {"home":[6,13,4],"away":[15,7,8],"bye":[14,2,10],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[11,5,12],"away":[9,1,3],"bye":[14,2,10],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(7 14 5 v 11 8 9)  (12 1 13 v 10 2 4)  (15 3 6)
	matchup.append( {"home":[7,14,5],"away":[11,8,9],"bye":[15,3,6],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[12,1,13],"away":[10,2,4],"bye":[15,3,6],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
elif len(players)==16:
	#( 2  7  6 v  1  4 10)  (14 12  9 v 13  3  5)  (11 15  8 16)
	matchup.append( {"home":[2,7,6], "away":[1,4,10],"bye":[11,15,8,16],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[14,12,9], "away":[13,3,5],"bye":[11,15,8,16],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 4  9  8 v  3  6 12)  (16 14 11 v 15  5  7)  (13  1 10  2) 
	matchup.append( {"home":[4,9,8], "away":[3,6,12],"bye":[13,1,10,2],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[16,14,11], "away":[15,5,7],"bye":[13,1,10,2],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 6 11 10 v  5  8 14)  ( 2 16 13 v  1  7  9)  (15  3 12  4) 
	matchup.append( {"home":[6,11,10], "away":[5,8,14],"bye":[15,3,12,4],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[2,16,13], "away":[1,7,9],"bye":[15,3,12,4],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 8 13 12 v  7 10 16)  ( 4  2 15 v  3  9 11)  ( 1  5 14  6) 
	matchup.append( {"home":[8,13,12], "away":[7,10,16],"bye":[1,5,14,6],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[4,2,15], "away":[3,9,11],"bye":[1,5,14,6],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(10 15 14 v  9 12  2)  ( 6  4  1 v  5 11 13)  ( 3  7 16  8) 
	matchup.append( {"home":[10,15,14], "away":[9,12,2],"bye":[3,7,16,8],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[6,4,1], "away":[5,11,13],"bye":[3,7,16,8],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(12  1 16 v 11 14  4)  ( 8  6  3 v  7 13 15)  ( 5  9  2 10) 
	matchup.append( {"home":[12,1,16], "away":[11,14,4],"bye":[5,9,2,10],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[8,6,3], "away":[7,13,15],"bye":[5,9,2,10],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(14  3  2 v 13 16  6)  (10  8  5 v  9 15  1)  ( 7 11  4 12) 
	matchup.append( {"home":[14,3,2], "away":[13,16,6],"bye":[7,11,4,12],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[10,8,5], "away":[9,15,1],"bye":[7,11,4,12],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(16  5  4 v 15  2  8)  (12 10  7 v 11  1  3)  ( 9 13  6 14) 
	matchup.append( {"home":[16,5,4], "away":[15,2,8],"bye":[9,13,6,14],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[12,10,7], "away":[11,1,3],"bye":[9,13,6,14],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 1  6  5 v 16  3  9)  (13 11  8 v 12  2  4)  (10 14  7 15)
	matchup.append( {"home":[13,11,8], "away":[12,2,4],"bye":[10,14,7,15],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	matchup.append( {"home":[1,6,5], "away":[16,3,9],"bye":[10,14,7,15],"winners":{"id": [],"team":"none"}, "tv":tv[0]}); #10 14 7 15
	#( 3  8  7 v  2  5 11)  (15 13 10 v 14  4  6)  (12 16  9  1) 
	matchup.append( {"home":[3,8,7], "away":[2,5,11],"bye":[12,16,9,1],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[15,13,10], "away":[14,4,6],"bye":[12,16,9,1],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 5 10  9 v  4  7 13)  ( 1 15 12 v 16  6  8)  (14  2 11  3) 
	matchup.append( {"home":[5,10,9], "away":[4,7,13],"bye":[14,2,11,3],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[1,15,12], "away":[16,6,8],"bye":[14,2,11,3],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 7 12 11 v  6  9 15)  ( 3  1 14 v  2  8 10)  (16  4 13  5) 
	matchup.append( {"home":[7,12,11], "away":[6,9,15],"bye":[16,4,13,5],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[3,1,14], "away":[2,8,10],"bye":[16,4,13,5],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#( 9 14 13 v  8 11  1)  ( 5  3 16 v  4 10 12)  ( 2  6 15  7) 
	matchup.append( {"home":[9,14,13], "away":[8,11,1],"bye":[2,6,15,7],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[5,3,16], "away":[4,10,12],"bye":[2,6,15,7],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(11 16 15 v 10 13  3)  ( 7  5  2 v  6 12 14)  ( 4  8  1  9) 
	matchup.append( {"home":[11,16,15], "away":[10,13,3],"bye":[4,8,1,9],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[7,5,2], "away":[6,12,14],"bye":[4,8,1,9],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(13  2  1 v 12 15  5)  ( 9  7  4 v  8 14 16)  ( 6 10  3 11) 
	matchup.append( {"home":[13,2,1], "away":[12,15,5],"bye":[6,10,3,11],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[9,7,4], "away":[8,14,16],"bye":[6,10,3,11],"winners":{"id": [],"team":"none"}, "tv":tv[1]});
	#(15  4  3 v 14  1  7)  (11  9  6 v 10 16  2)  ( 8 12  5 13) 
	matchup.append( {"home":[15,4,3], "away":[14,1,7],"bye":[8,12,5,13],"winners":{"id": [],"team":"none"}, "tv":tv[0]});
	matchup.append( {"home":[11,9,6], "away":[10,16,2],"bye":[8,12,5,13],"winners":{"id": [],"team":"none"}, "tv":tv[1]});

else: 
	print str(len(players)); + " players specified"
"""

def sendToAll(event, data):
	#
	for conn in SUBSCRIBERS:
		#print "%s:%s" %(event,data)
		conn.send(json.dumps({'event':event, 'data':data}))


#
# SQLALCHEMY CHERRYPYPLUGIN
#

class SAEnginePlugin(plugins.SimplePlugin):
	def __init__(self, bus):
		"""
		The plugin is registered to the CherryPy engine and therefore
		is part of the bus (the engine *is* a bus) registery.
 
		We use this plugin to create the SA engine. At the same time,
		when the plugin starts we create the tables into the database
		using the mapped class of the global metadata.
 
		Finally we create a new 'bind' channel that the SA tool
		will use to map a session to the SA engine at request time.
		"""
		plugins.SimplePlugin.__init__(self, bus)
		self.sa_engine = None
		self.bus.subscribe("bind", self.bind)
 
	def start(self):
		db_path = os.path.abspath(os.path.join(os.curdir, 'hitz.sqlite'))
		self.sa_engine = create_engine('sqlite:///%s' % db_path, echo=False)
		Base.metadata.create_all(self.sa_engine)
 
	def stop(self):
		if self.sa_engine:
			self.sa_engine.dispose()
			self.sa_engine = None
 
	def bind(self, session):
		session.configure(bind=self.sa_engine)
 
class SATool(cherrypy.Tool):
	def __init__(self):
		"""
		The SA tool is responsible for associating a SA session
		to the SA engine and attaching it to the current request.
		Since we are running in a multithreaded application,
		we use the scoped_session that will create a session
		on a per thread basis so that you don't worry about
		concurrency on the session object itself.
 
		This tools binds a session to the engine each time
		a requests starts and commits/rollbacks whenever
		the request terminates.
		"""
		cherrypy.Tool.__init__(self, 'on_start_resource',
							   self.bind_session,
							   priority=20)
 
		self.session = scoped_session(sessionmaker(autoflush=True,
												  autocommit=False))
 
	def _setup(self):
		cherrypy.Tool._setup(self)
		cherrypy.request.hooks.attach('on_end_resource',
									  self.commit_transaction,
									  priority=80)
 
	def bind_session(self):
		cherrypy.engine.publish('bind', self.session)
		cherrypy.request.db = self.session
 
	def commit_transaction(self):
		cherrypy.request.db = None
		try:
			self.session.commit()
		except:
			self.session.rollback()  
			raise
		finally:
			self.session.remove()

#
# DEFAULTS
#


def getDefaultGamesList(session):
	global defaultGamesList
	if not defaultGamesList:
		defaultGamesList=list(generateGamePossibilities(session, usesWebsocket = False))
		return defaultGamesList
	else:
		return defaultGamesList

def generateGamePossibilities(session, listOfPlayers=[], numberOfGames=10, usesWebsocket = True):
	# 
	# output should be a list of games [{'home':team,'away':team, 'strength':float}] randomized, then sorted by strength
	#
	global defaultGamesList
	if len(listOfPlayers)<6:
		if listOfPlayers:
			print "error: %s doesn't have enough players" % listOfPlayers
		listOfPlayers=[player.name for player in session.query(Hitter).all()][0:6]
	
	potentialGames=[]
	potentialGamesCollection=SortedCollection(key=lambda item:-item['strength'])
	players = set(listOfPlayers)
	complete = set()
	begintime=datetime.datetime.now()
	lastupdate=begintime #when was the last time we printed the results?
	firstcombo=itertools.combinations(players, 3)
	
	iterations=(len(players))*(len(players)-1)*(len(players)-2)/6
	iterator=0
	for home in firstcombo:
		iterator=iterator+1
		complete.add(home[0])
		remaining_players = players - set(home) - complete
		for away in itertools.combinations(remaining_players, 3):
			potentialGamesCollection.insert({'home':[home[0], home[1], home[2]],'homerating':get_or_create_team(session, [home[0],home[1],home[2]]).getteamrating(), 'away':[away[0], away[1], away[2]], 'awayrating':get_or_create_team(session, [away[0],away[1],away[2]]).getteamrating(), 'strength':(float(getStrength(session, homeNames=home,awayNames=away))/100), 'lastPlayed':str(getLastPlayed(session, homeNames=home,awayNames=away))})
			#potentialGamesCollection.insert({'home':["%s", "%s", "%s"] % (home[0],home[1],home[2]),'homerating':get_or_create_team(session, [home[0],home[1],home[2]]).getteamrating(), 'away':'["%s", "%s", "%s"]' % (away[0],away[1],away[2]), 'awayrating':get_or_create_team(session, [away[0],away[1],away[2]]).getteamrating(), 'strength':(float(getStrength(session, homeNames=home,awayNames=away))/100), 'lastPlayed':str(getLastPlayed(session, homeNames=home,awayNames=away))})
			
			#potentialGames.append( {'home':home, 'away':away, 'strength':getStrength(homeNames=home,awayNames=away), 'lastPlayed':getLastPlayed(homeNames=home,awayNames=away)})
			if len(potentialGamesCollection)>numberOfGames:
				potentialGamesCollection.removebyindex(numberOfGames)
				
			
			if usesWebsocket==True:
				timenow=datetime.datetime.now()
				difference=timenow-lastupdate
				if difference.total_seconds()>1:
					#cls()
					#print list(potentialGamesCollection)
					lastupdate=timenow
					#sendToAll(event='top10games', data={'games':list(potentialGamesCollection), 'isdone':"Working...", 'percentComplete':str(iterator*100/iterations)})
					pub.sendMessage('topgames', event="topgames", message=({'games':list(potentialGamesCollection), 'isdone':"Working...", 'percentComplete':str(iterator*100/iterations)} ))
	#print "\n\n\n outer iterations: %d - inner iterations: %d - guesstimate: %d"%(iterator, iterations)
	if usesWebsocket == True:
		defaultGamesList = list(potentialGamesCollection)
		#sendToAll(event='top10games', data={'games':list(potentialGamesCollection), 'isdone':"Done", 'percentComplete':'100'})
		pub.sendMessage('topgames', event="topgames", message=({'games':list(potentialGamesCollection), 'isdone':"Done", 'percentComplete':'100'}))
		print 'Elapsed Time: %s seconds' % str((lastupdate-timenow).total_seconds)
		return True
	else:
		return potentialGamesCollection

class HitzApp(object):
	@cherrypy.expose
	def games(self):
		return Template(filename='htdocs/guessgames.html', input_encoding = 'utf-8').render(topGames=getDefaultGamesList(cherrypy.request.db),players=getPlayersForTemplate(session=cherrypy.request.db))
	@cherrypy.expose
	def overallstats(self):
		playerList = getUserList(cherrypy.request.db)
		playerList.sort(key=lambda player: player['overallskill'], reverse=True)
		return Template(filename='htdocs/overallranking.html', input_encoding='utf-8').render(players = playerList)
		
	@cherrypy.expose
	def playerstats(self, user=None):
		if not user:
			return Template(filename='htdocs/chooseuserforstats.html', input_encoding='utf-8').render(players = getUserList(cherrypy.request.db))
		else:
			
			#statssubject=cherrypy.request.db.query(Hitter).filter(Hitter.name==user).first()
			statssubject=get_or_create(cherrypy.request.db, Hitter, name=user)
			return Template(filename='htdocs/stats.html', input_encoding='utf-8').render(
				user=statssubject,
				rivals=rivals(cherrypy.request.db, statssubject),
				ofbs=outforbloods(cherrypy.request.db,statssubject),
				bffs=bffs(cherrypy.request.db, statssubject),
				rating=statssubject.rating,
				bestTeams=bestTeams(cherrypy.request.db, statssubject),
				hitzskill=statssubject.hitzskill(),
				currentrecord=currentSeasonRecordString(cherrypy.request.db, statssubject),
				gamehistory=getGameHistoryForUser(cherrypy.request.db, statssubject, currentseasonstartdate)) #"""upcomingGames(cherrypy.request.db, user)"""
#Template(filename='htdocs/standaloneleaderboard.html', input_encoding = 'utf-8').render(leaderboardList=leaderboardBody, nextmatch=nextMatch, matchlog = generateMatchLog())
	@cherrypy.expose
	def history(self):
		return Template(filename='htdocs/history.html', input_encoding='utf-8').render(gamesList=cherrypy.request.db.query(Game).all())
	@cherrypy.expose
	def update(self, **kwargs):
		#players="{'players':['Nick', 'Drew', 'Ced', 'Magoo', 'Rosen', 'White Rob', 'Crabman']}"
		playernames=json.loads(kwargs['players'])
		print playernames
		if len(playernames['data'])<6:
			players=[]
		else:
			players=playernames['data']
		pub.sendMessage('checkedPlayers', message=players)
		#print json.loads(players)['data']
		generateGamePossibilities(session=cherrypy.request.db,listOfPlayers=players)
		return "True"
	@cherrypy.expose
	def pickwinner(self, **kwargs):
		hometeam=json.loads(kwargs['home'])
		awayteam=json.loads(kwargs['away'])
		winner = kwargs['winner']
		datePlayed=kwargs['date']
		homepoints=kwargs['homepoints']
		awaypoints=kwargs['awaypoints']
		completeGame(session=cherrypy.request.db, homeTeam=hometeam, awayTeam=awayteam, winner=winner, datePlayed=datetime.datetime.strptime(datePlayed, '"%Y-%m-%d"'), homepoints=homepoints, awaypoints=awaypoints)
		print "%s vs %s %s won" %(awayteam, hometeam, winner)
	@cherrypy.expose
	def drawprobability(self, **kwargs):
		hometeam = json.loads(kwargs['hometeam'])
		awayteam = json.loads(kwargs['awayteam'])
		if (get_or_create_team(session=cherrypy.request.db, findplayers=awayteam) and get_or_create_team(session=cherrypy.request.db, findplayers=hometeam)):
			message={
				'awayNames':awayteam, 
				'homeNames':hometeam, 
				'strength':float(getStrength(
					session=cherrypy.request.db, 
					homeNames=hometeam, 
					awayNames=awayteam
					))/100.0,
				'winProbability':float(getWinProb(get_or_create_team(session=cherrypy.request.db, findplayers=awayteam).hitters,get_or_create_team(session=cherrypy.request.db, findplayers=hometeam).hitters))/100.0
				}
			pub.sendMessage('currentgamedrawprobability', 
				
				
				event='currentgamedrawprobability',
				message=message
				
			)
			"""
			{'awayNames':["player1","player2","player3"],
               'homeNames':["player4","player5","player6"],
               'strength': '63.28',
               'teamstrength':'64.30'
			"""
		else:
			print "invalid kwargs -> %s, %d, %d" % (kwargs, len(kwargs['awayteam']), len(kwargs['hometeam']))

	@cherrypy.expose
	def ws(self):
		handler = cherrypy.request.ws_handler

if __name__ == '__main__':
	
	SAEnginePlugin(cherrypy.engine).subscribe()
	cherrypy.tools.db = SATool()
	current_dir = os.path.dirname(os.path.abspath(__file__))
	configtest = {
			'/':
				{'tools.db.on': True,
				},
			'/css':
				{'tools.staticdir.on': True,
				 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/css')
				}, 
			'/js':
				{'tools.staticdir.on': True,
				 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/js')
				},
			'/images':
				{'tools.staticdir.on': True,
				 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/images')
				},
			#'/media':
			#	{'tools.staticdir.on': True,
			#	 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/media')
			#	},  
			'/ws': {'tools.websocket.on': True,
					'tools.websocket.handler_cls': Publisher}

			#'/media':
			#	{'tools.staticdir.on': True,
			#	 'tools.staticdir.dir': '/media'
			#	},		
			#'/':
			#	{'tools.staticdir.on': True,
			#	 'tools.staticdir.root': os.path.join(current_dir, "htdocs")
			#	 }


		}

	cherrypy.server.socket_host='0.0.0.0'
	cherrypy.server.socket_port=4011
	cherrypy.quickstart(HitzApp(), config=configtest)
