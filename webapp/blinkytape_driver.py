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
    def __init__(self, **kwargs):
        self.color = kwargs.get("color") # RGB tuple or "average"
        self.duration = kwargs.get("duration", 1) # Time to hold the frame
        self.transition = kwargs.get("transition", 0) # Time to blend into the next frame

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
        red_delta, green_delta, blue_delta = (0, 0, 0)
        output_red, output_green, output_blue = program[current_frame_index].color

        while True: # Infinite generator
            time_left -= STEP_TIME

            if time_left <= 0:

                if state == "TRANSITION": # Transition just ended
                    current_frame_index += 1 
                    if current_frame_index == program_length:
                        current_frame_index = 0

                    time_left = program[current_frame_index].duration 
                    red_delta, green_delta, blue_delta = (0, 0, 0)
                    output_red, output_green, output_blue = program[current_frame_index].color
                    state = "HOLD"

                elif state == "HOLD": # Hold just ended
                    transition_time = program[current_frame_index].transition
                    if transition_time != 0:
                        next_frame_index = current_frame_index + 1
                        next_frame_index = 0 if next_frame_index == program_length else next_frame_index

                        target_red, target_green, target_blue = program[next_frame_index].color
                        current_red, current_green, current_blue = program[current_frame_index].color

                        red_delta = STEP_TIME * (float(target_red) - current_red) / transition_time 
                        green_delta = STEP_TIME * (float(target_green) - current_green) / transition_time
                        blue_delta = STEP_TIME * (float(target_blue) - current_blue) / transition_time

                        time_left = program[current_frame_index].transition

                    state = "TRANSITION"

            
            output_red += red_delta
            output_green += green_delta
            output_blue += blue_delta

            if(output_red < 0): output_red = 0
            if(output_red > 255): output_red = 255

            if(output_green < 0): output_green = 0
            if(output_green > 255): output_green = 255
            
            if(output_blue < 0): output_blue = 0
            if(output_blue > 255): output_blue = 255
            
            output_color = "#%02x%02x%02x" % (int(output_red), int(output_green), int(output_blue))

            yield output_color 
        
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
        if self.program_generator == None:
            return
        next_color = self.program_generator.next()
        # Step 4
        gui_queue.put(next_color)

        # Step 5
        time.sleep(STEP_TIME) # Running about 40Hz

    def run(self):
        while True:
            self.step()
        

