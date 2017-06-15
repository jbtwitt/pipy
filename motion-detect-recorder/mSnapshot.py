import os
import cv2
import json
import datetime
from time import sleep
from classes.MdrMail import MdrMail

M_SNAPSHOT = 'snapshot'
def snapshotFilename(mdrConf):
    timestamp = datetime.datetime.now()
    return mdrConf['camCacheRepository'] + '/snapshot_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'


def snapshot(mdrConf):
    """Snapshot: init camera, take a picture and close camera
    """
    from picamera import PiCamera
    camera = PiCamera()
    jpgName = snapshotFilename(mdrConf)
    resolution = mdrConf[M_SNAPSHOT]['camera']['resolution']
    try:
        camera.resolution = (resolution[0], resolution[1])
        camera.start_preview()
        camera.capture(jpgName)
        camera.stop_preview()
    finally:
        camera.close()
    return jpgName


def mail(mdrConf, jpgFiles):
    mdrConf['email']['body'] = 'interval:' + str(mdrConf[M_SNAPSHOT]['frequency'])
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()


def mdrMain(mdrConf):
    from classes.MotionDetect import CMotionDetect
    # motion detect
    jpgFile = snapshot(mdrConf)
    im = cv2.imread(jpgFile)
    cMotion = CMotionDetect(im, alpha=0.4)

    jpgFiles = []
    jpgFiles.append(jpgFile)

    frequency = mdrConf[M_SNAPSHOT]['frequency'] - 1
    interval = mdrConf[M_SNAPSHOT]['interval']
    for i in range(frequency):
        sleep(interval)  # in second
        # motion detect
        jpgFile = snapshot(mdrConf)
        im = cv2.imread(jpgFile)
        cnts = cMotion.update(im)

        if len(cnts) > 0:
            print 'md found ...'
            cv2.drawContours(im, cnts, -1, (0,155,0), 1)
            cv2.imwrite(jpgFile, im)
            jpgFiles.append(jpgFile)
        else:
            os.remove(jpgFile)

def main(mdrConf):
    frequency = mdrConf[M_SNAPSHOT]['frequency'] - 1
    interval = mdrConf[M_SNAPSHOT]['interval']
    jpgFiles = []
    jpgFiles.append(snapshot(mdrConf))
    for i in range(frequency):
        sleep(interval)  # in second
        jpgFiles.append(snapshot(mdrConf))
    # send mail
    mail(mdrConf, jpgFiles)


if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
    # main(mdrConf)
    mdrMain(mdrConf)
