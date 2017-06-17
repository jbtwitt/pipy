import sys
import cv2
import json
import datetime
from time import sleep
from classes.MdrMail import MdrMail
import classes.MdrUtil as MdrUtil

def mail(mdrConf, jpgFiles):
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()


def mdrSnapshotMain(mdrConf):
    from classes.MdrSnapshot import MdrSnapshot
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


def main(mdrConf):
    from classes.MdrSnapshot import MdrSnapshot
    doMdRecord = mdrConf['snapshot']['mdRecord']
    frequency = mdrConf['snapshot']['frequency'] - 1
    interval = mdrConf['snapshot']['interval']
    mdRecords = []
    mdrSnapshot = MdrSnapshot(mdrConf)
    prevJpgFile = mdrSnapshot.cameraSnapshot()
    for i in range(frequency):
        sleep(interval)  # in second
        jpgFile = mdrSnapshot.cameraSnapshot()
        # md record
        if doMdRecord:
            cnts = MdrUtil.diff2JpgFiles(prevJpgFile, jpgFile)
            if len(cnts) > 0:
                mdRecords.append((i + 1, cnts))

    if len(mdRecords) > 0:
        color = (0,155,0)
        lastSnapshot = jpgFile
        im = cv2.imread(lastSnapshot)
        jpgFiles = mdrSnapshot.getSnapshotFiles()
        for jpgIdx, cnts in mdRecords:
            print str(jpgIdx) + ': ' + jpgFiles[jpgIdx] + ', contours: ' + str(len(cnts))
            cv2.drawContours(im, cnts, -1, color, 1)
        cv2.imwrite(lastSnapshot, im)

    # send mail
    if mdrConf['snapshot']['sendmail']:
        # mdrConf['email']['body'] = 'md found ' + str(len(mdRecords))
        mail(mdrConf, mdrSnapshot.getSnapshotFiles())


if __name__ == "__main__":
    mdrConfJsonFile = 'mdr.json'
    if len(sys.argv) > 1:
        mdrConfJsonFile = sys.argv[1]
    mdrConf = json.load(open(mdrConfJsonFile))
    main(mdrConf)
    # if len(sys.argv) > 1 and sys.argv[1] == 'mdrSnapshot':
    #     mdrSnapshotMain(mdrConf)
    # else:
    #     snapshotMain(mdrConf)
