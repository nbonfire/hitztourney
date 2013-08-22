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
#from matchups import *
#from publisher import *

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

def generateGamePossibilities(session, listOfPlayers=['Nick', 'Rosen', 'Magoo', 'White Rob', 'Ziplox', 'Ced'], numberOfGames=10, usesWebsocket = True):
	# 
	# output should be a list of games [{'home':team,'away':team, 'strength':float}] randomized, then sorted by strength
	#
	global defaultGamesList
	if len(listOfPlayers)<6:
		print "error: %s doesn't have enough players" % listOfPlayers
		return generateGamePossibilities(numberOfGames=numberOfGames, usesWebsocket=usesWebsocket)
	else:
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
	def playerstats(self, user):
		if not user:
			return Template(filename='htdocs/chooseuserforstats.html', input_encoding='utf-8').render(userlist = generateUserList())
		else:
			return Template(filename='htdocs/stats.html', input_encoding='utf-8').render(user=user,rival=rival(user),bff=bff(user),ratingMu=ratingMu(user),ratingSigma=ratingSigma(user),bestTeam=bestTeam(user),rank=rank(user),upcominggames=upcomingGames(user))
#Template(filename='htdocs/standaloneleaderboard.html', input_encoding = 'utf-8').render(leaderboardList=leaderboardBody, nextmatch=nextMatch, matchlog = generateMatchLog())
	@cherrypy.expose
	def update(self, **kwargs):
		#players="{'players':['Nick', 'Drew', 'Ced', 'Magoo', 'Rosen', 'White Rob', 'Crabman']}"
		playernames=json.loads(kwargs['players'])
		print playernames
		if len(playernames['data'])<6:
			players=["Magoo","Rosen","White Rob","Ziplox","Drew","Crabman"]
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
		completeGame(session=cherrypy.request.db, homeTeam=hometeam, awayTeam=awayteam, winner=winner, datePlayed=datetime.datetime.strptime(datePlayed, '"%Y-%m-%d"'))
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
					))/100.0
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
	cherrypy.quickstart(HitzApp(), config=configtest)