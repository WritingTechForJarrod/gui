'''
Author:    max@embeddedprofessional.com
'''
from __future__ import print_function
from __future__ import unicode_literals
import sys
try:
    assert sys.version_info[0] == 3
    from tkinter import *
    import tkinter.font as font
except AssertionError as e:
    from Tkinter import *
    import tkFont as font
from threading import Thread, Lock
from random import randint
import time
import types
from math import atan2, pi
from predictionary import Predictionary

class Letter():
    def __init__(self, char, handle, (x, y)):
        self.char = char
        self.handle = handle # ex: app.canvas.configure
        self.position = (x, y)

predict = Predictionary('sample_dict.txt')
quit()

def distance((x1,y1), (x2,y2)):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Application(Frame):
    def __init__(self, master=None, screen_size=(1080, 720)):
        Frame.__init__(self, master)
        self.is_alive = True
        self.screen_w = screen_size[0]
        self.screen_h = screen_size[1]
        self.drawables = []
        self.letters = []
        self.letter_added = False
        self.last_letter = None
        self.last_char = None
        self.last_mouse = (0,0)
        self.mutex = Lock()
        self.i = 0
        self.inc_val = 5
        self.letters_hovered = 0
        self.pack()
        self.createWidgets()
        self.console_text = self.w.create_text(self.screen_w/2, 50, font=helv100, text='')

    def delete_stuff(self):
        self.w.delete(ALL)

    def next(self):
        global freq_inc
        char = freq_keys[freq_inc]
        freq_inc = (freq_inc + 1) % len(freq_keys)
        return char

    def replace_letters(self):
        for letter in self.letters:
            letter.char = self.next()
            self.w.itemconfigure(letter.handle, text=letter.char)

    def update_console(self,string):
        text = self.w.itemcget(self.console_text, 'text')
        if string == '-':
            freq_inc = 0
            self.replace_letters()
            text += ' '
        else: 
            text += self.last_char
        self.w.itemconfigure(self.console_text, text=text)

    def draw_periodic(self):
        global freq_inc
        global freq_keys

        # change color of letter if close to mouse
        for letter in self.letters:
            key = self.w.itemcget(letter.handle, 'text')
            position = letter.position
            if distance(self.last_mouse, position) < 100:
                self.w.itemconfigure(letter.handle, fill='red')
                if self.last_letter is not None:
                    if self.last_letter is not letter:
                        self.letters_hovered += 1
                self.last_letter = letter
                self.last_char = str(letter.char)
            else:
                self.w.itemconfigure(letter.handle, fill='black')
                if self.letters_hovered >= len(self.letters):
                    print('Adding new letters')
                    self.letters_hovered = 0
                    self.replace_letters()

        # draw angle of selector and mouse spotlight
        '''
        start = self.w.itemcget(self.selector, 'start')
        dx = self.last_mouse[0] - self.screen_w/2
        dy = self.last_mouse[1] - 2*self.screen_h/3
        d = (dx**2 + dy**2)**0.5
        if d > 2*self.selector_radius:
            selector_angle = -atan2(dy,dx)*180/pi
            self.w.itemconfigure(self.selector, start=selector_angle)
        elif d < self.selector_radius: 
            if (self.letter_added is False) and (self.last_char is not None):
                self.update_console(self.last_char)
                freq_inc = 0
                freq_keys = 'etao-inshrdlcumwfgypbvkjxqz'
                self.replace_letters()
                self.letter_added = True
                #next_letter = self.next()
                #self.last_letter.char = next_letter
                #self.w.itemconfigure(self.last_letter.handle, text=next_letter)
        else:
            self.letter_added = False
        '''
        if self.last_mouse[1] > self.screen_h/2:
            if (self.letter_added is False) and (self.last_char is not None):
                self.update_console(self.last_char)
                freq_inc = 0
                freq_keys = 'etao-inshrdlcumwfgypbvkjxqz'
                self.replace_letters()
                self.letter_added = True
        else:
            self.letter_added = False

        self.w.coords(self.mouselight, 
            self.last_mouse[0] - self.mouselight_radius, 
            self.last_mouse[1] - self.mouselight_radius,
            self.last_mouse[0] + self.mouselight_radius, 
            self.last_mouse[1] + self.mouselight_radius
            )

        self.i += self.inc_val
        if self.i < 0:
            self.i = 0
            self.inc_val = -self.inc_val
        elif self.i >= 255:
            self.i = 255
            self.inc_val = -self.inc_val
        self.mutex.acquire()
        hex_val1 = '0x{:02x}'.format(self.i).replace('0x', '')
        hex_val2 = '0x{:02x}'.format(255-self.i).replace('0x', '')
        color_string = '#00' + hex_val1 + hex_val2
        self.w.itemconfigure(self.mouselight, fill=color_string)
        self.mutex.release()
        self.w.after(10, self.draw_periodic)

    def quit(self):
        self.is_alive = False
        Frame.quit(self)

    def add_letter(self, letter, (x, y)):
        handle = self.w.create_text(x, y, font=helv250, text=letter)
        new_letter = Letter(letter, handle, (x, y))
        self.letters.append(new_letter)

    def clear_letters(self):
        global freq_inc
        global freq_keys
        freq_inc = 0
        freq_keys = 'toawbcdsfmrhiyeglnpujkqzx'
        self.w.itemconfigure(self.console_text, text='')
        self.replace_letters()

    def createWidgets(self):
        global freq_inc
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

        self.mouselight_radius = mouselight_radius = 150
        self.selector_radius = selector_radius = 200
        w,h = (self.screen_w, self.screen_h)
        self.mouselight = self.w.create_oval(
            w/2 - mouselight_radius, 2*h/3 - mouselight_radius,
            w/2 + mouselight_radius, 2*h/3 + mouselight_radius, 
            fill='blue')
        '''
        self.w.create_oval(
            w/2 - selector_radius, 2*h/3 - selector_radius,
            w/2 + selector_radius, 2*h/3 + selector_radius, 
            fill='green')
        self.selector = self.w.create_arc(
            w/2 - selector_radius, 2*h/3 - selector_radius,
            w/2 + selector_radius, 2*h/3 + selector_radius, 
            fill='red', extent=180, start=0)
        '''
        self.bar_selector = self.w.create_rectangle(0, h/2, w, h, fill='green')
        self.w.pack()
        x1,x2,y1,y2 = w/6, 5*w/6, h/4, 3*h/4
        x3 = 1*w/3
        x4 = 2*w/3
        self.add_letter('t', (x1,y1))
        self.add_letter('o', (x3,y1))
        self.add_letter('a', (x4,y1))
        self.add_letter('w', (x2,y1))
        self.add_letter('b', (w/2,y1))
        freq_inc = 4
        self.w.bind("<Motion>", on_mouse_move)
        self.w.bind("<ButtonPress-1>", on_left_click)
        self.w.bind("<ButtonPress-3>", on_right_click)

    def mainloop(self):
        go = Thread(target=self.draw_periodic)
        go.start()
        Frame.mainloop(self)
        go.join()

def on_mouse_move(event):
    app.last_mouse = (event.x, event.y)

def on_right_click(event):
    pass
def on_left_click(event):
    #python_green = "#476042"
    #gimmicky AF
    global freq_inc
    app.mutex.acquire()
    app.mutex.release()
    freq_inc = (freq_inc + 1) % len(freq_keys)
    #app.w.create_oval(x1, y1, x2, y2, fill = python_green)

root = Tk()
helv50 = font.Font(family='Helvetica', size=50, weight='bold')
helv100 = font.Font(family='Helvetica', size=100, weight='bold')
helv200 = font.Font(family='Helvetica', size=200, weight='bold')
helv250 = font.Font(family='Helvetica', size=250, weight='bold')
freq_keys = 'toawbcdsfmrhiyeglnpujkqzx'
freq_inc = 0
root.attributes("-fullscreen", True)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app = Application(master=root, screen_size=(screen_width, screen_height))
app.master.minsize(500, 500)
app.mainloop()
app.quit()