"""
Runs a program that passed has been passed into the thread's mailbox

Programs are made of a list of frames that can be looped over

"""


import time
import threading

from Queue import Queue, Empty

from multiprocessing import Queue as MPQueue, Process

from test_gui import TestGUI

STEP_TIME = 0.025

gui_queue = MPQueue()

current_time = lambda: int(round(time.time() * 1000))

class Frame(object):
    def __init__(self, color, duration=1, transition=0):
        self.color = color # RGB tuple or "average"
        self.duration = duration # Time to hold the frame
        self.transition = transition # Time to blend into the next frame

def run_gui():
    TestGUI(gui_queue)

class BlinkytapeDriver(threading.Thread):
    def __init__(self, mailbox):
        super(BlinkytapeDriver, self).__init__()
        self.mailbox = mailbox
        self.program_generator = None

        # Start GUI process
        p = Process(target=run_gui)
        p.start()


    def get_program_generator(self, program):
        """
        Returns a generator that yields the next color value to set
        Assumes that roughly 25 ms have passed

        """
        state = "HOLD" 
        current_frame_index = 0
        program_length = len(program)

        time_left = program[current_frame_index].duration
        while True: # Infinite generator
            time_left -= STEP_TIME
            if time_left <= 0:
                current_frame_index += 1 # Ignoring transition time for now
                if current_frame_index == program_length:
                    current_frame_index = 0

                time_left = program[current_frame_index].duration 

            yield program[current_frame_index].color
        
    def step(self):
        """
        1) Check the mailbox
        2) If new program in the mailbox, set program_generator to the new program
        3) Get the next value from the generator
        4) Write to file (or serial)
        5) Sleep for a bit - future enhacement: rate limit?
        """
        try:
            # Step 1
            new_program = self.mailbox.get_nowait() 
            self.mailbox.task_done()
            # Step 2
            self.program_generator = self.get_program_generator(new_program)

        except Empty:
            pass # There's nothing new

        # Step 3
        next_color = self.program_generator.next()
        # Step 4
        gui_queue.put(next_color)

        # Step 5
        time.sleep(STEP_TIME) # Running about 40Hz

    def run(self):
        while True:
            self.step()
        

