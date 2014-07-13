import random
from Tkinter import * 



class TestGUI(object):
    def __init__(self, input_pipe):
        self.master = Tk()
        self.canvas = Canvas(self.master, width=200, height=100)
        self.canvas.pack()
        self.canvas.create_rectangle(50, 25, 150, 75, fill="#12BB45", tags='color_swatch')
        self.pipe = input_pipe


        update_color(self)
        self.master.mainloop()


def update_color(gui):

    color_exists = gui.pipe.poll()
    if color_exists:
        the_color = gui.pipe.recv()
        the_color = "#%02x%02x%02x" % tuple(the_color)
        gui.canvas.itemconfig('color_swatch', fill=the_color) 

    gui.master.after(10, update_color, gui)

if __name__ == "__main__":
    t = TestGUI(None)
