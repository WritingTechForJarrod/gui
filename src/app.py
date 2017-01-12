'''
Writing Tech for Jarrod
On-screen keyboard and gui
max@embeddedprofessional.com

Entry point for gui module of wtfj
'''
# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Dynamic import if python 2 or 3
import sys
try:
    assert sys.version_info[0] == 3
    from tkinter import *
    import tkinter.font as font
except AssertionError as e:
    from Tkinter import *
    import tkFont as font
from threading import Thread, Lock
import time
import types
import logging
import pyttsx
from os import remove
from wtfj import *

class Application(Frame):
    def __init__(self, master=None, screen_size=(1080, 720)):
        # Create lists of drawable objects in app
        self.drawables = []
        # Application housekeeping
        Frame.__init__(self, master)
        self.is_alive = True
        self.screen_w,self.screen_h = screen_size
        self.last_mouse = (0,0)
        self.last_eye = (0,0)
        self.filter_type = MovingAverage(settings.filter_window_size)
        self.mutex = Lock()
        self._createWidgets()
        self.last_update = time.clock()
        self.last_dt = 0

    def _delete_stuff(self):
        self.canvas.delete(ALL)

    @self_timing
    def _draw_periodic(self):
        # Select mouse or eye tracker as input stream, write to log
        input_device = (self.last_mouse,self.last_eye)[settings.input_device]
        if settings.keep_coordinates_log == 1:
                coordinates_log.write(str(input_device[0]) + "," + str(input_device[1]) + "\n")
        
        # Read eye tracker stream from file if needed
        if input_device is self.last_eye:
            self._read_eye_track('../data/eye_tests/eyeStream.txt')

        # Draw all objects
        self.mutex.acquire()
        for drawable in self.drawables:
            drawable.update(self.canvas, input_device)
        self.mutex.release()

        # Update speech engine
        engine.iterate()

        # If in calibrate mode update time and change keyboard
        # TODO put this mess somewhere else
        global t0
        global cal_stage
        if settings.calibrate == True:
            t_h = settings.calibration_hold_time
            t = [t_h,2*t_h,3*t_h,4*t_h]
            if t0 > 0:
                dt = time.clock() - t0
                if dt > t[cal_stage]:
                    kb.next_page()
                    cal_stage += 1
                    if cal_stage >= len(t):
                        cal_stage = 0
                        t0 = 0
                        settings.calibrate = False
                        kb.reset()
                        l = cluster.Test('../data/eye_tests/combined_calibration_log.txt',False)
                        for i in range(len(l)):
                            l[i] = [int(x/1.5) for x  in l[i]]
                        mainlog.debug(l)
                        kb.set_centroids(l)

        '''if settings.collect_data == True:
            t_h = settings.calibration_hold_time
            t = [t_h,2*t_h,3*t_h,4*t_h,5*t_h]
            if t0 > 0:
                dt = time.clock() - t0
                if dt > t[cal_stage]:
                    kb.next_page()
                    cal_stage += 1
                    if cal_stage >= len(t):
                        cal_stage = 0
                        t0 = 0
                        settings.calibrate = False
                        kb.reset()
                        l = cluster.Test('../data/eye_tests/combined_calibration_log.txt',False)
                        for i in range(len(l)):
                            l[i] = [int(x/1.5) for x  in l[i]]
                        mainlog.debug(l)
                        kb.set_centroids(l)'''

        # Find refresh rate
        if len(timelog) > 11:
            last_10 = timelog[-11:-1]
            last_9_diff = [last_10[i+1][1]-last_10[i][1] for i in range(0,9)]
            app.refresh.clear()
            app.refresh.write(str(int(9/sum(last_9_diff))))
            
        # Call this loop again after some milliseconds
        self.canvas.after(50, self._draw_periodic)

    def quit(self):
        logging.getLogger('app').debug('Exiting application...')
        self.is_alive = False
        Frame.quit(self)
        #for line in timelog:
        #    logging.getLogger('timing').debug(line)

    def _createWidgets(self):
        ''' Create the base canvas, menu/selection elements, mouse/key functions '''
        self.canvas = Canvas(self.master, width=self.screen_w, height=self.screen_h)
        w,h = (self.screen_w, self.screen_h)
        
        # Upper text console and keyboard
        if (settings.kb_version <= 2 or settings.kb_version > 3):
            self.console = Text(0,0, console_font)
        elif (settings.kb_version == 3):
            self.console = Text(self.screen_w/3,self.screen_h/3, console_font)
        self.drawables.append(self.console)
        self.refresh = Text(w,0, console_font, justify='right')
        self.drawables.append(self.refresh)
        kb.set_dimensions(0,h//6,w,h-h//6)
        self.drawables.append(kb)
        
        self.drawables.append(self.console)
        # Marker that follows mouse movement
        self.drawables.append(MouseLight(settings.mouselight_radius))

        # Initial drawing of all Drawables
        for drawable in self.drawables:
            drawable.draw(self.canvas)

        self.canvas.pack()
        self.canvas.itemconfigure(self.console.handle, anchor='nw')
        self.canvas.itemconfigure(self.refresh.handle, anchor='ne')
        self.canvas.bind("<Motion>", on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", on_left_click)
        self.canvas.bind("<ButtonPress-3>", on_right_click)
        self.canvas.bind_all("<Escape>", on_esc)
        self.canvas.bind_all("<space>", on_space)
        self.canvas.bind_all("<Tab>", on_tab)

    def mainloop(self):
        go = Thread(target=self._draw_periodic)
        go.start()
        Frame.mainloop(self)
        go.join()

    def _read_eye_track(self, fileName):
        with open(fileName,'r') as f:
            try:
                contents = f.readline()
                x_y = contents.split(',')
                eye_x = int(float(x_y[0])/1.5)
                eye_y = int(float(x_y[1])/1.5)
                self.filter_type.calculate_average(eye_x, eye_y)
                self.last_eye = (self.filter_type.filtered_x, self.filter_type.filtered_y)
            except ValueError:
                pass

def on_mouse_move(event):
    app.last_mouse = (event.x, event.y)

def on_esc(event):
    app.quit()

def on_space(event):
    global t0
    global cal_stage
    settings.calibrate = True
    with open('go.txt','w') as f:
        rows,cols = settings.kb_shape
        f.write(str(rows*cols) + "," + str(settings.calibration_hold_time)) # Create go.txt flag file
    kb.reset()
    speak('calibrating')
    t0 = time.clock()
    cal_stage = 0

def on_tab(event):
    global t0
    global cal_stage
    settings.collect_data = True

def on_right_click(event):
    mainlog.debug('Right click')
    if settings.dynamic_screen == 1:
        kb.smaller()
    else:
        mainlog.debug()
        app.quit()

def on_left_click(event):
    mainlog.debug('Left click')
    kb.larger()

def speak(phrase):
    engine.say(phrase)
    mainlog.debug('Speaking phrase '+phrase)

if __name__ == '__main__':
    ''' Run the gui interface '''
    # Create root of windowing system, set to fullscreen
    root = Tk()
    root.attributes("-fullscreen", True)
    w,h = (root.winfo_screenwidth(), root.winfo_screenheight()) # TODO fix the resolution issues

    # Create loggers, fonts, keyboard
    logging.basicConfig(level=logging.DEBUG)
    mainlog = logging.getLogger('main')
    console_font = font.Font(family='Helvetica',size=settings.console_font_size, weight='bold')
    kb_font = font.Font(family='Helvetica',size=settings.kb_font_size, weight='bold')
    kb = OnscreenKeyboard(kb_font, settings.kb_shape, Predictionary('../dict/'+settings.dict_filename))
    if (settings.keep_coordinates_log == 1):
        coordinates_log = open(settings.log_name,'w')

    # Start speech enginge
    engine = pyttsx.init()
    engine.startLoop(False)
    engine.setProperty('rate',100)
    mainlog.debug('Speech volume set to '+str(engine.getProperty('volume')))

    # Setup calibration variables
    t0 = 0
    cal_stage = 0

    # Start main app
    app = Application(master=root,screen_size=(w,h))
    
    # Attach callbacks
    def clear_callback():
        speak(app.console.text)
        app.console.clear()

    def delete_callback():
        app.console.text = app.console.text[0:-1]

    kb.attach_write_callback(app.console.write)
    kb.attach_speak_callback(speak)
    kb.attach_clear_callback(clear_callback)
    kb.attach_delete_callback(delete_callback)

    app.master.minsize(500,500)
    app.mainloop()
    app.quit()

    try:
        remove('go.txt')
    except WindowsError:
        # Calibration start file not created, this is fine
        pass
    engine.endLoop()