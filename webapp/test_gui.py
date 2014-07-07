import random
from Tkinter import * 
from threading import Thread

from Queue import Queue, Empty
from multiprocessing import Queue as MPQueue


color_queue = Queue(maxsize=1)

class ColorFetcher(Thread):
    def __init__(self, input_queue):
        super(ColorFetcher, self).__init__()
        self.queue = input_queue # The queue that communicates with the driver

    def run(self):
        while True:
            try:
                color_command = self.queue.get_nowait()
                color_queue.put(color_command)
            except Empty:
                pass



class TestGUI(object):
    def __init__(self, input_queue):
        self.master = Tk()
        self.canvas = Canvas(self.master, width=200, height=100)
        self.canvas.pack()
        self.canvas.create_rectangle(50, 25, 150, 75, fill="#12BB45", tags='color_swatch')

        self.fetcher = ColorFetcher(input_queue)
        self.fetcher.daemon = True
        self.fetcher.start()

        update_color(self)
        self.master.mainloop()


def update_color(gui):
    try:
        the_color = color_queue.get_nowait()
        color_queue.task_done()
        gui.canvas.itemconfig('color_swatch', fill=the_color) 
    except Empty:
        pass

    gui.master.after(10, update_color, gui)

if __name__ == "__main__":
    t = TestGUI(None)
