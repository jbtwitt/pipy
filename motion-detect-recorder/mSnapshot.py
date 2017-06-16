import cv2
import json
import datetime
from time import sleep
from classes.MdrSnapshot import MdrSnapshot
from classes.MdrMail import MdrMail

def mail(mdrConf, jpgFiles):
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()


def mdrSnapshotMain(mdrConf):
    from classes.MotionDetect import CMotionDetect
    # init motion detect
    mdrSnapshot = MdrSnapshot(mdrConf)
    jpgFile = mdrSnapshot.cameraSnapshot()
    im = cv2.imread(jpgFile)
    cMotion = CMotionDetect(im, alpha=0.4)

    frequency = mdrConf['snapshot']['mdr']['frequency'] - 1
    interval = mdrConf['snapshot']['mdr']['interval']
    mdFoundJpgFiles = []
    for i in range(frequency):
        sleep(interval)  # in second
        # motion detect
        jpgFile = mdrSnapshot.cameraSnapshot()
        im = cv2.imread(jpgFile)
        cnts = cMotion.update(im)

        if len(cnts) > 0:
            cv2.drawContours(im, cnts, -1, (0,155,0), 1)
            cv2.imwrite(jpgFile, im)
            mdFoundJpgFiles.append(jpgFile)
    # send mail
    if len(mdFoundJpgFiles) > 0 and mdrConf['snapshot']['mdr']['sendmail']:
        mdrConf['email']['body'] = 'md found ' + str(len(mdFoundJpgFiles))
        mail(mdrConf, mdFoundJpgFiles)


def snapshotMain(mdrConf):
    frequency = mdrConf['snapshot']['frequency'] - 1
    interval = mdrConf['snapshot']['interval']
    mdrSnapshot = MdrSnapshot(mdrConf)
    mdrSnapshot.cameraSnapshot()
    for i in range(frequency):
        sleep(interval)  # in second
        mdrSnapshot.cameraSnapshot()
    # send mail
    mail(mdrConf, mdrSnapshot.getSnapshotFiles())


if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
    # snapshotMain(mdrConf)
    # mdrSnapshotMain(mdrConf)
