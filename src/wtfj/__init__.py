'''
Writing Tech for Jarrod
Gui module classes and objects
max.prokopenko@gmail.com
'canvas' in these methods is a Tkinter(tkinter if py3) canvas
'''
import logging
import settings
import cluster
import winsound
import thread
from predictionary import Predictionary
from filters import *
from decorators import *
from sklearn import svm, datasets
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
from collections import Counter

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

def speak_character(character):
    if (character == 'a:m'):
        winsound.PlaySound('audio_files/a_to_m_sound.wav',winsound.SND_FILENAME)
    elif (character == 'n:z'):
        winsound.PlaySound('audio_files/n_to_z_sound.wav',winsound.SND_FILENAME)
    elif (character == 'a'):
        winsound.PlaySound('audio_files/a_sound.wav',winsound.SND_FILENAME)
    elif (character == 'b'):
        winsound.PlaySound('audio_files/b_sound.wav',winsound.SND_FILENAME)
    elif (character == 'c'):
        winsound.PlaySound('audio_files/c_sound.wav',winsound.SND_FILENAME)
    elif (character == 'd'):
        winsound.PlaySound('audio_files/d_sound.wav',winsound.SND_FILENAME)
    elif (character == 'e'):
        winsound.PlaySound('audio_files/e_sound.wav',winsound.SND_FILENAME)
    elif (character == 'f'):
        winsound.PlaySound('audio_files/f_sound.wav',winsound.SND_FILENAME)
    elif (character == 'g'):
        winsound.PlaySound('audio_files/g_sound.wav',winsound.SND_FILENAME)
    elif (character == 'h'):
        winsound.PlaySound('audio_files/h_sound.wav',winsound.SND_FILENAME)
    elif (character == 'i'):
        winsound.PlaySound('audio_files/i_sound.wav',winsound.SND_FILENAME)
    elif (character == 'j'):
        winsound.PlaySound('audio_files/j_sound.wav',winsound.SND_FILENAME)
    elif (character == 'k'):
        winsound.PlaySound('audio_files/k_sound.wav',winsound.SND_FILENAME)
    elif (character == 'l'):
        winsound.PlaySound('audio_files/l_sound.wav',winsound.SND_FILENAME)
    elif (character == 'm'):
        winsound.PlaySound('audio_files/m_sound.wav',winsound.SND_FILENAME)
    elif (character == 'n'):
        winsound.PlaySound('audio_files/n_sound.wav',winsound.SND_FILENAME)
    elif (character == 'o'):
        winsound.PlaySound('audio_files/o_sound.wav',winsound.SND_FILENAME)
    elif (character == 'p'):
        winsound.PlaySound('audio_files/p_sound.wav',winsound.SND_FILENAME)
    elif (character == 'q'):
        winsound.PlaySound('audio_files/q_sound.wav',winsound.SND_FILENAME)
    elif (character == 'r'):
        winsound.PlaySound('audio_files/r_sound.wav',winsound.SND_FILENAME)
    elif (character == 's'):
        winsound.PlaySound('audio_files/s_sound.wav',winsound.SND_FILENAME)
    elif (character == 't'):
        winsound.PlaySound('audio_files/t_sound.wav',winsound.SND_FILENAME)
    elif (character == 'u'):
        winsound.PlaySound('audio_files/u_sound.wav',winsound.SND_FILENAME)
    elif (character == 'v'):
        winsound.PlaySound('audio_files/v_sound.wav',winsound.SND_FILENAME)
    elif (character == 'w'):
        winsound.PlaySound('audio_files/w_sound.wav',winsound.SND_FILENAME)
    elif (character == 'x'):
        winsound.PlaySound('audio_files/x_sound.wav',winsound.SND_FILENAME)
    elif (character == 'y'):
        winsound.PlaySound('audio_files/y_sound.wav',winsound.SND_FILENAME)
    elif (character == 'z'):
        winsound.PlaySound('audio_files/z_sound.wav',winsound.SND_FILENAME)
    elif (character == '{}'):
        winsound.PlaySound('audio_files/space_sound.wav',winsound.SND_FILENAME)
    elif (character == '<'):
        winsound.PlaySound('audio_files/undo_sound.wav',winsound.SND_FILENAME)

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
            fill='blue', 
            outline='blue'
        )

    def update(self, canvas, pos):
        x,y = self.position = pos
        r = self.radius
        canvas.coords(self.handle, int(x-r), int(y-r), int(x+r), int(y+r))
        self.i += 1 if self.countup == True else -1
        if self.i == 255:
            self.countup = False
        elif self.i == 0:
            self.countup = True
        canvas.itemconfigure(self.handle,fill=make_color(0,self.i,255-self.i))
        canvas.itemconfigure(self.handle,outline=make_color(0,self.i,255-self.i))

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
    def __init__(self,x,y,font, size=5,justify='left'):
        self.x, self.y = (x,y)
        self.font = font
        self.text = ''
        self.size = size
        self.justify = justify

    def draw(self, canvas):
        self.handle = canvas.create_text(
            self.x,self.y, 
            text=self.text, 
            font=self.font,
            justify=self.justify,
            tags = "key_tag"
        )

    def update(self, canvas, pos):
        x,y = pos
        canvas.itemconfigure(self.handle, text=self.text)

    def delete(self, canvas):
        canvas.delete(self.handle)

    def write(self, text):
        if text is not None:
            self.text += text
        else:
            print('Warning, None value passed to Text.write()')

    def write_line(self, text):
        self.write(text+'\n')

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
        self._centroid_x, self._centroid_y = (0,0) # x,y selection centroid

    def set_centroid(self, centroid):
        self._centroid_x, self._centroid_y = centroid

    def draw(self, canvas):
        if (settings.kb_version == 2):
            r = settings.letter_selection_radius
            sx,sy = (self._centroid_x,self._centroid_y)
            self._circle_handle = canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill='#ddd', outline='white', tags = "key_tag")
            super(Key2,self).draw(canvas)

    def delete(self, canvas):
        super(Key2, self).delete(canvas)
        canvas.delete(self._circle_handle)

    def update(self, canvas, pos):
        ''' 
        Checks if the selector is in the field of the key selection radius.
        Takes the difference of the last two screen update times to calculate
        the time since the key was last updated, if selected adds that time to the
        selection_score counter, if not selected subtracts half that time.
        Once selection_score reaches a set threshold the key is marked as selected
        '''
        x,y = pos

        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        #canvas.coords(self._circle_handle, sx-r, sy-r, sx+r, sy+r)

        super(Key2, self).update(canvas, (x,y))
        if len(timelog) >= 2:
            if distance((x,y), (self._centroid_x, self._centroid_y)) < settings.letter_selection_radius:
                self.selection_score += timelog[-1][1]-timelog[-2][1]
            else:
                self.selection_score -= (timelog[-1][1]-timelog[-2][1])/2
                self.selection_score = max(0,self.selection_score)

        if self.selection_score > settings.selection_delay:
            self.selection_score = 0
            self.selected = True
        else:
            self.selected = False
        r = int((self.selection_score*255) / settings.selection_delay)
        canvas.itemconfigure(self.handle, fill=make_color(r,0,0))

class Key3(Text):
    '''Dynamic on-screen key used for max spacing layout (kb_version 3)'''
    #Note: Currently inflexible key, specifically designed for 2 key layout on horizontal edges
    def __init__(self, x,y, font, size=5):
        super(Key3, self).__init__(x,y, font, size)
        self.selected = False
        self.selection_score = 0
        self._centroid_x, self._centroid_y = (0,0) # x,y selection centroid
        self._x0, self._y0 = (0,0) # upper left corner
        self._x1, self._y1 = (0,0) # bottom right corner

    def delete(self, canvas):
        super(Key3, self).delete(canvas)
        canvas.delete(self._circle_handle)

    def set_corners(self, uleft, bright):
        self._x0, self._y0 = uleft
        self._x1, self._y1 = bright

    def set_centroid(self, centroid):
        self._centroid_x, self._centroid_y = centroid

    def contains(self, pos):
        '''Determines if pos lies within the key'''
        x,y = pos

        if (x > self._x0 and x < self._x1 and y > self._y0 and y < self._y1):
            return True
        return False

    def draw(self, canvas):
        #r is no longer radius, but width from closest edge of screen
        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        ledge,redge = (0,float(canvas.cget("width"))) #ledge = left_edge, redge = right_edge

        if (distance((sx,sy),(ledge,sy)) < distance((sx,sy),(redge,sy))):
            #closer to left edge
            uleft = (0,0)
            bright = (r,canvas.cget("height"))
        else:
            #closer to right edge
            uleft = (float(canvas.cget("width"))-r, 0)
            bright = (canvas.cget("width"), canvas.cget("height"))
            
        #self._circle_handle = canvas.create_rectangle(uleft, bright, fill='#ddd', outline='white')
        self._circle_handle = canvas.create_rectangle(uleft, bright, fill='yellow', outline='white', tags = "key_tag")
        self.set_corners(uleft, bright)
        super(Key3,self).draw(canvas)

    def update(self, canvas, pos):
        ''' 
        Checks if the selector is in the key.
        Takes the difference of the last two screen update times to calculate
        the time since the key was last updated, if selected adds that time to the
        selection_score counter, if not selected subtracts half that time.
        Once selection_score reaches a set threshold the key is marked as selected
        '''
        x,y = pos

        super(Key3, self).update(canvas, (x,y))
        if len(timelog) >= 2:
            if self.contains(pos):
                self.selection_score += timelog[-1][1]-timelog[-2][1]
            else:
                self.selection_score -= (timelog[-1][1]-timelog[-2][1])/2
                self.selection_score = max(0,self.selection_score)

        if self.selection_score > settings.selection_delay:
            self.selection_score = 0
            self.selected = True
        else:
            self.selected = False
        r = int((self.selection_score*255) / settings.selection_delay)
        canvas.itemconfigure(self.handle, fill=make_color(r,0,0))
## below is a keyboard based on Key 3 that will divide the screen into 3 parts 
class Three_Key(Text):
    '''Dynamic on-screen key used for3 key layout (kb_version 5)'''
    #Note: Currently inflexible key, specifically designed for 3 key layout on horizontal edges
    def __init__(self, x,y, font, size=5):
        # inherit from Text 
        super(Three_Key, self).__init__(x,y, font, size)
        self.selected = False
        self.selection_score = 0
        self._centroid_x, self._centroid_y = (0,0) # x,y selection centroid
        # with 3 selection regions , one letter on the upper corner , one letter on the bottom left and one on the left 
        self._x0, self._y0 = (0,0) # upper right corner
        self._x1, self._y1 = (0,0) # bottom right corner

    def delete(self, canvas):
        super(Three_Key, self).delete(canvas)
        canvas.delete(self._circle_handle)

    def set_corners(self, uleft, bright):
        self._x0, self._y0 = uleft
        self._x1, self._y1 = bright

    def set_centroid(self, centroid):
        self._centroid_x, self._centroid_y = centroid

    def contains(self, pos):
        '''Determines if pos lies within the key'''
        x,y = pos

        if (x > self._x0 and x < self._x1 and y > self._y0 and y < self._y1):
            return True
        return False

    def draw(self, canvas):
        #modify this to make 3 selection regions 
        #r is no longer radius, but width from closest edge of screen
        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        # y coordinates of upper edge and bottom edge
        width = float(canvas.cget("width"))
        height = float(canvas.cget("height"))
        print ('width is ', width)
        print ('height is ', height)
        uedge,bedge = (0,height) 
        redge = width
        ledge = 0
        middle = width/2
        if (distance((sx,sy),(sx,uedge)) < distance((sx,sy),(sx,bedge))):
            #closer to upper edge
            uleft = (2.0*width//3,0)
            bright = (width,2*height/5)
        elif(distance((sx,sy),(sx,uedge)) > distance((sx,sy),(sx,bedge))):
            #closer to bottom edge
            uleft = (2*width/3, 3*height/5)
            bright = (width, height)
        elif(distance((sx,sy),(ledge,sy)) < distance((sx,sy),(redge,sy))):
            uleft =(0,0)
            bright =(1*width/3,height)
        #if (sx > 960 and sy < 540):
        #    uleft = (960,0)
        #    bright = (1920,540)
        #elif (sx>960 and sy>540):
        #    uleft = (960,540)
        #    bright = (1920,1080)
            
        #self._circle_handle = canvas.create_rectangle(uleft, bright, fill='#ddd', outline='white')
        self._circle_handle = canvas.create_rectangle(uleft, bright, fill='green', outline='white', tags = "key_tag")
        canvas.tag_lower(self._circle_handle)
        self.set_corners(uleft, bright)
        super(Three_Key,self).draw(canvas)

    def update(self, canvas, pos):
        ''' 
        Checks if the selector is in the key.
        Takes the difference of the last two screen update times to calculate
        the time since the key was last updated, if selected adds that time to the
        selection_score counter, if not selected subtracts half that time.
        Once selection_score reaches a set threshold the key is marked as selected
        '''
        x,y = pos

        super(Three_Key, self).update(canvas, (x,y))
        if len(timelog) >= 2:
            if self.contains(pos):
                self.selection_score += timelog[-1][1]-timelog[-2][1]
            else:
                self.selection_score -= (timelog[-1][1]-timelog[-2][1])/2
                self.selection_score = max(0,self.selection_score)

        if self.selection_score > settings.selection_delay:
            self.selection_score = 0
            self.selected = True
        else:
            self.selected = False
        r = int((self.selection_score*255) / settings.selection_delay)
        canvas.itemconfigure(self.handle, fill=make_color(r,0,0))
class SingleKeyTimeSelectionKey(Text):
    ''' Dynamic on-screen key. Designed for a single key layout. Uses time-based selection.
    Selection region decoupled from character display'''
    def __init__(self, x,y, font, size=5):
        super(SingleKeyTimeSelectionKey, self).__init__(x,y, font, size)
        self.selected = False
        self.next_page = False
        self.selection_score = 0
        self.next_page_score = 0
        self._centroid_x, self._centroid_y = (0,0) # x,y selection centroid

    def set_centroid(self, centroid):
        self._centroid_x, self._centroid_y = centroid

    def draw(self, canvas):
        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        self._circle_handle = canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill="yellow", outline="", tags = "key_tag")
        super(SingleKeyTimeSelectionKey,self).draw(canvas)

    def delete(self, canvas):
        super(SingleKeyTimeSelectionKey, self).delete(canvas)
        canvas.delete(self._circle_handle)

    def update(self, canvas, pos):
        ''' 
        Checks if the selector is in the field of the key selection radius.
        Takes the difference of the last two screen update times to calculate
        the time since the key was last updated, if selected adds that time to the
        selection_score counter, if not selected subtracts half that time.
        Once selection_score reaches a set threshold the key is marked as selected.
        Looking outside of the key selects the key, whereas looking in the key advances to
        the next page.
        '''
        x,y = pos

        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        #canvas.coords(self._circle_handle, sx-r, sy-r, sx+r, sy+r)

        super(SingleKeyTimeSelectionKey, self).update(canvas, (x,y))
        if len(timelog) >= 2:
            if distance((x,y), (self._centroid_x, self._centroid_y)) < settings.letter_selection_radius:
                # If the gaze is within the selection radius, increment next page value
                self.next_page_score += timelog[-1][1]-timelog[-2][1]
                self.selection_score -= timelog[-1][1]-timelog[-2][1]
                self.selection_score = max(0,self.selection_score)
            else:
                self.selection_score += timelog[-1][1]-timelog[-2][1]
                self.next_page_score -= timelog[-1][1]-timelog[-2][1]
                self.next_page_score = max(0,self.selection_score)

        if self.selection_score > settings.selection_delay:
            self.selection_score = 0
            self.next_page_score = 0
            self.selected = True
            self.next_page = False
        elif self.next_page_score > settings.selection_delay:
            self.selection_score = 0
            self.next_page_score = 0
            self.selected = False
            self.next_page = True
        else:
            self.selected = False
            self.next_page = False
        r = int((self.selection_score*255) / settings.selection_delay)
        canvas.itemconfigure(self.handle, fill=make_color(r,0,0))

class DataCollectionKey(Text):
    '''Key used in calibration process or for data collection'''
    def __init__(self, x,y, font, size=5):
        super(DataCollectionKey, self).__init__(x,y, font, size)
        self._text = settings.cal_letter
        self.write(self._text)

    def draw(self, canvas):
        super(DataCollectionKey,self).draw(canvas)

class SVMScoringKey(Text):
    '''Key useing SVM for calibration'''
    def __init__(self, x,y, font, size=5):
        super(SVMScoringKey, self).__init__(x,y, font, size)
        self.selected = False
        self.selection_score = 0
        self._centroid_x, self._centroid_y = (0,0) # x,y selection centroid
        self._x0, self._y0 = (0,0) # upper left corner
        self._x1, self._y1 = (0,0) # bottom right corner

    def delete(self, canvas):
        super(SVMScoringKey, self).delete(canvas)
        canvas.delete(self._circle_handle)

    def draw(self, canvas):
        super(SVMScoringKey,self).draw(canvas)
        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        self._circle_handle = canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill=None, outline="", tags = "key_tag")

    def set_centroid(self, centroid):
        pass

    def update(self, canvas, pos):
        x,y = pos
        super(SVMScoringKey, self).update(canvas, (x,y))
        if self.selection_score > settings.selection_delay:
            self.selection_score = 0
            self.selected = True
        else:
            self.selected = False
        r = int((self.selection_score*255) / settings.selection_delay)
        canvas.itemconfigure(self.handle, fill=make_color(r,0,0))

    def increment_score(self):
        if len(timelog) >= 2:
            self.selection_score += timelog[-1][1]-timelog[-2][1]

    def decrement_score(self):
        if len(timelog) >= 2:
            self.selection_score -= (timelog[-1][1]-timelog[-2][1])/2
            self.selection_score = max(0,self.selection_score)

class AudioKey(Text):
    '''When displayed on screen, key speaks its text value. No on-screen presence, only audio feedback'''
    def __init__(self, x,y, font, size=5):
        super(AudioKey, self).__init__(x,y, font, size)
        self.selected = False
        self.next_page = False
        self.next_page_score = 0
        self.time_elapsed = 0
        self._centroid_x, self._centroid_y = (0,0) # x,y selection centroid
        self.last_pos = None
        self.phase1 = False
        self.phase2 = False
        self.preselect = False
        self.pre_next_page = False
        self.spoken = False
        self.time_off_screen = 0

        self.point_history = []

        if (settings.selection_delay > 1):
            self.point_history_length = 7
        else:
            self.point_history_length = 4

    def set_centroid(self, centroid):
        self._centroid_x, self._centroid_y = centroid

    def draw(self, canvas):
        r = settings.letter_selection_radius
        sx,sy = (self._centroid_x,self._centroid_y)
        self._circle_handle = canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill='', outline="", tags = "key_tag")
        super(AudioKey,self).draw(canvas)

    def delete(self, canvas):
        super(AudioKey, self).delete(canvas)
        canvas.delete(self._circle_handle)

    def reset_vars(self):
        self.phase1 = False
        self.phase2 = False
        self.preselect = False
        self.spoken = False
        self.time_off_screen = 0
        self.time_elapsed = 0
        self.selected = False
        self.next_page = False

    def update(self, canvas, pos):
        ''' 
        Cycles through letters at rate specified by settings.selection_delay. Checks if on-screen vision has been recorded.
        '''
        x,y = pos

        if(len(self.point_history) < self.point_history_length):
            self.point_history = [pos] + self.point_history
        else:
            self.point_history = [pos] + self.point_history[0:len(self.point_history)-1]
        
        super(AudioKey, self).update(canvas, (x,y))
        if len(timelog) >= 2 and pos != self.last_pos:
            if (settings.only_open == True):
                if (pos != self.last_pos):
                    # only track time when eyes are open or on screen
                    self.time_elapsed += timelog[-1][1]-timelog[-2][1]
            else:
                # always track time
                self.time_elapsed += timelog[-1][1]-timelog[-2][1]
    
        # Evaluation phase. Determine if there was a blink.
        if self.time_elapsed > settings.pre_audio_buffer + settings.selection_delay:
            # if preselect is false (no blink), prepare to advance page
            if (self.preselect == False):
                self.next_page = True
                self.selected = False
            else:
                self.selected = True

            # reset variables for next key
            self.phase1 = False
            self.phase2 = False
            self.preselect = False
            self.time_elapsed = 0

        # Data collection phase. Speak option and monitor for blink.
        elif (self.time_elapsed > settings.pre_audio_buffer):
            # only speak once
            if (self.spoken == False):
                thread.start_new_thread(speak_character, (self.text,))
                self.spoken = True

            # blink select detection
            if (self.phase1 == False and len(self.point_history) == self.point_history_length):
                self.phase1 = True
                for val in self.point_history:
                    if val != pos:
                        self.phase1 = False
                        break
            # No motion phase observed
            elif (self.phase1 == True and self.last_pos != pos):
                # Motion observed after phase 1 of no motion
                self.phase2 = True
                self.preselect = True

        # Null phase. Resets variables for blink detection and evaluation.
        else:
            self.spoken = False
            self.selected = False
            self.next_page = False

        self.last_pos = pos

class OnscreenKeyboard(Drawable):
    ''' Consists of a number of evenly spaced Text objects '''
    def __init__(self, font, shape, predictionary, screen_w, screen_h):
        self.logger = logging.getLogger('kb')
        row,col = shape
        if not isinstance(predictionary, Predictionary):
            self.logger.critical(str(type(predictionary)) + ' does not inherit from ' + str(Predictionary))
            self.logger.critical('Initialization of Keyboard failed, exiting...')
            quit()
        self.set_rows_and_cols(row, col)
        self.keys = []

        unattached_msg = 'called but no callback function attached'
        self._write = lambda x: self.logger.warning('kb._write '+unattached_msg+', attempted to write '+str(x))
        self._speak = lambda x: self.logger.warning('kb._speak '+unattached_msg+', attempted to speak '+str(x))
        self._clear = lambda: self.logger.warning('kb._clear '+unattached_msg)
        self._delete = lambda: self.logger.warning('kb._delete '+unattached_msg)

        self._predict = predictionary
        self._last_selection = None
        self._index_history = []
        self._at_end = False
        self._page = 0
        self.font = font
        self.standard_operation = True
        self.calibrating = False
        self.collecting_data = False
        self.cal_t0 = 0
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.move_keys = False

        #SVM variables
        self.svm_window = []
        self.svm_model = None

        self.initialize_keys()

    def initialize_keys(self):
        i = 0
        for x in xrange(0, self.row*self.col):
            if settings.kb_version == 2:
                key = Key2(0,0, self.font)
            elif settings.kb_version == 3:
                key = Key3(0,0,self.font)
            elif settings.kb_version == 4:
                key = SVMScoringKey(0,0,self.font)
            elif settings.kb_version == 5:
                key = SingleKeyTimeSelectionKey(0,0, self.font)
            elif settings.kb_version == 6:
                key = Three_Key(0,0,self.font)
            elif settings.kb_version == 7:
                key = AudioKey(0,0,self.font)
            else:
                key = Key(0,0, self.font)
            try:
                key.write(self._get_arrangement()[i])
            except IndexError as e:
                self.logger.warning('Not enough choices to populate keyboard')
            i += 1
            self.keys.append(key)

    def reset(self):
        self._change_page()

    def set_centroids(self, centroids):
        try:
            for i in range(len(self.keys)):
                self.keys[i].set_centroid(centroids[i])
        except IndexError:
            self.logger.warning('Number of centroids passed does not match number of keys')
    def set_rows_and_cols(self, row,col):
        self.row,self.col = row,col

    def set_dimensions(self, x,y,w,h):
        self.x,self.y,self.w,self.h = (x,y,w,h)

    def _get_arrangement(self):
        ''' Returns the current on-screen layout of the keyboard '''
        if settings.calibrate == True: 
            layout = [
                ['a','','',''], # 0
                ['','b','',''], # 1
                ['','','c',''], # 2
                ['','','','d']  # 3
            ]
            self._page = self._page % len(layout)
            return layout[self._page]
        elif self.calibrating == True:
            layout = [
            ['a', '', '', '', ''], # 0
            ['', 'b', '', '', ''], # 1
            ['', '', 'c', '', ''], # 2
            ['', '', '', 'd', ''], # 3
            ['', '', '', '', 'e'], # 4
            ]
        elif settings.kb_version > 1:
            if self.col*self.row == 8:
                layout = [
                    ['A','H','N','U','#','.','{}','<'], # 0
                    ['a','b','c','d','e','f','g', '<'], # 1
                    ['h','i','j','k','l','m','#', '<'], # 2
                    ['n','o','p','q','r','s','t', '<'], # 3
                    ['u','v','w','x','y','z','#', '<']  # 4
                ]
            elif self.col*self.row == 4:
                layout = [
                    ['ai','jr','sz','#'], # 0
                    ['ac','df','gi','<'], # 1
                    ['a', 'b', 'c', '<'], # 2
                    ['d', 'e', 'f', '<'], # 3
                    ['g', 'h', 'i', '<'], # 4
                    ['jl','mo','pr','<'], # 5
                    ['j', 'k', 'l', '<'], # 6
                    ['m', 'n', 'o', '<'], # 7
                    ['p', 'q', 'r', '<'], # 8
                    ['su','vx','yz','<'], # 9
                    ['s', 't', 'u', '<'], # 10
                    ['v', 'w', 'x', '<'], # 11
                    ['y', 'z', '',  '<'], # 12
                    ['{}','.', '',  '<']  # 13
                ]
            elif self.col*self.row == 2:
                if (settings.kb_uniform_selection == 1):
                    '''Uniform tree depth layout (repeated characters in tree branches)'''
                    layout = [
                        ['a:z','#'], # 0
                        ['a:m','n:z'], #1
                        ['a:g','h:m'], #2
                        ['a:d','e:g'], #3
                        ['a:b','c:d'], #4
                        ['a','b'], #5
                        ['c','d'], #6
                        ['e:f','f:g'], #7
                        ['e','f'], #8
                        ['f','g'], #9
                        ['h:j','k:m'], #10
                        ['h:i','i:j'], #11
                        ['h','i'], #12
                        ['i','j'], #13
                        ['k:l','l:m'], #14
                        ['k','l'], #15
                        ['l','m'], #16
                        ['n:t','u:z'], #17
                        ['n:q','r:t'], #18
                        ['n:o','p:q'], #19
                        ['n','o'], #20
                        ['p','q'], #21
                        ['r:s','s:t'], #22
                        ['r','s'], #23
                        ['s','t'], #24
                        ['u:w','x:z'], #25
                        ['u:v','v:w'], #26
                        ['u','v'], #27
                        ['v','w'], #28
                        ['x:y','y:z'], #29
                        ['x','y'], #30
                        ['y','z'], #31
                        ['{}:<','<:.'], #32
                        ['{}', '<'], #33
                        ['<','.'] #34
                    ]

            elif (self.col*self.row == 1 or settings.kb_version == 7):
                layout = [
                    ['a:m'], #0
                    ['n:z'], #1
                    ['<'], #2
                    ['a'], #3
                    ['b'], #4
                    ['c'], #5
                    ['d'], #6
                    ['e'], #7
                    ['f'], #8
                    ['g'], #9
                    ['h'], #10
                    ['i'], #11
                    ['j'], #12
                    ['k'], #13
                    ['l'], #14
                    ['m'], #15
                    ['n'], #16
                    ['o'], #17
                    ['p'], #18
                    ['q'], #19
                    ['r'], #20
                    ['s'], #21
                    ['t'], #22
                    ['u'], #23
                    ['v'], #24
                    ['w'], #25
                    ['x'], #26
                    ['y'], #27
                    ['z'], #28
                    ['{}'], #29
                ]
            elif (self.col*self.row == 3):
                layout =[ ['a:z','#','<'], # 0
                          ['a:m','n:z','<'], #1
                          ['a:g','h:m','<'], #2
                          ['a:d','e:g','<'], #3
                          ['a:b','c:d','<'], #4
                          ['a','b','<'], #5
                          ['c','d','<'], #6
                          ['e:f','f:g','<'], #7
                          ['e','f','<'], #8
                          ['f','g','<'], #9
                          ['h:j','k:m','<'], #10
                          ['h:i','i:j','<'], #11
                          ['h','i','<'], #12
                          ['i','j','<'], #13
                          ['k:l','l:m','<'], #14
                          ['k','l','<'], #15
                          ['l','m','<'], #16
                          ['n:t','u:z','<'], #17
                          ['n:q','r:t','<'], #18
                          ['n:o','p:q','<'], #19
                          ['n','o','<'], #20
                          ['p','q','<'], #21
                          ['r:s','s:t','<'], #22
                          ['r','s','<'], #23
                          ['s','t','<'], #24
                          ['u:w','x:z','<'], #25
                          ['u:v','v:w','<'], #26
                          ['u','v','<'], #27
                          ['v','w','<'], #28
                          ['x:y','y:z','<'], #29
                          ['x','y','<'], #30
                          ['y','z','<'], #31
                          ['{}:<','<:.','#'], #32
                          ['{}', '<','#'], #33
                          ['<','.','#'] #34
                ]    


            self._page = self._page % len(layout)
            return layout[self._page]
        else:
            return self._predict._get_arrangement()

    def draw(self, canvas):
        ''' Draws keyboard keys evenly spaced on tk canvas '''
        if (settings.kb_version == 2 or settings.kb_version == 5):
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
                key.set_centroid((key.x,key.y))
                key.draw(canvas)
                canvas.coords(key.handle, x,y)
        elif (settings.kb_version == 3 or settings.kb_version == 4):
            if (self.row*self.col > 2):
                raise Exception('More than two keys not yet supported for max spacing layout')
            # loop fills keys on left edge then right edge
            i = 0
            offset = 225 # offset into screen from edge
            for key in self.keys:
                x,y = (i*self.w + offset - 2*offset*i, i*self.h + offset//3 - 2*offset*i//3)
                key.x,key.y = (x,y)
                key.set_centroid((key.x,key.y))
                key.draw(canvas)
                canvas.coords(key.handle, x,y)
                i+=1
        elif (settings.kb_version == 6):
            i = 0
            offset = 225 # offset into screen from edge
            for key in self.keys:
                #print('i is ',i)
                #x,y = (i*self.w + offset - 2*offset*i, i*self.h + offset//3 - 2*offset*i//3)
                if (i == 0):
                    x,y =(self.screen_w-255,150)
                elif (i == 1):
                    x,y =(self.screen_w-255,600) 
                elif(i==2):
                    x,y =(self.screen_w/6,self.screen_h/2)
                key.x,key.y = (x,y)
                key.set_centroid((key.x,key.y))
                key.draw(canvas)
                canvas.coords(key.handle, x,y)
                i+=1        
        elif (settings.kb_version == 7):
            key = self.keys[0]
            #x,y = (self.w//2, self.h//2)
            x,y = (-200, -200)
            key.x,key.y = (x,y)
            key.set_centroid((key.x,key.y))
            key.draw(canvas)
            canvas.coords(key.handle,x,y)


    def update(self, canvas, pos):
        ''' Checks if a key is selected and if events occur '''
        if (self.standard_operation == True):
            x,y = pos
            if (settings.kb_version == 4):
                if self.svm_model != None:
                    selected_key = self.svm_prediction(canvas, pos)
                    if (selected_key > -1): # -1 indicates no prediction (insufficent data)
                        self.keys[int(selected_key) - 1].increment_score()
            for key in self.keys: 
                key.update(canvas, (x,y))
                if settings.calibrate == False:
                    key_next_page = False # Flag only relevant for kb_version 5
                    if (settings.kb_version == 5 or settings.kb_version == 7):
                        if (key.next_page == True):
                            key_next_page = True
                    if key.selected == True or key_next_page == True:
                        self._last_selection = key.text
                        index = self.keys.index(key)
                        if len(self._index_history) > 1:
                            if self._index_history[0] is not index:
                                self._index_history[1] = self._index_history[0]
                                self._index_history[0] = index
                        else:
                            self._index_history.append(index)
                            self._index_history.append(index)
                        if settings.kb_version > 1:
                            self.process(key)
                    if key.text == self._last_selection and y < key.y:
                        canvas.coords(key.handle, x,y)
                    else:
                        canvas.coords(key.handle, key.x,key.y)
        elif (self.collecting_data == True):
            self.collect_data(canvas)
        elif (self.calibrating == True):
            self.calibrate(canvas)

    def delete(self, canvas):
        for key in self.keys: key.delete(canvas)
        self.keys = []

    def larger(self):
        size = self.font['size']
        self.font.configure(size=int(size*1.1))

    def smaller(self):
        size = self.font['size']
        self.font.configure(size=int(size*0.9))

    def process(self, key):
        '''
        Outputs last selected char/key
        v1:Processes the last key pressed through the predictionary 
        v2:Flips to another page
        Clears last selection, console if '.' selected
        '''
        if self._last_selection is not '':
            next_page = 0
            if settings.kb_version > 1:
                if self.col*self.row == 8:
                    selection_map = {
                        'A':1,
                        'H':2,
                        'N':3,
                        'U':4
                    }
                elif self.col*self.row == 4:
                    selection_map = {
                        'ai':1,
                        'ac':2,
                        'df':3,
                        'gi':4,
                        'jr':5,
                        'jl':6,
                        'mo':7,
                        'pr':8,
                        'sz':9,
                        'su':10,
                        'vx':11,
                        'yz':12,
                        '#' :13
                    }
                elif self.col*self.row == 2 or self.col*self.row == 3:
                    if (settings.kb_uniform_selection == 1):
                        selection_map = {
                            'a:z':1,
                            'a:m':2,
                            'a:g':3,
                            'a:d':4,
                            'a:b':5,
                            'c:d':6,
                            'e:g':7,
                            'e:f':8,
                            'f:g':9,
                            'h:m':10,
                            'h:j':11,
                            'h:i':12,
                            'i:j':13,
                            'k:m':14,
                            'k:l':15,
                            'l:m':16,
                            'n:z':17,
                            'n:t':18,
                            'n:q':19,
                            'n:o':20,
                            'p:q':21,
                            'r:t':22,
                            'r:s':23,
                            's:t':24,
                            'u:z':25,
                            'u:w':26,
                            'u:v':27,
                            'v:w':28,
                            'x:z':29,
                            'x:y':30,
                            'y:z':31,
                            '#':32,
                            '{}:<':33,
                            '<:.':34
                        }
                elif self.col*self.row == 1:
                    if (settings.kb_version == 5 or settings.kb_version == 7):
                        if (key.selected == True):
                            selection_map = {
                            'a:m':3,
                            'n:z':16
                            }
                        elif (key.next_page == True):
                            #TODO: fix bug with '.' (currently always gets selected)
                            selection_map = {
                                'a:m':1,
                                'n:z':2,
                                '<': 0,
                                'a':4,
                                'b':5,
                                'c':6,
                                'd':7,
                                'e':8,
                                'f':9,
                                'g':10,
                                'h':11,
                                'i':12,
                                'j':13,
                                'k':14,
                                'l':15,
                                'm':0,
                                'n':17,
                                'o':18,
                                'p':19,
                                'q':20,
                                'r':21,
                                's':22,
                                't':23,
                                'u':24,
                                'v':25,
                                'w':26,
                                'x':27,
                                'y':28,
                                'z':29,
                                '{}':0,
                            }
                    else:
                        selection_map = {
                            'a':1,
                            'b':2,
                            'c':3,
                            'd':4,
                            'e':5,
                            'f':6,
                            'g':7,
                            'h':8,
                            'i':9,
                            'j':10,
                            'k':11,
                            'l':12,
                            'm':13,
                            'n':14,
                            'o':15,
                            'p':16,
                            'q':17,
                            'r':18,
                            's':19,
                            't':20,
                            'u':21,
                            'v':22,
                            'w':23,
                            'x':24,
                            'y':25,
                            'z':26,
                            '{}':27,
                            '<':28,
                            '.':0
                        }
                def add_space(): 
                    self._last_selection = ' '
                    if (settings.kb_version != 7):
                        self._speak('space')
                    self.process(key)
                def undo():
                    if self._page == 0 or self._page == 13 or self._page == 33 or self._page == 34 or self._page == 27 or self._page == 2:
                        self._delete()
                    else:
                        self.reset()
                function_map = {'<':undo,'{}':add_space}
                try:
                    next_page = selection_map[self._last_selection]
                except KeyError:
                    try:
                        function_map[self._last_selection]()
                        #settings.selection_delay += 5
                    except KeyError:
                        self._write(self._last_selection)
                        if (settings.kb_version != 7):
                            self._speak(self._last_selection)
                        #settings.selection_delay = max(1,settings.selection_delay-1)
            else:
                self._write(self._last_selection)
                self._predict.process(self._last_selection) # TODO more flexible letter provider interface
            self._change_page(next_page)
            if self._last_selection == '.':
                self._clear()
            self._last_selection = ''

    def _change_page(self, page=0):
        ''' 
        Selects from one of several pages in current keyboard layouts
        e.g. maybe 'a b c d' or 'e f g h' for 4-key keyboard
        '''
        self._page = page
        self._at_end = False
        del self._index_history[:]
        i = self._page*self.col*self.row
        choices = self._get_arrangement()
        i %= len(choices)
        for key in self.keys:
            key.selected = False
            key.clear()
            key.write(choices[i])
            i = (i+1) % len(choices)
            '''if (settings.kb_version == 7):
                thread.start_new_thread (self.speak_character, (choices[i],))'''

    def gen_svm_model(self):
        df = pd.read_csv('../data/eye_tests/combined_calibration_log.csv',sep=',')
        X = df.iloc[:,[0,1]].values
        #standardize feature vectors 
        stdsc = StandardScaler()
        X = stdsc.fit_transform(X)
        y=df.iloc[:,3].values
        C = 1.0  # SVM regularization parameter
        if (settings.SVM_model_type == 1):
            self.svm_model = svm.SVC(kernel='linear', C=C).fit(X, y)
        elif (settings.SVM_model_type == 2):
            self.svm_model = svm.SVC(kernel='rbf', gamma=0.7, C=C).fit(X, y)
        elif (settings.SVM_model_type == 3):
            self.svm_model = svm.SVC(kernel='poly', degree=3, C=C).fit(X, y)
        elif (settings.SVM_model_type == 4):
            self.svm_model = svm.LinearSVC(C=C).fit(X, y)
        else:
            raise Exception("Invalid SVM model selection")

    def svm_prediction(self, canvas, pos):
        size = settings.SVM_window_size
        n_pos = np.array(pos)
        #standardize it before make predictions
        stdsc = StandardScaler()
        n_pos = stdsc.fit_transform(pos)
        #depend on how many points we want to look in order to make prediction
        if len(self.svm_window) == size:
            b = Counter(self.svm_window)
            self.svm_window = []   #reinitialize window

            return b.most_common(1)[0][0]    #output the most common class labels

        else:  
            n_pos = np.array(n_pos)
            #standardize it before make predictions
            stdsc = StandardScaler()
            n_pos = stdsc.fit_transform(n_pos)
            prediction = self.svm_model.predict(n_pos)
      
            self.svm_window.append(str(prediction[0]))
            return -1

    def configure_calibration(self):
        self.standard_operation = False
        self.collecting_data = False
        self.calibrating = True
        self.cal_t0 = time.clock()

    def configure_data_collection(self, canvas):
        self.standard_operation = False
        self.collecting_data = True
        self.calibrating = False
        #self._clear_keyboard(canvas)
        self.delete(canvas)
        # create the first data collection key and place it in the upper left corner of the screen
        key = DataCollectionKey(0,0, self.font)
        x,y = (settings.dc_dx,settings.dc_dy)
        key.x,key.y = (x,y)
        key.draw(canvas)
        canvas.coords(key.handle, x,y)
        self.keys.append(key)
        self.cal_t0 = time.clock()

    def configure_standard_operation(self, canvas):
        self.standard_operation = True
        self.calibrating = False
        self.collecting_data = False
        self.delete(canvas)
        self.initialize_keys()
        self.draw(canvas)

    def collect_data(self,canvas):
        dt = settings.calibration_hold_time
        current_time = time.clock()
        dx,dy = (settings.dc_dx, settings.dc_dy)
        key = self.keys[0]
        if (current_time > self.cal_t0 + 5*dt + 2):
            #after 5*dt seconds, restore keyboard to original format
            # Note: 2 second buffer is used to ensure c is done compiling calibration logs
            self.configure_standard_operation(canvas)
        elif (current_time > self.cal_t0 + 4*dt):
            # after 4*dt seconds, move key to center
            canvas.coords(key.handle, (self.screen_w//2, self.screen_h//2))
        elif (current_time > self.cal_t0 + 3*dt):
            # after 3*dt seconds, move key to bottom left corner
            canvas.coords(key.handle, (dx, self.screen_h - dy))
        elif (current_time > self.cal_t0 + 2*dt):
            # after 2*dt seconds, move key to bottom right corner
            canvas.coords(key.handle, (self.screen_w - dx, self.screen_h - dy))
        elif (current_time > self.cal_t0 + dt):
            # after dt seconds, move key to upper right corner
            canvas.coords(key.handle, (self.screen_w - dx,dy))

    def calibrate(self, canvas):
        dt = settings.calibration_hold_time
        current_time = time.clock()
        for key in self.keys:
            key.clear()
            key.update(canvas,(0,0))        
        if (current_time > self.cal_t0 + self.row*self.col*dt):
            self.configure_standard_operation(canvas)
            if (settings.kb_version == 4):
                self.gen_svm_model()
        elif (current_time > self.cal_t0 + 4*dt):
            self.keys[4].write(settings.cal_letter)
            self.keys[4].update(canvas,(0,0))
        elif (current_time > self.cal_t0 + 3*dt):
            self.keys[3].write(settings.cal_letter)
            self.keys[3].update(canvas,(0,0))
        elif (current_time > self.cal_t0 + 2*dt):
            self.keys[2].write(settings.cal_letter)
            self.keys[2].update(canvas,(0,0))
        elif (current_time > self.cal_t0 + dt):
            self.keys[1].write(settings.cal_letter)
            self.keys[1].update(canvas,(0,0))
        elif (current_time > self.cal_t0):
            self.keys[0].write(settings.cal_letter)
            self.keys[0].update(canvas,(0,0))

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

    def attach_delete_callback(self, delete_function):
        '''
        Passed function is invoked when an undo command is chosen
        Undo function takes no arguments
        '''
        self._delete = delete_function

    def next_page(self):
        self.logger.debug('Turning the page forward...')
        self._change_page(self._page+1)

    def prev_page(self):
        self.logger.debug('Turning back the page...')
        self._change_page(self._page-1)

if __name__ == '__main__':
    pass