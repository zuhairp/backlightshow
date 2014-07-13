import time
import socket

from itertools import *

import numpy as np

"""
Code source:   http://bytes.com/topic/python/answers/576924-win32ui-vs-wxpy-screen-capture-multi-monitor

"""
import win32gui,  win32ui,  win32con, win32api
 
class ScreenHandle:
    pass

screenHandle = ScreenHandle() 

def init_stuff():
    hwnd = win32gui.GetDesktopWindow()
      
    # get complete virtual screen including all monitors
    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79
    w = vscreenwidth = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    h = vscreenheigth = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    l = vscreenx = win32api.GetSystemMetrics(SM_XVIRTUALSCREEN)
    t = vscreeny = win32api.GetSystemMetrics(SM_YVIRTUALSCREEN)
    r = l + w
    b = t + h


    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)

    screenHandle.hwndDC = hwndDC
    screenHandle.mfcDC = mfcDC
    screenHandle.w = w
    screenHandle.h = h
    screenHandle.r = r
    screenHandle.b = b
    screenHandle.l = l
    screenHandle.t = t



def get_screen_pixels():
    saveDC = screenHandle.mfcDC.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(screenHandle.mfcDC, screenHandle.w, screenHandle.h)
    saveDC.SelectObject(screenshot)
    saveDC.BitBlt((0, 0), (screenHandle.w, screenHandle.h),  screenHandle.mfcDC,  (screenHandle.l, screenHandle.t),  win32con.SRCCOPY)
    
    pixels = screenshot.GetBitmapBits(True) 

    saveDC.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    
    #hwnDC.DeleteDC()
    #mfcDC.DeleteDC()

    return pixels

"""
End of code taken from that website
"""

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

if __name__ == '__main__':
    run = True
    init_stuff()
    while(run):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect(('localhost', 2374))
            
            #start_time = time.time()
            try:
                pixels = get_screen_pixels()
            except Exception as e:
                print e
                continue # Not sure if fatal...
            pix_array = np.fromstring(pixels, dtype=np.uint8).reshape(len(pixels)/4, 4)
            pix_compressed = pix_array[::4]
            average_blue, average_green, average_red, _ = np.average(pix_compressed, axis=0) 
            #end_time = time.time()
            #print "Averaging time: %.02f ms" % (1000*(end_time-start_time))
            
            s.send(chr(int(average_red))+chr(int(average_green))+chr(int(average_blue)))

            run = True
        except KeyboardInterrupt:
            run = False

     
       
