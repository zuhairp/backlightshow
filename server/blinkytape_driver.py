"""
Runs a program that passed has been passed into the thread's mailbox

Programs are made of a list of frames that can be looped over

"""


import time
import threading

from Queue import Queue, Empty
from multiprocessing import Process, Pipe

from blinkytape import BlinkyTape

from color_generators import STEP_TIME, frame_generator, single_color_generator, socket_color_generator

from test_gui import TestGUI



current_time = lambda: int(round(time.time() * 1000))

class Instruction(object):
    def __init__(self, command=""):
        """
        Don't really expect to use this constructor

        The driver will expect certain attributes to exist depending on the command
        
        Makes the code slightly hard to follow, but also more readable... Tradeoffs...

        Here's a *ROUGH* expectation:

        command         expected attributes
        -------         -------------------
        "program"       frames
        "color"         color

        """
        self.command = command

class GUIBackend(object):
    """
    Implements a BlinkyTaple like interface for the GUI pipe
    
    """
    def __init__(self, output_pipe):
        self.pipe = output_pipe

    def display_color(self, data):
        self.pipe.send(data)

def run_gui(in_pipe):
    TestGUI(in_pipe)


class BlinkytapeDriver(threading.Thread):
    def __init__(self, port, mailbox):
        super(BlinkytapeDriver, self).__init__()
        self.mailbox = mailbox
        self.color_generator = None
        self.current_color = (0,0,0)

        if port == 'gui':
            # Start GUI process
            gui_out_connection, gui_in_connection = Pipe()
            self.led = GUIBackend(gui_out_connection)
            p = Process(target=run_gui, args=(gui_in_connection,))
            p.start()

        else:
            # TODO: Implement actual LED stuff
            self.led = BlinkyTape(port) 


    def get_color_generator(self, instruction):
        if instruction.command == "color":
            return single_color_generator(instruction.color)
        if instruction.command == "program":
            return frame_generator(instruction.frames)
        if instruction.command == "stream":
            return socket_color_generator()
        
    def step(self):
        """
        The update function of the run loop

        1) Check the mailbox
        2) If instruction in the mailbox, set program_generator to the appropriate generator
        3) Get the next value from the generator
        4) Display the color if it's not None
        5) Sleep for a bit - future enhacement: rate limit?
        
        """
        try:
            # Step 1
            new_instruction = self.mailbox.get_nowait() 
            self.mailbox.task_done()
            # Step 2
            self.color_generator = self.get_color_generator(new_instruction)

        except Empty:
            pass # There's nothing new
        
        # Step 3
        if self.color_generator == None:
            return
        next_color = self.color_generator.next()
        # Step 4
        if next_color is not None: 
            red, green, blue = next_color
            self.led.displayColor(red, green, blue)
            self.current_color = next_color


        # Step 5
        time.sleep(STEP_TIME) 

    def run(self):
        while True:
            self.step()
        

