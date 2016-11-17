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
from wtfj import *
import pyttsx
from multiprocessing import Process, Queue, current_process, Event

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
        self.createWidgets()

    def delete_stuff(self):
        self.canvas.delete(ALL)

    def draw_periodic(self):
        # Select mouse or eye tracker as input stream, write to log
        input_device = (self.last_mouse,self.last_eye)[settings.input_device]
        if settings.keep_coordinates_log == 1:
                coordinates_log.write(str(input_device[0]) + "," + str(input_device[1]) + "\n")
        
        # Draw all objects, read eye tracker stream from file if needed
        self.mutex.acquire()
        for drawable in self.drawables:
            if input_device is self.last_eye:
                self.readEyeTrack('eyeStream.txt')
            drawable.update(self.canvas, input_device)
        self.mutex.release()

        # Call this loop again after 1 millisecond
        engine.iterate()
        self.canvas.after(20, self.draw_periodic)

        # Get any messages from audio engine
        #if q2.empty() == False:
        #    logging.getLogger('process').debug(q2.get())

    def quit(self):
        #estop.set()
        logging.getLogger('app').debug('Exiting application...')
        self.is_alive = False
        Frame.quit(self)

    def createWidgets(self):
        ''' Create the base canvas, menu/selection elements, mouse/key functions '''
        self.canvas = Canvas(self.master, width=self.screen_w, height=self.screen_h)
        w,h = (self.screen_w, self.screen_h)
        
        # Marker that follows mouse movement
        self.drawables.append(MouseLight(100))

        # Function boxes in corner of screen
        if (settings.dynamic_screen == 1):
            self.drawables.append(FunctionBox(w-h//4,      0,     w, h//5, self.quit, fill='red'))
            self.drawables.append(FunctionBox(     0, 4*h//5,  h//4,    h, kb.prev_page, fill='black'))
            self.drawables.append(FunctionBox(w-h//4, 4*h//5,     w,    h, kb.next_page, fill='black'))
            #self.drawables.append(FunctionBox(    0,      0,   h/4,  h/5, select_last_letter, fill='yellow'))

        # Upper text console and keyboard
        self.console = Text(0,0, console_font)
        self.drawables.append(self.console)
        kb.set_dimensions(0,0,w,4*h//8)
        self.drawables.append(kb)

        # Initial drawing of all Drawables
        for drawable in self.drawables:
            drawable.draw(self.canvas)

        self.canvas.pack()
        self.canvas.itemconfigure(self.console.handle, anchor='nw')
        self.canvas.bind("<Motion>", on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", on_left_click)
        self.canvas.bind("<ButtonPress-3>", on_right_click)
        self.canvas.bind_all("<Escape>", on_esc)

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
                eye_x = int(float(x_y[0])/1.5)
                eye_y = int(float(x_y[1])/1.5)
                self.filter_type.calculate_average(eye_x, eye_y)
                self.last_eye = (self.filter_type.filtered_x, self.filter_type.filtered_y)
            except ValueError:
                pass

def f(q,e):
    name = current_process().name
    q.put('Starting'+name)
    engine = pyttsx.init()
    q.put('Reached this')
    engine.setProperty('rate', 100)
    voices = engine.getProperty('voices')
    for voice in voices:
        engine.setProperty('voice', voice.id)
    #e.wait()
    #engine.startLoop()
    e.wait()
    engine.say('yo!')
    engine.runAndWait()
    q.put('Exiting')

def f2(q1,q2,e,estop): 
    start = time.clock()
    engine = pyttsx.init()
    end = time.clock()
    q2.put('Time to init engine: '+str(end-start))
    while estop.is_set() == False:
        #e.wait()
        if q1.empty() == False:
            engine.say(q1.get())
            start = time.clock()
            engine.runAndWait()
            end = time.clock()
            q2.put('Time to runAndWait: '+str(end-start))
        #e.clear()
        time.sleep(10)

def on_mouse_move(event):
    app.last_mouse = (event.x, event.y)

def on_esc(event):
    app.quit()

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

def select_last_letter():
    mainlog.debug('Selecting last letter')
    kb.process()

def speak(phrase):
    #q1.put(phrase)
    #e.set()
    engine.say(phrase)
    mainlog.debug('Speaking phrase '+phrase)

if __name__ == '__main__':
    ''' Run the gui interface '''
    # Create root of windowing system, set to fullscreen
    root = Tk()
    root.attributes("-fullscreen", True)
    w,h = (root.winfo_screenwidth(), root.winfo_screenheight()) # TODO fix the resolution issues

    # Create logger, fonts, keyboard
    logging.basicConfig(level=logging.DEBUG)
    mainlog = logging.getLogger('main')
    console_font = font.Font(family='Helvetica',size=settings.console_font_size, weight='bold')
    kb_font = font.Font(family='Helvetica',size=settings.kb_font_size, weight='bold')
    mainlog.debug('Using dict file '+settings.dict_path+settings.dict_filename)
    kb = OnscreenKeyboard(kb_font, settings.kb_shape, Predictionary('../dict/'+settings.dict_filename))
    if (settings.keep_coordinates_log == 1):
        coordinates_log = open(settings.log_name,'w')

    '''
    queue = Queue()

    from multiprocessing.managers import BaseManager
    class Q(BaseManager):
        pass
    BaseManager.register(str('get_queue'), callable=lambda: queue)
    manager = BaseManager(address=('', 50000), authkey='abc')
    server = manager.get_server()
    server.serve_forever()
    '''
    
    '''
    e = Event()
    estop = Event()
    q1,q2 = Queue(),Queue()
    p = Process(target=f2,args=(q1,q2,e,estop))
    p.start()
    '''

    '''
    p = Process(target=f1, args=(q,e,))
    mainlog.debug('This is where the new Process should start')
    p.start()
    '''
    engine = pyttsx.init()
    engine.startLoop(False)

    # Start main app
    app = Application(master=root,screen_size=(w,h))
    kb.attach_write_callback(app.console.write)
    kb.attach_speak_callback(speak)
    def clear_callback():
        speak(app.console.text)
        app.console.clear()
    kb.attach_clear_callback(clear_callback)
    #kb.attach_undo_function
    app.master.minsize(500,500)
    app.mainloop()
    app.quit()

    engine.endLoop()