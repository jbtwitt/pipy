from MotionDetect import CMotionDetect
#from DetectedFrameStore import DetectedFrameStore
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import os
import datetime
import numpy as np
import MdrUtil as MdrUtil
 
class PiCamMotionDetect:
	def __init__(self, resolution, frameRate, cacheDir):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = frameRate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
 
		self.startTime = None
		self.endTime = None
		self.stopped = False

		self.homeDir = cacheDir
		self.homeDir = '%s/d%s' % (self.homeDir,
			datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
		if not os.path.exists(self.homeDir):
			os.makedirs(self.homeDir)

		self.mdrFile = open(self.homeDir + '/mdrData.json', 'w')
		self.mdrFile.write('{')
		self.mdrFile.write('"resolution":' + '"' + str(resolution) + '",')
		self.mdrFile.write('"fps":' + str(frameRate))

		self.cacheOn = False
		self.cacheHomeDir = self.homeDir
		if self.cacheOn:
			if not os.path.exists(self.cacheHomeDir):
				print self.cacheHomeDir
				os.makedirs(self.cacheHomeDir)

		count = 0
		for f in self.stream:
			frame = f.array
			self.rawCapture.truncate(0)
			count += 1
			if count > 25:
				break
		self.totalFrames = 1
		self.cMotion = CMotionDetect(frame, alpha=0.4)
		#self.frameStore = DetectedFrameStore(home='/home/pi/jb/tmp').start()

	def start(self):
		# start the thread
		self.startTime = datetime.datetime.now()
		Thread(target=self.update, args=()).start()
		return self
 
	def update(self):
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			frame = f.array
			self.rawCapture.truncate(0)

			#if self.cMotion is None:
			#	self.cMotion = CMotionDetect(frame)

			if self.cacheOn:
				path = "%s/f%s.jpg" % (self.cacheHomeDir,
					datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
				cv2.imwrite(path, frame)

			self.totalFrames += 1
			cnts = self.cMotion.update(frame)
			if len(cnts) > 0:
				#self.frameStore.queue((frame, cnts, datetime.datetime.now()))
				mdrTs = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
				path = "%s/f%s" % (self.homeDir, mdrTs)
				#cv2.drawContours(frame, cnts, -1, (255,255,255), 1)
				cv2.imwrite(path + '.jpg', frame)

				cntFile = open(path + '.json', "w")
				cntFile.write('{"f' + mdrTs + '.jpg":' + MdrUtil.contours2ArsStr(cnts) + '}')
				cntFile.close

				'''
				cntStr = str(cnts).replace(' ','').replace("\n",'')
				cntStr = cntStr.replace('array(','').replace(')','')
				contoursFile = open(path + '.json2', "w")
				contoursFile.write('{"f' + mdrTs + '.jpg":' + cntStr + '}')
				contoursFile.close
				'''
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				runTime = datetime.datetime.now() - self.startTime
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()

				self.mdrFile.write(",total frames: " + str(self.totalFrames))
				self.mdrFile.write(",run time: " + str(runTime))
				runTime = runTime.seconds + (runTime.days * 86400)
				if runTime > 0:
					self.mdrFile.write(",actual fps: %0.1f" % (self.totalFrames / runTime))
				#print "fps: %0.1f" % (self.totalFrames / (runTime.seconds + (runTime.days * 86400)))
				self.mdrFile.write('}')
				self.mdrFile.close

				#self.frameStore.stop()
				return

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
