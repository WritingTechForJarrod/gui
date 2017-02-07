'''
Writing Tech for Jarrod
Server
max@embeddedprofessional.com

Server handling all input/output routing
'''
# For future compatibility with python 3
from __future__ import print_function
from __future__ import unicode_literals
# Dynamic import of python 2 or 3
import sys
try:
	assert sys.version_info[0] == 3
	from tkinter import *
	import tkinter.font as font
except AssertionError as e:
	from Tkinter import *
	import tkFont as font
from threading import Thread
import time
import logging
import zmq
from wtfj import *

class Application(Frame):
	def __init__(self,master=None,sz=(1080, 720)):
		# Application housekeeping
		Frame.__init__(self, master)
		self.alive = True
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("tcp://*:5555")
		self.canvas = Canvas(self.master,width=sz[0],height=sz[1])
		self.canvas.pack()
		self.console = Text(sz[0]/2,sz[1]/2,console_font)
		self.console.draw(self.canvas)
		self.frames_drawn = 0

	def _draw_periodic(self):
		self.frames_drawn += 1
		try:
			message = self.socket.recv(zmq.DONTWAIT)
			ret = "ack"
			serverlog.debug("Received request: %s" % message)
			if "quit" in message:
				serverlog.debug('Quitting server...')
				quit()
			elif "#face" in message:
				parts = message.split(':')
				serverlog.debug("%s" % int(parts[1]))
				self.console.clear()
				if int(parts[1]) == 0:
					self.console.write('No input')
				elif int(parts[1]) == 1:
					self.console.write('Eyebrow')
				elif int(parts[1]) == 2:
					self.console.write('Mouth')
				elif int(parts[1]) == 3:
					self.console.write('Both')
			else:
				self.console.write('Drawing frame # '+str(self.frames_drawn))
			self.console.update(self.canvas,(0,0))
			self.socket.send(bytes(ret))
		except zmq.Again:
			pass
			
		self.canvas.after(50, self._draw_periodic)

	def quit(self):
		logging.getLogger('app').debug('Exiting application...')
		self.alive = False
		Frame.quit(self)

	def mainloop(self):
		go = Thread(target=self._draw_periodic)
		go.start()
		Frame.mainloop(self)
		go.join()

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	serverlog = logging.getLogger("server")
	applog = logging.getLogger("app")

	root = Tk()
	root.attributes("-fullscreen", True)
	console_font = font.Font(family='Helvetica',size=settings.console_font_size, weight='bold')
	app = Application(master=root,sz=(1080,720))

	alive = True
	serverlog.debug("Starting server...")
	app.mainloop()
	app.quit()