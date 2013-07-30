#simple page to show stats for the db
from model import *
import cherrypy
from mako.template import Template
from datetime import datetime
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import json

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

class StatsPage(object):
	@cherrypy.expose
	def index(self, user="None"):
		if user=="None":
			#Choose a user and reload
			return Template(filename='htdocs/chooseuserforstats.html', input_encoding='utf-8').render(userlist = generateUserList())
		else:
			return Template(filename='htdocs/stats.html', input_encoding='utf-8').render(user=user,rival=rival(user),bff=bff(user),ratingMu=ratingMu(user),ratingSigma=ratingSigma(user),bestTeam=bestTeam(user),rank=rank(user),upcominggames=upcomingGames(user))
#Template(filename='htdocs/standaloneleaderboard.html', input_encoding = 'utf-8').render(leaderboardList=leaderboardBody, nextmatch=nextMatch, matchlog = generateMatchLog())

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
	cherrypy.server.socket_host='0.0.0.0'
	cherrypy.quickstart(HitzTourneyRunner(), config=configtest)