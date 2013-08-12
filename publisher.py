
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import json, cherrypy
from model import * 
from matchups import *

SUBSCRIBERS = set()

class Publisher(WebSocket):
    events = {'gettop10games':generateGamePossibilities}
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        print str(self) + "connected"
        SUBSCRIBERS.add(self)

    def closed(self, code, reason=None):
        SUBSCRIBERS.remove(self)
    def received_message(self, message):
    	pythonmessage = json.loads(message)
    	eventname = pythonmessage['event']
    	eventdata = pythonmessage['data']

    	if events[eventname](eventdata):
    		print "%s triggered successfully with data %s" % eventname, str(eventdata)
    	else:
            print "\nevent %s not found. Data: %s \n From message: %s\n" % eventname, str(eventdata), str(message)
    #for conn in SUBSCRIBERS:
    #    conn.send(json.dumps({"event":'leaderboard', 'data':returnString}))

def sendMessage(event, data):
    #
    for conn in SUBSCRIBERS:
        conn.send(json.dumps({'event':event, 'data':data}))