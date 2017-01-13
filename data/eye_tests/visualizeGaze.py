import sys
import pylab

xVals = []
yVals = []
f = open('combined_calibration_log.txt','r')
#f = open('calibration_log_5.txt','r')

for line in f:
	vals = line.split(',')
	if (int(vals[3]) == 1):
		pylab.plot(vals[0],720 - float(vals[1]),'r.')
	elif (int(vals[3]) == 2):
		pylab.plot(vals[0],720 - float(vals[1]),'g.')
	elif (int(vals[3]) == 3):
		pylab.plot(vals[0],720 - float(vals[1]),'b.')
	elif (int(vals[3]) == 4):
		pylab.plot(vals[0],720 - float(vals[1]),'c.')
	elif (int(vals[3]) == 5):
		pylab.plot(vals[0],720 - float(vals[1]),'y.')

pylab.show()
