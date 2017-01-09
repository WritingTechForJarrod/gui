#!/bin/bash/python
import time
import logging

timelog = []

def self_timing(func):
	def func_wrapper(*args,**kwargs):
		start = time.clock()
		ret = func(*args,**kwargs)
		dt = time.clock()-start
		timelog.append([func.__name__,start,dt])
		return ret
	return func_wrapper

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	
	@self_timing
	def foo():
		pass
	
	@self_timing
	def bar():
		pass
	
	foo()
	bar()
	for line in timelog:
		logging.debug(line)
