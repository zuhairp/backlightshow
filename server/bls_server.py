import os
import json
import socket
import argparse
from Queue import Queue

import cherrypy

import color_lookup

from bls_config import *
from blinkytape_driver import *
from color_generators import Frame

bls_directory = os.path.dirname(os.path.abspath(__file__))

the_mailbox = Queue(1)
#TODO: Don't open up the port right away...
led_driver = BlinkytapeDriver(port=LED_SERIAL_PORT, mailbox=the_mailbox)
led_driver.daemon = True


class BacklightshowApp(object):
    @cherrypy.expose
    def index(self):
        file_name = "%s/../webapp/index.html" % bls_directory
        return file(os.path.abspath(file_name))
    
    #
    # TODO: Make an entire colors api
    #
    @cherrypy.expose
    def colors(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return file('colors.json')

class BacklightshowWebService(object):
    exposed = True

    program = [
        Frame(color=(0,0,0))
    ]

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        response = {}
        red, green, blue = led_driver.current_color
        hex_color = color_lookup.rgb_to_hex(red, green, blue)
        response['color'] = hex_color
        return json.dumps(response)

    def PUT(self, **data):
        self.current_command = data # Want to save exactly what we got
        
        command_type = self.guess_instruction_type(data)
        
        inst = Instruction(command=command_type)
        if command_type == "color":
            the_color = self.get_rgb(data['color'])
            if the_color is None:
                return
            inst.color = the_color
        elif command_type == "program":
            print data['frames']
            the_frames = self.create_frame_list(json.loads(data['frames']))
            if the_frames is None or len(the_frames) == 0:
                return
            inst.frames = the_frames

        the_mailbox.put(inst)


    def guess_instruction_type(self, request_dict):
        if "mode" in request_dict:
            return request_dict["mode"]  # That was easy... they told us :-)

        if "frames" in request_dict:
            return "program"
        
        if "color" in request_dict:
            return "color"

    def create_frame_list(self, frames_data):
        frames = []
        for frame in frames_data:
            the_color = self.get_rgb(frame['color'])
            if the_color is None:
                return
            frame['color'] = the_color
            frames.append(Frame(**frame))
        return frames

    def get_rgb(self, color_code):
        try:
            if color_code[0] == '#': # If it begins with a #, assume it is a hex code
                return color_lookup.hex_to_rgb(color_code[1:])
            else:
                return color_lookup.get_rgb_by_name(color_code, raise_exception=True)
        except Exception:
            cherrypy.response.headers['Status'] = "400 Unable to resolve color '%s'" % color_code




if __name__ == '__main__':
    conf = {
        '/' : {
            'tools.sessions.on' : True,
            'tools.staticdir.root' : os.path.abspath(os.getcwd()),
            'tools.caching.on' : False
        },
        '/controller': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        },
        '/static' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : '../webapp',
            'tools.caching.on' : False
        }
    }

    # On startup, set the LEDs to white
    startup_instruction = Instruction(command="color")
    startup_instruction.color = (255,255,255)
    the_mailbox.put(startup_instruction)

    led_driver.start()
    
    webapp = BacklightshowApp()
    webapp.controller = BacklightshowWebService()

    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.server.socket_host = SERVER_ADDRESS

    cherrypy.quickstart(webapp, '/', conf)

