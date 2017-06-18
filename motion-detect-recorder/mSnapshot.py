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


def main(mdrConf):
    from classes.MdrSnapshot import MdrSnapshot
    doMdRecord = mdrConf['snapshot']['mdRecord']
    frequency = mdrConf['snapshot']['frequency'] - 1
    interval = mdrConf['snapshot']['interval']
    # mdArea = None
    # if 'mdArea' in mdrConf['snapshot']:
    #     mdArea = mdrConf['snapshot']['mdArea']
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
    summary = "mdr summary<br>"
    if len(mdRecords) > 0:
        color = (0,155,0)
        lastSnapshot = jpgFile
        im = cv2.imread(lastSnapshot)
        # if not mdArea == None:
        #     im = MdrUtil.cropArea(im, mdArea)
        jpgFiles = mdrSnapshot.getSnapshotFiles()
        for jpgIdx, cnts in mdRecords:
            summary += str(jpgIdx) + ': ' + jpgFiles[jpgIdx] + ', contours: ' + str(len(cnts)) + '<br>'
            cv2.drawContours(im, cnts, -1, color, 1)
        cv2.imwrite(lastSnapshot, im)

        # send mail
        if mdrConf['snapshot']['sendmail']:
            mdrConf['email']['body'] = summary
            mail(mdrConf, mdrSnapshot.getSnapshotFiles())


if __name__ == "__main__":
    mdrConfJsonFile = 'mdr.json'
    if len(sys.argv) > 1:
        mdrConfJsonFile = sys.argv[1]
    mdrConf = json.load(open(mdrConfJsonFile))
    main(mdrConf)
