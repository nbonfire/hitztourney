#hitztourney.py
#port 4579
import os
import cherrypy
from mako.template import Template
import shelve
import threading
import time
from datetime import datetime
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
#from mako.template import TemplateLookup

WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

SUBSCRIBERS = set()

class Publisher(WebSocket):
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        print str(self) + "connected"
        SUBSCRIBERS.add(self)

    def closed(self, code, reason=None):
        SUBSCRIBERS.remove(self)

rootDir = os.path.abspath("/Users/nickb/Projects/hitztourney/")

matchup = [];
players = ["Adi","Bader","Ced","Gio","James","Jeff","Jesse","Jon","Kent","Koplow","Magoo","Nick","Rosen","Sean","White Rob","Ziplox"];

rankedOrder=[];
playerList = [];
nextMatchIndex = 0

#initialize db lock
#_dbLocker = threading.Lock()
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

def checkWin(game,team):
	if game['winners']['team'] == team :
		return '<span class="winner">'
	else:
		return '<span class="loser">'

def compare_wins(a,b):
	if a['games']>0 and b['games']>0:
		return cmp(b["wins"]/b["games"], a["wins"]/a["games"])
	elif a['games']>0:
		return cmp(a['wins'],0)


def updateLeaderboard():
	for player in range(len(players)):
		playerList[player]['wins']=0
		playerList[player]['games']=0
		playerList[player]['average']=0.000
	completedgames = []
	for match in matchup:
		if match['winners']['team'] != 'none':
			completedgames.append(match)
	if completedgames != []:
		for match in completedgames:
			for playerid in match['winners']['id']:
				playerList[playerid-1]['wins']+=1
				playerList[playerid-1]['games']+=1
				playerList[playerid-1]['average']=float(playerList[playerid-1]['wins'])/float(playerList[playerid-1]['games'])
			if match['winners']['team']=='away':
				for playerid2 in match['home']:
					playerList[playerid2-1]['games']+=1
					playerList[playerid2-1]['average']=float(playerList[playerid2-1]['wins'])/float(playerList[playerid2-1]['games'])
			else:
				for playerid3 in match['away']:
					playerList[playerid3-1]['games']+=1
					playerList[playerid3-1]['average']=float(playerList[playerid3-1]['wins'])/float(playerList[playerid3-1]['games'])

			
		
		#rankedOrder = sorted(playerList,compare_wins)
		rankedOrder = sorted(playerList,key=lambda x: x['average'], reverse=True)
	else: 
		rankedOrder = playerList
	returnString=""
	for i,player in enumerate(rankedOrder):
		returnString+='\n<tr><td class="rank">'+str(i+1)+'.</td><td class="playername">'+player["name"]+'  </td><td class="wins">'
		returnString+=str(player["wins"])+' </td><td class="games">'+str(player["games"])+' </td><td class="average">'+'{percent:.0%}'.format(percent=player["average"])+'</td></tr>'
	return returnString

def displayLeaderboard():
	for i,player in enumerate(rankedOrder):
		returnString+='\n<tr><td class="rank">'+str(i+1)+'.</td><td class="playername">'+player["name"]+'  </td><td class="wins">'
		returnString+=str(player["wins"])+' </td><td class="games">'+str(player["games"])+' </td><td class="average">'+'{percent:.0%}'.format(percent=player["average"])+'</td></tr>'
	return returnString
matchesTemplate = """<li class="matchup" id="{match}"><div class="match">Match {match} - {tv}<p>
<a href="javascript:loadMatchTest('{match}','home')" team="home" match={match} class="{homewinstatus}">
{listOfHomeNames}</a> 
vs 
<a href="javascript:loadMatchTest('{match}','away')" team="away" match={match} class="{awaywinstatus}" >{listOfAwayNames}</a>
</p> Bye: <a href="#" team="bye" match={match} class="noWinner">{byenames}</a></li></div>\n
""" # Round number, homewinstatus ,home team names list, awaywinstatus, away team names list
nextmatchTemplate = """<li class="matchup" id="{match}"><div class="match">Match {match} - {tv}<p>
<a href="#" team="home" match={match} class="noWinner">
{listOfHomeNames}</a> 
vs 
<a href="#" team="away" match={match} class="noWinner" >{listOfAwayNames}</a> Bye: <a href="#" team="bye" match={match} class="noWinner">{byenames}</a>
</p><a href="#"></a></li></div>
"""
matchlogTemplate="""<li class="logitem" id="{match}"><div class="match">Match {match} - {tv} - {time}<p> <div class="winningTeam">{names}</div></p>
"""

matchHistory=[]

def matchLog(matchDict):
	matchHistory.append(matchDict)
	#sort by matchDict['match'] then matchDict['time']

def listNames(team,match):
	names =""
	for k,playerid in enumerate(match[team]):
		names+=players[playerid-1]
		if k < len(match[team])-1:
			names+="<br>"
	return names

def processMatch(matchid, match):
	if match["winners"]["team"] == 'home':
		homestatus = 'winningTeam'
		awaystatus = 'losingTeam'
	elif match['winners']['team'] == 'away':
		homestatus = 'losingTeam'
		awaystatus = 'winningTeam'
	else:
		homestatus = 'noWinner'
		awaystatus = 'noWinner'
	homeNames = ''
	awayNames = ''
	
	homeNames = listNames('home',match)
	awayNames = listNames('away',match)
	byeNames = listNames('bye',match)
	return matchesTemplate.format(match=matchid+1,homewinstatus=homestatus,awaywinstatus=awaystatus,listOfHomeNames=homeNames,listOfAwayNames=awayNames,tv=match['tv'],byenames=byeNames)

def generateMatchList():
	matchListString = ""
	for i, match in enumerate(matchup):
		
		matchListString+=processMatch(i, match)
	return matchListString

def determineNextMatch():
	for i, match in enumerate(matchup):
		if match['winners']['team']=='none':
			return i
	return 0
def generateMatchLog():
	returnString=""
	for i, item in enumerate(matchHistory):
		print str(item)+" "
		print listNames(item['winners'],matchup[item['match']])
		print matchup[item['match']]['tv'] #+ " "+item['time']
		returnString += matchlogTemplate.format(match=item["match"]+1,tv=matchup[item["match"]]['tv'],time=item['time'],names=listNames(item['winners'],matchup[item['match']]))
	return returnString



class HitzTourneyRunner(object):
	
	@cherrypy.expose
	def update():
		return updateLeaderboard()

	@cherrypy.expose
	def embedLeaderboard(self):
		#return header + generated list of records + footer		
		leaderboardBody = updateLeaderboard()
		return Template(filename='htdocs/leaderboard.html', input_encoding = 'utf-8').render(leaderboardList=leaderboardBody)
	
	@cherrypy.expose
	def index(self):	
		leaderboardBody = updateLeaderboard()
		nextMatchIndex = determineNextMatch()
		nextMatch=""
		for i in range(0,2):
			homeNames = listNames('home',matchup[nextMatchIndex+i])
			awayNames = listNames('away',matchup[nextMatchIndex+i])
			byeNames = listNames('bye',matchup[nextMatchIndex+i])
			nextMatch += nextmatchTemplate.format(match=nextMatchIndex+1+i,listOfHomeNames=homeNames,listOfAwayNames=awayNames,byenames=byeNames,tv=matchup[nextMatchIndex+i]['tv'])


		return Template(filename='htdocs/standaloneleaderboard.html', input_encoding = 'utf-8').render(leaderboardList=leaderboardBody, nextmatch=nextMatch, matchlog = generateMatchLog())
	@cherrypy.expose
	def admin(self):
		#return header + generated list + footer
		matchListBody = generateMatchList()
		return Template(filename='htdocs/index.html', input_encoding = 'utf-8').render(matchList=matchListBody,leaderboard=updateLeaderboard())
		
	@cherrypy.expose
	def pickwinner(self, **kwargs):
		#
		matchindex=int(kwargs['match'])-1
		matchup[matchindex]['winners']['team']=kwargs['team']
		matchup[matchindex]['winners']['id']=matchup[matchindex][kwargs['team']]
		nextMatchIndex = (matchindex / 2) * 2 # python integer division returns the floor, so we always get an even number this way, showing the next match.
		nextMatchIndex = nextMatchIndex * 2
		#print str(matchup[int(kwargs['match'])-1]['winners'])
		matchLog({"match":matchindex,'winners':kwargs['team'], 'time':datetime.now().strftime('%I:%M:%S%p')})

		matchListBody = generateMatchList()
		return processMatch(matchindex,matchup[matchindex])
		#return Template(filename='htdocs/index.html', input_encoding = 'utf-8').render(matchList=matchListBody)
#print rootDir#
#print os.path.join(rootDir, u'css')
current_dir = os.path.dirname(os.path.abspath(__file__))
configtest = {
			'/css':
				{'tools.staticdir.on': True,
				 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/css')
				}, 
		  	'/js':
		  		{'tools.staticdir.on': True,
				 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/js')
				},
			'/media':
		  		{'tools.staticdir.on': True,
				 'tools.staticdir.dir': os.path.join(current_dir, 'htdocs/media')
				},  
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

# test

for i in range(len(matchup)):
  print "Game "+ str(i+1) + " is " + playerList[matchup[i]["home"][0]-1]["name"] + ", " + playerList[matchup[i]["home"][1]-1]["name"] + ", and "+playerList[matchup[i]["home"][2]-1]["name"] +" against "+playerList[matchup[i]["away"][0]-1]["name"]+", "+playerList[matchup[i]["away"][1]-1]["name"]+", and " + playerList[matchup[i]["away"][2]-1]["name"] + " on the "+matchup[i]["tv"]+" TV"
#cherrypy.config.update(configtest)
cherrypy.server.socket_host='0.0.0.0'
cherrypy.quickstart(HitzTourneyRunner(), config=configtest)
