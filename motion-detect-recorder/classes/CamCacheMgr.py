import datetime
import os
import glob

class CamCacheMgr:
	def __init__(self, baseDir='../camCache'):
		self.baseDir = baseDir
		self.subDirs = os.listdir(self.baseDir)
		self.subDirs.sort(reverse=True)

	def getLastCache(self):
		if len(self.subDirs) > 0:
			return SegMgr(self.baseDir + '/' + self.subDirs[0] + '/')
		return None

class SegMgr:
	def __init__(self, baseDir, capSeconds=60):
		self.baseDir = baseDir
		self.imgFiles = []
		tmpImgFiles = glob.glob(self.baseDir + '*.jpg')
		for img in tmpImgFiles:
			self.imgFiles.append(img[len(self.baseDir):])
		self.imgFiles.sort()
		#print self.imgFiles[0]
		self.segs, self.totalFrames = self.findSegments(capSeconds)

	def findSegments(self, capSeconds=5):
		segs = []
		segCount = 0
		totalFrames = 0
		startTs = None
		prev = None
		for filename in self.imgFiles:
			ts = self.toTimestamp(filename)
			if startTs is None:
				startTs = ts
			if prev is not None:
				if (ts - prev).seconds > capSeconds:
					segs.append([startTs, prev, segCount])
					startTs = ts
					totalFrames += segCount
					segCount = 0
			segCount += 1
			prev = ts
		if segCount > 0:
			segs.append([startTs, prev, segCount])
			totalFrames += segCount
		return segs, totalFrames

	def ts2filename(self, ts):
		return 'f' + ts.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'

	def findSegImgFiles(self, seg):
		segFiles = []
		begin, end = self.ts2filename(seg[0]), self.ts2filename(seg[1])
		for img in self.imgFiles:
			if len(segFiles) >= seg[2]:
				break
			if img >= begin and img <= end:
				segFiles.append(img)
		return segFiles

	def rptSegCap(self):
		count = 0
		prev = None
		for seg in self.segs:
			startTs = seg[0].strftime("%m-%d-%y %H:%M:%S")
			count += 1
			if prev is None:
				print '%s [%d:%d]' % (startTs, count, seg[2])
				prev = seg
				continue
			print '%s [%d:%d], %d' % (startTs, count, prev[2], (seg[0] - prev[1]).seconds)
			prev = seg

	def toTimestamp(self, file):
		year = int(file[1:5])
		month = int(file[5:7])
		day = int(file[7:9])
		h = int(file[10:12])
		min = int(file[12:14])
		sec = int(file[14:16])
		msec = int(file[17:23])
		#print 'yr: %d, mon: %d, day: %d, hr: %d, min: %d, sec: %d, msec %d' % (
		#	year, month, day, h, min, sec, msec)
		return datetime.datetime(year, month, day, h, min, sec, msec)
