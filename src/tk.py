'''
Author:    max@embeddedprofessional.com
'''
import sys
try:
    assert sys.version_info[0] == 3
except AssertionError as e:
    print("Warning: Python 3 required but Python " + repr(sys.version_info[0]) +\
        " found, please install or change sys path")
    raise e
from tkinter import *
from threading import Thread, Lock
from random import randint
import time
import types

class Application(Frame):
    def __init__(self, master=None, screen_size=(1080, 720)):
        Frame.__init__(self, master)
        self.is_alive = True
        self.screen_w = screen_size[0]
        self.screen_h = screen_size[1]
        self.drawables = []
        self.letters = []
        self.mutex = Lock()
        self.i = 0
        self.inc_val = 10
        self.pack()
        self.createWidgets()

    def delete_stuff(self):
        self.w.delete(ALL)

    def draw_periodic(self):
        if self.i < 0:
            self.inc_val = -self.inc_val
        elif self.i >= (self.screen_w - 200):
            self.inc_val = -self.inc_val
        self.i += self.inc_val
        self.mutex.acquire()
        if randint(0,1) > 0:
            for drawable in self.drawables:
                self.w.move(drawable, self.inc_val, 0)
        else:
            for drawable in self.drawables:
                self.w.move(drawable, self.inc_val, 0)
        self.mutex.release()
        self.w.after(10, self.draw_periodic)

    def quit(self):
        self.is_alive = False
        Frame.quit(self)

    def clear_letters(self):
        for letter in self.letters: 
            self.w.delete(letter)

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT['text'] = 'QUIT'
        self.QUIT['fg']   = 'red'
        self.QUIT['command'] =  self.quit
        self.QUIT.pack({'side': 'left'})

        self.w = Canvas(self.master, width=self.screen_w, height=self.screen_h)

        self.id_buttons = []
        id_button = Button(self)
        id_button['text'] = "Clear"
        id_button.pack({'side':'left'})
        id_button['command'] = self.clear_letters
        self.id_buttons.append(id_button)

        h = 10
        w = 10
        x = 0
        y = 50
        self.drawables.append(self.w.create_rectangle(x, y, x+w, y+h, fill='#ff0'))
        y += 50
        self.drawables.append(self.w.create_rectangle(x, y, x+w, y+h, fill='#ff0'))
        self.w.pack()
        self.w.bind("<ButtonPress-1>", paint)
        self.w.bind("<ButtonPress-3>", do_thing)

    def mainloop(self):
        go = Thread(target=self.draw_periodic)
        go.start()
        Frame.mainloop(self)
        go.join()

def do_thing(event):
    for letter in app.letters:
        app.w.itemconfig(letter, text="COOL")

def paint(event):
    python_green = "#476042"
    x1, y1 = event.x - 10, event.y - 10
    x2, y2 = event.x + 10, event.y + 10
    
    #gimmicky AF
    global freq_inc
    app.mutex.acquire()
    app.letters.append(app.w.create_text(event.x, event.y, 
        font=helv200, text=freq_keys[freq_inc], activefill='red'))
    app.mutex.release()
    freq_inc = (freq_inc + 1) % len(freq_keys)
    #app.w.create_oval(x1, y1, x2, y2, fill = python_green)

root = Tk()
import tkinter.font as font
helv50 = font.Font(family='Helvetica', size=50, weight='bold')
helv100 = font.Font(family='Helvetica', size=100, weight='bold')
helv200 = font.Font(family='Helvetica', size=200, weight='bold')
helv250 = font.Font(family='Helvetica', size=250, weight='bold')
freq_keys = 'toawbcdsfmrhiyeglnpujkqzx'
freq_inc = 0
root.attributes("-fullscreen", True)

app = Application(master=root, screen_size=(1366, 768))
app.master.minsize(500, 500)
app.mainloop()
app.quit()