# from classes.T_PiCamMotionDetect import PiCamMotionDetect
# from classes.util import freeSpace
#import numpy as np
# import cv2
import time
import datetime
import os
import json
#import sys

def runMDR(mdrConf):
	fps = mdrConf['fps']
	endTime = mdrConf['endTs']
	resolution = mdrConf['resolution']
	cacheDir = mdrConf['camCache']

	print 'MDR start at ' + str(datetime.datetime.now())
	piMDR = PiCamMotionDetect(resolution, fps, cacheDir).start()
	while(1):
		if endTime is not None:
			if datetime.datetime.now() > endTime:
				break

		time.sleep(5)

		space1 = freeSpace()
		# break loop by an existing file
		if space1 < 1000000L or os.path.exists(quitCmd):
			break

	piMDR.stop()
	print 'MDR stop at ' + str(datetime.datetime.now())


def main():
	quitCmd = '/home/pi/jb/jbstop'
	if os.path.exists(quitCmd):
		print "remove quit file: %s" % quitCmd
		os.remove(quitCmd)

	startTime = None
	endTime = None

	startTime = datetime.datetime(2017,5,11, 22,0,0, 0)
	endTime = datetime.datetime(2017,5,12, 6,0,0, 0)
	#startTime = datetime.datetime(2016,9,23, 8,0,0,0)
	#endTime = datetime.datetime(2016,9,23, 17,0,0,0)

	if startTime is not None:
		print startTime
		if startTime > datetime.datetime.now():
			waitTime = startTime-datetime.datetime.now()
			time.sleep(waitTime.seconds + (waitTime.days * 86400))
	else:
		print datetime.datetime.now()

	if endTime is not None:
		print endTime


	# cam motion detect in separated thread
	fps = 30
	#resolution = (640, 480)
	resolution = (800, 608)

	# monitor free space
	# space0 = freeSpace()
	# print space0

	mdrConf = {
		'camCache': '../../../camCache',
		'resolution': (800,608),
		'fps': 30,
		'startTs': None,
		'endTs': None
	}
	mdrConf['startTs'] = startTime
	mdrConf['endTs'] = endTime
	# runMDR(mdrConf)
	print datetime.datetime.now()
	# space1 = freeSpace()
	# print "space used: %d" % (space0 - space1)


'''
piMotion = PiCamMotionDetect(resolution, fps).start()
while(1):
	if endTime is not None:
		if datetime.datetime.now() > endTime:
			break

	time.sleep(5)

	space1 = freeSpace()
	# break loop by an existing file
	if space1 < 1000000L or os.path.exists(quitCmd):
		break

piMotion.stop()
'''
if __name__ == "__main__":
	rootDir = 'motion-detect-recorder/'
	conf = json.load(open(rootDir + 'mdr.json'))
	# print conf
	# main()
