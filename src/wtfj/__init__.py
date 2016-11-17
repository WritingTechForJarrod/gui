'''
Writing Tech for Jarrod
Gui module classes and objects
max.prokopenko@gmail.com

'canvas' in these methods is a Tkinter(tkinter if py3) canvas
'''
import logging
import settings
from predictionary import Predictionary
from filters import *

def distance(pos1,pos2):
    ''' Euclidean distance '''
    x1,y1 = pos1
    x2,y2 = pos2
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

def make_color(r_uint8,g_uint8,b_uint8):
    ''' Color in 24-bit RGB format to '0x#######' string format '''
    r = '0x{:02x}'.format(r_uint8).replace('0x','')
    g = '0x{:02x}'.format(g_uint8).replace('0x','')
    b = '0x{:02x}'.format(b_uint8).replace('0x','')
    return '#'+r+g+b

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
        canvas.itemconfigure(self.handle,fill=make_color(0,self.i,255-self.i))

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
    def __init__(self,x,y,font, size=5):
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

class Key2(Text):
    ''' Dynamic OnscreenKeyboard key '''
    def __init__(self, x,y, font, size=5):
        super(Key2, self).__init__(x,y, font, size)
        self.selected = False
        self.selection_score = 0
        self.selection_threshold = settings.selection_delay

    def update(self, canvas, pos):
        x,y = pos
        super(Key2, self).update(canvas, (x,y))
        #app.console.clear()
        #app.console.write_line(str(self.x) + ' ' + str(self.y))
        #app.console.write(str(x) + ' ' + str(y))
        if distance((x,y), (self.x, self.y)) < settings.letter_selection_radius:
            self.selection_score += 1
        else:
            self.selection_score = 0
        if self.selection_score > self.selection_threshold:
            self.selection_score = 0
            self.selected = True
        else:
            self.selected = False
        r = (self.selection_score*255) // self.selection_threshold
        canvas.itemconfigure(self.handle, fill=make_color(r,0,0))

class OnscreenKeyboard(Drawable):
    ''' Consists of a number of evenly spaced Text objects '''
    def __init__(self, font, shape, predictionary):
        self.logger = logging.getLogger('kb')
        row,col = shape
        if not isinstance(predictionary, Predictionary):
            self.logger.critical(str(type(predictionary)) + ' does not inherit from ' + str(Predictionary))
            self.logger.critical('Initialization of Keyboard failed, exiting...')
            quit()
        self.set_rows_and_cols(row, col)
        self.keys = []
        self._write = lambda x: self.logger.warning('_write called, function has no handler, attempted to write '+str(x))
        self._speak = lambda x: self.logger.warning('_speak called, function has no handler, attempted to speak '+str(x))
        self._clear = lambda x: self.logger.warning('_clear called, function has no handler')
        self._predict = predictionary
        self._last_selection = None
        self._index_history = []
        self._at_end = False
        self.page = 0
        self.font = font

        i = 0
        for x in xrange(0, self.row*self.col):
            if settings.kb_version == 2:
                key = Key2(0,0, self.font)
            else:
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
                if settings.kb_version == 2:
                    self._speak(self._last_selection+' ') # Do always before processing
                    self.process()
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
        '''
        Processes the last key pressed through the predictionary 
        Replaces the key with next key given by predictionary
        Clears last selection, console if '.' selected
        '''
        self.page = 0
        if self._last_selection is not '':
            self._predict.process(self._last_selection) # TODO more flexible letter provider interface
            i = 0
            choices = self._predict.get_arrangement()
            for key in self.keys:
                key.selected = False
                key.clear()
                key.write(choices[i])
                i += 1
            self._write(self._last_selection)
            if self._last_selection == '.':
                self._clear()
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

    def attach_write_callback(self, write_function):
        ''' 
        Set destination for letters that are entered into kb buffer
        Write function takes argument of char to be written out
        '''
        self._write = write_function

    def attach_speak_callback(self, speak_function):
        '''
        Set output function for speech
        Speak function takes argument of phrase to be spoken
        '''
        self._speak = speak_function

    def attach_clear_callback(self, clear_function):
        '''
        Set function to call on clearing kb buffer
        Clear function takes no arguments
        '''
        self._clear = clear_function

    def next_page(self):
        logging.getLogger('app').debug('Turning the page forward...')
        self._change_page(1)

    def prev_page(self):
        logging.getLogger('app').debug('Turning back the page...')
        self._change_page(-1)

if __name__ == '__main__':
    pass