"""
Various infinite generators that create colors according to some criteria

"""


from Queue import Empty
from multiprocessing import Queue, Process

from twisted.internet import protocol, reactor

STEP_TIME = 0.025  # Running about 40Hz

class Frame(object):
    def __init__(self, color, duration=1.0, transition=0):
        self.color = color
        self.duration = float(duration) # The duration to hold the color
        self.transition = float(transition) # The duration to transition to the next color


def frame_generator(program):
    """
    Returns a generator that yields the next color value to set
    Assumes that roughly STEP_TIME has passed

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
        
        # TODO: Intelligently return None if there's no update to the color
        yield (int(output_red), int(output_green), int(output_blue))


def single_color_generator(color):
    """
    Color generator that generates a single color and then infinitely returns None

    """
    yield color
    while True: 
        yield None # So that color is written only once to serial 


socket_queue = Queue()
socket_process = None
#----------------- Socket Color Networking Code (Runs in separate process) ----------------------#
class LEDSocketControl(protocol.Protocol):
    buffered = ""
    def dataReceived(self, data):
        global socket_queue
        self.buffered += data
        while len(self.buffered) >= 3:
            # Send one RGB value at a time
            write_data, self.buffered = self.buffered[0:3], self.buffered[3:]
            rgb = [ord(c) for c in write_data]
            socket_queue.put(rgb)

class LEDSocketControlFactory(protocol.Factory):
    protocol = LEDSocketControl

def run_socket_controller():
    reactor.listenTCP(2374, LEDSocketControlFactory())
    reactor.run()

#----------------- Socket Color Generator (Runs in this thread) ----------------------#
def socket_color_generator():
    global socket_queue
    global socket_process

    #socket_queue = Queue()
    if socket_process is None:
        print "Starting socket process"
        socket_process = Process(target=run_socket_controller)
        socket_process.start()

    while True:
        try: 
            yield socket_queue.get_nowait()
        except Empty:
            yield None


if __name__ == '__main__':
    run_socket_controller()

