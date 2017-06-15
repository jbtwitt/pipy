import os
import cv2
import json
import datetime
from time import sleep
from classes.MdrUtil import MdrUtil
from classes.MdrMail import MdrMail

def mail(mdrConf, jpgFiles):
    mdrConf['email']['body'] = 'interval:' + str(mdrConf[M_SNAPSHOT]['frequency'])
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()


def mdrMain(mdrConf):
    from classes.MotionDetect import CMotionDetect
    mdrUtil = MdrUtil(mdrConf)
    # motion detect
    jpgFile = mdrUtil.cameraSnapshot()
    im = cv2.imread(jpgFile)
    cMotion = CMotionDetect(im, alpha=0.4)

    jpgFiles = []
    jpgFiles.append(jpgFile)

    frequency = mdrConf['snapshot']['mdr']['frequency'] - 1
    interval = mdrConf['snapshot']['mdr']['interval']
    for i in range(frequency):
        sleep(interval)  # in second
        # motion detect
        jpgFile = mdrUtil.cameraSnapshot()
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
    mdrUtil = MdrUtil(mdrConf)
    frequency = mdrConf['snapshot']['frequency'] - 1
    interval = mdrConf['snapshot']['interval']
    jpgFiles = []
    jpgFiles.append(mdrUtil.cameraSnapshot())
    for i in range(frequency):
        sleep(interval)  # in second
        jpgFiles.append(mdrUtil.cameraSnapshot())
    # send mail
    mail(mdrConf, jpgFiles)


if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
    # main(mdrConf)
    mdrMain(mdrConf)
