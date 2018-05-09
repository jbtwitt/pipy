#import datetime
import cv2
#import numpy as np
 
#
# Motion Detect using running average
#
class CMotionDetect:
	def __init__(self, frame, alpha=0.5):

		"""
		# alpha is the weight of the input image. According to Docs, alpha regulates the update speed (how fast the accumulator 'forgets' about earlier images). In simple words, if alpha is a higher value, average image tries to catch even very fast and short changes in the data. If it is lower value, average becomes sluggish and it won't consider fast changes in the input images. I will explain it a little bit with help of images at the end of article.
		# kernel size used for Gaussian Blur
		"""
		self.alpha = alpha
		self.kernelSize = (21, 21)
		self.threshold = 5

		# initial avg before running average
		# astype("float") is a much or fail on accumulateWeighted
		#frame = imutils.resize(frame, width=500)
		toGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		toGray = cv2.GaussianBlur(toGray, self.kernelSize, 0)
		self.avg = toGray.astype("float")

	def update(self, frame):
		toGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		toGray = cv2.GaussianBlur(toGray, self.kernelSize, 0)
		# using accumulate avg help deal with lighting condition change
		cv2.accumulateWeighted(toGray, self.avg, self.alpha)
		frameDelta = cv2.absdiff(toGray, cv2.convertScaleAbs(self.avg))
		thresh = cv2.threshold(frameDelta, self.threshold, 255,
			cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=1)
		(im, cnts, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		#if len(cnts) > 0:	# motion found
		#	self.frameStore.queue((frame, cnts, datetime.datetime.now()))
		return cnts

	def getBackground(self):
		return cv2.convertScaleAbs(self.avg)
