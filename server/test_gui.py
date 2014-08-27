import random
from Tkinter import * 



class TestGUI(object):
    def __init__(self, input_pipe):
        self.master = Tk()
        self.canvas = Canvas(self.master, width=150, height=150)
        self.canvas.pack()
        self.canvas.create_rectangle(0, 0, 150, 150, fill="#000000", tags='color_swatch')
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
