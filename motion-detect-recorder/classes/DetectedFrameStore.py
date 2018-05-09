from threading import Thread
import cv2
import datetime
 
#
# Store detected frame item
#
class DetectedFrameStore:
	def __init__(self, home='tmp'):
		self.frameMeta = []
		self.homeDir = home
		self.stopped = False
		self.contourColor = (0, 255, 0)

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		while True:
			if self.stopped:
				break
			if len(self.frameMeta) == 0:
				continue
			frame, contours, ts = self.frameMeta.pop(0)
			path = "%s/d%s.jpg" % (self.homeDir, ts.strftime("%Y%m%d%H%M%S%f"))
			cv2.drawContours(frame, contours, -1, self.contourColor, 1)
			cv2.imwrite(path, frame)
 
	def queue(self, frameItem):
		self.frameMeta.append(frameItem)
 
	def stop(self):
		self.stopped = True
