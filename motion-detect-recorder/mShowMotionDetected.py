from classes.CamCacheMgr import CamCacheMgr
from classes.MdrUtil import MdrUtil
# import numpy as np
import cv2
import datetime
import time
import json

mdrUtil = MdrUtil()
# def arr2nparr(arr):
#     nparr = []
#     for a in arr:
#         nparr.append(np.array(a))
#     return nparr

def drawData(img, jsonData):
	for k, v in jsonData.items():
		# cnts = arr2nparr(v)
		cnts = mdrUtil.arr2Contours(v)
		cv2.drawContours(img, cnts, -1, (0,155,0), 1)

def showSegFrames(win, segMgr, segCount, lag=166):
	nextSeg = None
	seg = segMgr.segs[segCount]
	if (segCount+1) < len(segMgr.segs):
		nextSeg = segMgr.segs[segCount+1]
		nextSegTime = str(nextSeg[0] - seg[1])
		nextSegTime = 'next ' + nextSegTime[0:len(nextSegTime)-7]
	names = segMgr.findSegImgFiles(seg)
	txtColor = (0,255,0)
	for name in names:
		ts = segMgr.toTimestamp(name)
		txtFormat = '%d/%d] ' % (segCount+1, len(segMgr.segs))
		#txtFormat += ts.strftime("%m-%d-%y %H:%M:%S %f")
		txtFormat += ts.strftime("%H:%M:%S")
		path = segMgr.baseDir + name
		im = cv2.imread(path)

		#print path.replace('.jpg','.json')
		cntStr = json.load(open(path.replace('.jpg','.json')))
		drawData(im, cntStr)

		cv2.putText(im, txtFormat,
			(10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, txtColor, 2)
		if nextSeg is not None:
			cv2.putText(im, nextSegTime,
				(10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
		cv2.imshow(win, im)
		k = cv2.waitKey(lag) & 0xff
		if k == 27:
			return False
	return True


def main(mdrConf):
	homeDir = mdrConf['camCacheRepository']
	camCacheMgr = CamCacheMgr(homeDir)
	segMgr = camCacheMgr.getLastCache()
	print 'cache dir: ' + segMgr.baseDir
	print 'segs: %d, frames: %d' % (len(segMgr.segs), segMgr.totalFrames)
	segMgr.rptSegCap()

	win = 'win'
	cv2.namedWindow(win, flags=cv2.WINDOW_AUTOSIZE)
	cv2.moveWindow(win, 5, 45)
	count = 0
	for seg in segMgr.segs:
		if not showSegFrames(win, segMgr, count, 360):
			break
		count += 1
		#time.sleep(5)
	cv2.destroyAllWindows()


if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
	main(mdrConf)

'''
# frame folder
homeDir = '/home/pi/camCache/'
homeDir = '../camCache/'
subDirs = os.listdir(homeDir)
subDirs.sort(reverse=True)
homeDir = homeDir + subDirs[0] + '/'
print homeDir

# frame images
#imgFiles = os.listdir(homeDir)
imgFiles = []
tmpImgFiles = glob.glob(homeDir + '*.jpg')
for img in tmpImgFiles:
	imgFiles.append(img[len(homeDir):])
imgFiles.sort()
segs, total = findSegments(imgFiles)
print "Total Files: %d" % len(imgFiles)
print 'total segment: %s, frames: %d' % (len(segs), total)
'''

'''
for seg in segs:
	begin, end = seg[0], seg[1]
	print ts2filename(seg[0])
	print ts2filename(seg[1])
	print 'seg count: %s, duration: %s seconds' % (seg[2], (end-begin).seconds)

cv2.namedWindow('image')
cv2.moveWindow('image', 5, 45)

prevTs = None
textColor = (0,255,0)

count = 0
countBreak = 0
for filename in imgFiles:
	if filename.endswith(".jpg"):
		#print(filename)
		ts = toTimestamp(filename)

		# show
		img = cv2.imread(homeDir + filename)
		cv2.putText(img, ts.strftime("%m/%d/%y %H:%M:%S %f"),
			(10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, textColor, 2)
		cv2.imshow('image', img)
		count += 1

		k = cv2.waitKey(166) & 0xff
		if k == 27:
			break

		if prevTs is not None:
			if (ts - prevTs).seconds > 5:
				#print '%s: %d' % (filename, (ts - prevTs).seconds)
				time.sleep(3)
				#if (cv2.waitKey(5000) & 0xff) == ord("n"):
				#	prevTs = ts
				#	continue

		prevTs = ts

	#if count > 1000:
	#	break

time.sleep(5)
print "file count: %d" % count
cv2.destroyAllWindows()
'''
