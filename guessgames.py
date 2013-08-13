import cherrypy
from mako.template import Template
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import json
import os

from model import *
from matchups import *
#from publisher import *

WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

SUBSCRIBERS = set()

class Publisher(WebSocket):
    #events = {'gettop10games':generateGamePossibilities}
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        print str(self) + "connected"
        SUBSCRIBERS.add(self)

    def closed(self, code, reason=None):
        SUBSCRIBERS.remove(self)
    def received_message(self, message):
    	print "received_message"
    	pythonmessage = json.loads(message)

    	eventname = pythonmessage['event']
    	eventdata = pythonmessage['data']

    	if eventname == 'gettop10games':
    		generateGamePossibilities(json.loads(eventdata))
    		print "%s triggered successfully with data %s" % eventname, str(eventdata)
    	else:
            print "\nevent %s not found. Data: %s \n From message: %s\n" % eventname, str(eventdata), str(message)
    #for conn in SUBSCRIBERS:
    #    conn.send(json.dumps({"event":'leaderboard', 'data':returnString}))
    def update(self):
    	generateGamePossibilities

def sendMessage(event, data):
    #
    for conn in SUBSCRIBERS:
        conn.send(json.dumps({'event':event, 'data':data})
)
defaultGamePossibilities= list(generateGamePossibilities(usesWebsocket = False))
defaultPlayersForTemplate = getPlayersForTemplate(checkedPlayers=defaultPlayers)




class HitzApp(object):
	@cherrypy.expose
	def games(self):
		return Template(filename='htdocs/guessgames.html', input_encoding = 'utf-8').render(topGames=defaultGamePossibilities,players=defaultPlayersForTemplate)

	@cherrypy.expose
	def playerstats(self, user):
		if not user:
			return Template(filename='htdocs/chooseuserforstats.html', input_encoding='utf-8').render(userlist = generateUserList())
		else:
			return Template(filename='htdocs/stats.html', input_encoding='utf-8').render(user=user,rival=rival(user),bff=bff(user),ratingMu=ratingMu(user),ratingSigma=ratingSigma(user),bestTeam=bestTeam(user),rank=rank(user),upcominggames=upcomingGames(user))
#Template(filename='htdocs/standaloneleaderboard.html', input_encoding = 'utf-8').render(leaderboardList=leaderboardBody, nextmatch=nextMatch, matchlog = generateMatchLog())
	@cherrypy.expose
	def update(self):
		generateGamePossibilities(['Nick', 'Drew', 'Ced', 'Magoo', 'Rosen', 'White Rob', 'Crabman'])
	@cherrypy.expose
	def ws(self):
		handler = cherrypy.request.ws_handler

if __name__ == '__main__':
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