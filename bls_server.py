import cherrypy
import json

from Queue import Queue

from blinkytape_driver import *

class BacklightshowWebService(object):
    exposed = True

    current_color = 'magenta'

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        response = {}
        response['color'] = self.current_color
        return json.dumps(response)

    def PUT(self, color):
        self.current_color = color


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    }
    

    the_mailbox = Queue(1)
    simple_program = [Frame('red'), Frame('green'), Frame('blue')]
    the_mailbox.put(simple_program)
    led_driver = BlinkytapeDriver(the_mailbox)
    led_driver.daemon = True
    led_driver.start()

    cherrypy.quickstart(BacklightshowWebService(), '/', conf)

