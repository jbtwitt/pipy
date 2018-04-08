import sys
import json
import glob
import os
import tarfile
import zipfile
print(os.listdir("/temp"))
for i in range(2):
    continue
print(os.path.dirname("/pirepo/front-door/apply/20180211.tar.gz"))
# cwd = os.getcwd()
# os.chdir('/pirepo/front-door/apply/')
# opener, mode = tarfile.open, 'r:gz'
# try:
#     targz = opener("/pirepo/front-door/apply/20180211.tar.gz", mode)
#     targz.extractall()
#     targz.close()
# finally:
#     os.chdir(cwd)
sys.exit()
import dryscrape
from bs4 import BeautifulSoup
import time
import datetime
import re

#we visit the main page to initialise sessions and cookies
session = dryscrape.Session()
session.set_attribute('auto_load_images', False)
session.set_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95     Safari/537.36')    

#call this once as it is slow(er) and then you can do multiple download, though there seems to be a limit after which you have to reinitialise...
session.visit("https://finance.yahoo.com/quote/AAPL/history?p=AAPL")
response = session.body()


#get the dowload link
soup = BeautifulSoup(response, 'lxml')
for taga in soup.findAll('a'):
    if taga.has_attr('download'):
        url_download = taga['href']
print(url_download)

#now replace the default end date end start date that yahoo provides
s = "2017-02-18"
period1 = '%.0f' % time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d").timetuple())
e = "2017-05-18"
period2 = '%.0f' % time.mktime(datetime.datetime.strptime(e, "%Y-%m-%d").timetuple())

#now we replace the period download by our dates, please feel free to improve, I suck at regex
m = re.search('period1=(.+?)&', url_download)
if m:
    to_replace = m.group(m.lastindex)
    url_download = url_download.replace(to_replace, period1)        
m = re.search('period2=(.+?)&', url_download)
if m:
    to_replace = m.group(m.lastindex)
    url_download = url_download.replace(to_replace, period2)

#and now viti and get body and you have your csv
session.visit(url_download)
csv_data = session.body()

#and finally if you want to get a dataframe from it
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

import pandas as pd
df = pd.read_csv(StringIO(csv_data), index_col=[0], parse_dates=True)
df

"""
import numpy as np
import cv2
from skimage.measure import compare_ssim

def arrs2Contours(arrs):
    contours = []
    for arr in arrs:
        contours.append(np.array(arr))
    return contours


def cropArea(im, mdArea):
    x1 = mdArea[0]
    y1 = mdArea[1]
    x2 = mdArea[2]
    y2 = mdArea[3]
    return im[y1:y2, x1:x2]


def compare(imSrc, imTgt, mdCnts):
    for cnts in mdCnts:
        x,y,w,h = cv2.boundingRect(cnts)
        srcImg = cropArea(imSrc, [x, y, x+w, y+h])
        tgtImg = cropArea(imTgt, [x, y, x+w, y+h])

        # convert the images to grayscale
        grayA = cv2.cvtColor(srcImg, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(tgtImg, cv2.COLOR_BGR2GRAY)

        # compute the Structural Similarity Index (SSIM) between the two
        # images, ensuring that the difference image is returned
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        # diff = (diff * 255).astype("uint8")
        print "SSIM: {}".format(score)


def compareContourArea(imSrc, imTgt, cnts):
    x,y,w,h = cv2.boundingRect(cnts)
    if w > 9 and h > 9:
        # somehow compare_ssim throw error if w or h are small
        srcImg = cropArea(imSrc, [x, y, x+w, y+h])
        tgtImg = cropArea(imTgt, [x, y, x+w, y+h])
        (score, diff) = compare_ssim(srcImg, tgtImg, multichannel=True, full=True)
        return score

    # convert the images to grayscale
    # grayA = cv2.cvtColor(srcImg, cv2.COLOR_BGR2GRAY)
    # grayB = cv2.cvtColor(tgtImg, cv2.COLOR_BGR2GRAY)
    # (score, diff) = compare_ssim(grayA, grayB, full=True)
    return -1


def testContours():
    import glob
    import json
    win = 'snapshot'
    cv2.namedWindow(win, flags=cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(win, 5, 45)
    dir = '/tmp/snapshot/'
    jsonFiles = glob.glob(dir + '*.json')
    contours = json.load(open(jsonFiles[0]))
    print 'mdRecords: ' + str(len(contours))
    idxs = contours.keys()
    for idx in idxs:
        im = cv2.imread(idx)
        imPrev = cv2.imread(contours[idx]['snapshot'])
        snapshotCnts = arrs2Contours(contours[idx]['contours'])
        print "prev snapshot:" + contours[idx]['snapshot']
        print "snapshot jpg: " + idx
        print "contours: " + str(len(snapshotCnts))
        for cnts in snapshotCnts:
            moments = cv2.moments(cnts)
            area = moments["m00"]
            if area > 0:
                cX = int(moments["m10"] / area)
                cY = int(moments["m01"] / area)
                cv2.circle(im, (cX, cY), 3, (255, 255, 255), -1)
                score = compareContourArea(imPrev, im, cnts)
            x,y,w,h = cv2.boundingRect(cnts)
            print "\tcontour area/center: " + str(area) + ', ' + str(w*h) + " / (" + str(cX) + ', ' + str(cY) + ')'
            print "\tarea ratio/score: " + str(area/(w*h)) + " / " + str(score)
            cv2.rectangle(im, (x, y), (x+w, y+h), (0,0,155), 1)

        cv2.drawContours(im, snapshotCnts, -1, (0,155,0), 1)
        cv2.imshow(win, im)


        while(True):
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

def testSnapshot():
    import os
    import classes.MdrUtil as MdrUtil
    dir = '/tmp/snapshot/'
    jpgFiles = os.listdir(dir)
    for i in range(2):
        cnts = MdrUtil.diff2JpgFiles(dir + jpgFiles[i], dir + jpgFiles[i + 1])
        if len(cnts) > 0:
            im = cv2.imread(dir + jpgFiles[i + 1])
            cv2.drawContours(im, cnts, -1, (0,155,0), 1)
            centers = MdrUtil.findContoursCenters(cnts)
            for c in centers:
                cv2.circle(im, (c[0], c[1]), 3, (255, 255, 255), -1)
            cv2.imwrite('/tmp/test_' + str(i) + '.jpg', im)
            print 'contours: ' + str(len(cnts))
            # test contours to string
            jsonStr = '{"cnts":' + contours2ArrsStr(cnts) + '}'
            jsonObj = json.loads(jsonStr)
            im = cv2.imread(dir + jpgFiles[i + 1])
            cv2.drawContours(im, arrs2Contours(jsonObj['cnts']), -1, (0,155,0), 1)
            cv2.imwrite('/tmp/test_' + str(i) + str(i) + '.jpg', im)


def testCV2Camera():
    cap = cv2.VideoCapture(0)
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        # cv2.imshow('frame',gray)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    testContours()
    # import motion-detect-recorder.classes.MdrUtil
    # mdrConfJsonFile = 'mdr.json'
    # mdrConf = json.load(open(mdrConfJsonFile))
"""