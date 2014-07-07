import os
import json
from Queue import Queue

import cherrypy

from blinkytape_driver import *


the_mailbox = Queue(1)

class BacklightshowApp(object):
    @cherrypy.expose
    def index(self):
        return file('index.html')

class BacklightshowWebService(object):
    exposed = True

    current_color = 'magenta'

    program = [
        Frame(color=(0,0,0))
    ]

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        response = {}
        response['color'] = self.current_color
        return json.dumps(response)

    def PUT(self, program):
        self.program = self.interpret_program(program)
        the_mailbox.put(self.program)

    def interpret_program(self, program):
        data = json.loads(program)
        frames_data = data['frames']
        frames = []
        for frame in frames_data:
            frames.append(Frame(**frame))
        return frames



if __name__ == '__main__':
    conf = {
        '/' : {
            'tools.sessions.on' : True,
            'tools.staticdir.root' : os.path.abspath(os.getcwd())
        },
        '/controller': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        },
        '/static' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : './static_content'
        }
    }
    
    led_driver = BlinkytapeDriver(the_mailbox)
    led_driver.daemon = True
    led_driver.start()

    webapp = BacklightshowApp()
    webapp.controller = BacklightshowWebService()

    cherrypy.quickstart(webapp, '/', conf)

