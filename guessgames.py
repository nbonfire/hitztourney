import cherrypy
from mako.template import Template
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import json

from model import *
from matchups import *
from publisher import *

WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

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
	cherrypy.quickstart(HitzApp(), config=configtest)