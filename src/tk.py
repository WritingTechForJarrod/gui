'''
Author:    max@embeddedprofessional.com
'''
from __future__ import print_function
from __future__ import unicode_literals
from Tkinter import *
import tkFont
from threading import Thread
import time
import types

class Application(Frame):
    def __init__(self, master=None, screen_size=(1080, 720)):
        Frame.__init__(self, master)
        self.is_alive = True
        self.screen_w = screen_size[0]
        self.screen_h = screen_size[1]
        self.displayed_struct = None
        self.pack()
        self.createWidgets()

    def delete_stuff(self):
        self.w.delete(ALL)

    def draw_periodic(self):
        font = tkFont.Font(family='Helvetica',size=16, name="font16s")
        i = 0
        inc = 1
        while self.is_alive:
            if i < 0:
                inc = 1
            elif i == self.screen_w:
                inc = -1
            i += inc
            self.w.create_rectangle(i, 0, self.screen_w, 50, fill='#ff0')
            time.sleep(0.001)

    def quit(self):
        self.is_alive = False
        Frame.quit(self)

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT['text'] = 'QUIT'
        self.QUIT['fg']   = 'red'
        self.QUIT['command'] =  self.quit

        self.QUIT.pack({'side': 'left'})

        self.id_buttons = []
        '''i = 0
        for c_struct in monitor.name_dict.values():
            id_button = Button(self)
            id_button['text'] = c_struct.name
            id_button.pack({'side':'left'})
            id_button['command'] = lambda x=c_struct.name: self.set_displayed(x)
            i += 1
            self.id_buttons.append(id_button)

        '''
        self.w = Canvas(self.master, width=self.screen_w, height=self.screen_h)
        self.test_rec = self.w.create_rectangle(0, 0, self.screen_w, 50, fill='#ff0')
        self.w.pack()

    def set_displayed(self, c_struct_name):
        self.displayed_struct = monitor.name_dict[c_struct_name]

    def mainloop(self):
        go = Thread(target=self.draw_periodic)
        go.start()
        Frame.mainloop(self)
        go.join()

root = Tk()
app = Application(master=root, screen_size=(1080, 720))
app.master.minsize(500, 500)
app.mainloop()
root.destroy()