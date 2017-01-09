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
from filters import MovingAverage
import settings # user settings

class Drawable(object):
    ''' Interface for objects that can be drawn on a tkinter Canvas '''
    def draw(self, canvas):
        raise NotImplementedError

    def update(self, canvas, pos):
        raise NotImplementedError

    def delete(self, canvas):
        raise NotImplementedError

class MouseLight(Drawable):
    ''' Coloured area that tracks current mouse '''
    def __init__(self, radius):
        self.radius = radius
        self.position = (0,0)
        self.i = 0
        self.countup = True
        self.handle = None

    def draw(self, canvas):
        self.handle = canvas.create_oval(
            self.position[0] - self.radius, self.position[1] - self.radius,
            self.position[0] + self.radius, self.position[1] + self.radius, 
            fill='blue')

    def update(self, canvas, pos):
        x,y = self.position = pos
        r = self.radius
        canvas.coords(self.handle, x-r, y-r, x+r, y+r)
        self.i += 1 if self.countup == True else -1
        if self.i == 255:
            self.countup = False
        elif self.i == 0:
            self.countup = True

        hex_val1 = '0x{:02x}'.format(self.i).replace('0x', '')
        hex_val2 = '0x{:02x}'.format(255-self.i).replace('0x', '')
        color_string = '#00' + hex_val1 + hex_val2
        canvas.itemconfigure(self.handle, fill=color_string)

class FunctionBox(Drawable):
    ''' Box executes a function when moused over '''
    def __init__(self, x1,y1,x2,y2, action=None, fill='black'):
        self.x1,self.y1,self.x2,self.y2 = x1,y1,x2,y2
        self.action = action
        self.selected = False
        self.fill = fill

    def draw(self, canvas):
        self.handle = canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2, fill=self.fill)

    def update(self, canvas, pos):
        x,y = pos
        if x > self.x1 and x < self.x2:
            if y > self.y1 and y < self.y2:
                if self.selected == False:
                    if self.action is not None:
                        self.action()
                    self.selected = True
                return
        self.selected = False

    def delete(self, canvas):
        canvas.delete(self.handle)

class Text(Drawable):
    ''' Updateable text field '''
    def __init__(self, x, y, font, size=5):
        self.x, self.y = (x,y)
        self.font = font
        self.text = ''
        self.size = size

    def draw(self, canvas):
        self.handle = canvas.create_text(self.x,self.y, 
            text=self.text, 
            font=self.font)

    def update(self, canvas, pos):
        x,y = pos
        canvas.itemconfigure(self.handle, text=self.text)

    def delete(self, canvas):
        canvas.delete(self.handle)

    def write(self, text):
        if text is not None:
            print('Text written: ' + text)
            self.text += text
        else:
            print('Warning, None value passed to Text.write()')

    def write_line(self, text):
        self.write(text + '\n')

    def clear(self):
        self.text = ''

class Key(Text):
    ''' Dynamic OnscreenKeyboard key '''
    def __init__(self, x,y, font, size=5):
        super(Key, self).__init__(x,y, font, size)
        self.selected = False

    def update(self, canvas, pos):
        x,y = pos
        super(Key, self).update(canvas, (x,y))
        #app.console.clear()
        #app.console.write_line(str(self.x) + ' ' + str(self.y))
        #app.console.write(str(x) + ' ' + str(y))
        if distance((x,y), (self.x, self.y)) < settings.letter_selection_radius:
            canvas.itemconfigure(self.handle, fill='red')
            self.selected = True
        else:
            canvas.itemconfigure(self.handle, fill='black')
            self.selected = False

class OnscreenKeyboard(Drawable):
    ''' Consists of a number of evenly spaced Text objects '''
    def __init__(self, font, shape, predictionary=Predictionary('sample_dict.txt')):
        row,col = shape
        if not isinstance(predictionary, Predictionary):
            print(str(type(predictionary)) + ' does not inherit from ' + str(Predictionary))
            print('Initialization of Keyboard failed, exiting')
            quit()
        self.set_rows_and_cols(row, col)
        self.keys = []
        self._predict = predictionary
        self._last_selection = None
        self._index_history = []
        self._at_end = False
        self.page = 0
        self.font = font

        i = 0
        for x in xrange(0, self.row*self.col):
            key = Key(0,0, self.font)
            key.write(self._predict.get_arrangement()[i])
            i += 1
            self.keys.append(key)

    def set_rows_and_cols(self, row, col):
        self.row, self.col = row, col

    def set_dimensions(self, x,y,w,h):
        self.x,self.y,self.w,self.h = (x,y,w,h)

    def draw(self, canvas):
        dx,dy = (self.w/self.col, self.h/self.row)
        x0,y0 =  (self.x + dx/2, self.y + dy/2)
        i,j = (0,0)
        for key in self.keys:
            y = y0 + i*dy
            x = x0 + j*dx
            j += 1
            if (j % self.col == 0):
                j = 0
                i += 1
            key.x,key.y = (x,y)
            key.draw(canvas)
            canvas.coords(key.handle, x,y)

    def update(self, canvas, pos):
        x,y = pos
        for key in self.keys: 
            key.update(canvas, (x,y))
            if key.selected == True:
                self._last_selection = key.text
                index = self.keys.index(key)
                if len(self._index_history) > 1:
                    if self._index_history[0] is not index:
                        self._index_history[1] = self._index_history[0]
                        self._index_history[0] = index
                        '''
                        if index == (self.col*self.row) - 1:
                            print('Reached end of page')
                            self._at_end = True
                        elif index == 0 and self._at_end == True:
                            self.next_page()
                            self._at_end = False
                        '''
                else:
                    self._index_history.append(index)
                    self._index_history.append(index)
            if key.text == self._last_selection and y < key.y:
                canvas.coords(key.handle, x,y)
            else:
                canvas.coords(key.handle, key.x,key.y)

    def delete(self, canvas):
        for key in self.keys: key.delete(canvas)

    def larger(self):
        size = self.font['size']
        self.font.configure(size=int(size*1.1))

    def smaller(self):
        size = self.font['size']
        self.font.configure(size=int(size*0.9))

    def process(self):
        self.page = 0
        if self._last_selection is not '':
            self._predict.process(self._last_selection)
            i = 0
            choices = self._predict.get_arrangement()
            for key in self.keys:
                key.selected = False
                key.clear()
                key.write(choices[i])
                i += 1
            app.console.write(self._last_selection)
            if self._last_selection == '.':
                app.console.clear()
            self._last_selection = ''

    def _change_page(self, page_inc):
        self.page = self.page + page_inc
        self._at_end = False
        del self._index_history[:]
        i = self.page*self.col*self.row
        choices = self._predict.get_arrangement()
        i %= len(choices)
        for key in self.keys:
            key.clear()
            key.write(choices[i])
            i = (i+1) % len(choices)

    def next_page(self):
        print('Turning the page forward...')
        self._change_page(1)

    def prev_page(self):
        print('Turning back the page...')
        self._change_page(-1)

def distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Application(Frame):
    def __init__(self, master=None, screen_size=(1080, 720)):
        # Create lists of drawable objects in app
        self.drawables = []
        # Application housekeeping
        Frame.__init__(self, master)
        self.is_alive = True
        self.screen_w = screen_size[0]
        self.screen_h = screen_size[1]
        self.last_mouse = (0,0)
        self.last_eye = (0,0)
        self.filter_type = MovingAverage(20)
        self.mutex = Lock()
        self.pack()
        self.createWidgets()

    def delete_stuff(self):
        self.canvas.delete(ALL)

    def draw_periodic(self):
        self.readEyeTrack('eyeStream.txt')
        self.mutex.acquire()
        for drawable in self.drawables:
            line = log.readline()
            points = line.split(",")
            if (points[0] == ''):
                quit()
            last_point = (int(float(points[0])/1.5),int(float(points[1])/1.5))
            drawable.update(self.canvas, last_point)
        self.mutex.release()
        self.canvas.after(5, self.draw_periodic) # slowed down to visualize inputs

    def quit(self):
        self.is_alive = False
        Frame.quit(self)

    def createWidgets(self):
        self.canvas = Canvas(self.master, width=self.screen_w, height=self.screen_h)
        w,h = (self.screen_w, self.screen_h)
        
        self.drawables.append(MouseLight(100))
        if (settings.dynamic_screen == 1):
            self.drawables.append(FunctionBox(w-h/4,     0,    w, h/5, self.quit, fill='red'))
            self.drawables.append(FunctionBox(    0, 4*h/5,  h/4,   h, kb.prev_page, fill='black'))
            self.drawables.append(FunctionBox(w-h/4, 4*h/5,    w,   h, kb.next_page, fill='black'))
            self.drawables.append(FunctionBox(    0,     0,  h/4, h/5, select_last_letter, fill='yellow'))
        self.console = Text(0,0, console_font)
        self.drawables.append(self.console)
        kb.set_dimensions(0,h/4,w,4*h/8)
        self.drawables.append(kb)

        for drawable in self.drawables:
            drawable.draw(self.canvas)

        self.canvas.itemconfigure(self.console.handle, anchor='nw')

        self.canvas.pack()
        self.canvas.bind("<Motion>", on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", on_left_click)
        self.canvas.bind("<ButtonPress-3>", on_right_click)

    def mainloop(self):
        go = Thread(target=self.draw_periodic)
        go.start()
        Frame.mainloop(self)
        go.join()

    def readEyeTrack(self, fileName):
        with open(fileName,'r') as f:
            try:
                contents = f.readline()
                x_y = contents.split(',')
                eye_x = int(float(x_y[0]))
                eye_y = int(float(x_y[1]))
                self.filter_type.calculate_average(eye_x, eye_y)
                self.last_eye = (self.filter_type.filtered_x, self.filter_type.filtered_y)
            except ValueError:
                pass

def on_mouse_move(event):
    app.last_mouse = (event.x, event.y)

def on_right_click(event):
    print('Right click')
    kb.smaller()

def on_left_click(event):
    print('Left click')
    kb.larger() 

def select_last_letter():
    kb.process()

if __name__ == '__main__':
    log = open('../../eyeCoordinatesLog1.txt', 'r')
    root = Tk()
    root.attributes("-fullscreen", True)
    w,h = (root.winfo_screenwidth(), root.winfo_screenheight())
    area = w*h
    console_font = font.Font(family='Helvetica', size=settings.console_font_size, weight='bold')
    kb_font = font.Font(family='Helvetica', size=settings.kb_font_size, weight='bold')
    kb = OnscreenKeyboard(kb_font, settings.kb_shape, Predictionary(settings.dict_filename))
    app = Application(master=root, screen_size=(w, h))
    app.master.minsize(500, 500)
    app.mainloop()
    app.quit()
