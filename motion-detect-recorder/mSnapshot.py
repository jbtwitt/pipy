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
    summary = "summary\n"
    if len(mdRecords) > 0:
        color = (0,155,0)
        jpgFiles = mdrSnapshot.getSnapshotFiles()
        for jpgIdx, cnts in mdRecords:
            jpgFile = jpgFiles[jpgIdx]
            summary += str(jpgIdx) + ': ' + jpgFile + ', contours: ' + str(len(cnts)) + '\n'
            im = cv2.imread(jpgFile)
            cv2.drawContours(im, cnts, -1, color, 1)
            cv2.imwrite(jpgFile, im)

        # send mail
        if mdrConf['snapshot']['sendmail']:
            mdrConf['email']['body'] = summary
            mail(mdrConf, jpgFiles)


if __name__ == "__main__":
    mdrConfJsonFile = 'mdr.json'
    if len(sys.argv) > 1:
        mdrConfJsonFile = sys.argv[1]
    mdrConf = json.load(open(mdrConfJsonFile))
    main(mdrConf)
