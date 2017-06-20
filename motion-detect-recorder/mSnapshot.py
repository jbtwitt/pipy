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


def getContourFilename(mdrConf):
    repository = mdrConf['snapshotRepository']
    timestamp = datetime.datetime.now()
    return repository + '/contour_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.json'


def saveSnapshotContours(mdrConf, snapshotFiles, mdRecords):
    cntFile = open(getContourFilename(mdrConf), "w")
    jsonStr = ''
    i = 1
    for jpgFile, cnts in mdRecords:
        # json format "jpgFile": contour array string
        jsonStr += '"' + jpgFile + '": ' + MdrUtil.contours2ArrsStr(cnts)
        if i < len(mdRecords):
            jsonStr += ','
        i += 1
    cntFile.write('{' + jsonStr + '}')
    cntFile.close


RUN_SNAPSHOT = 'run-snapshot'
def main(mdrConf):
    times = 1
    seconds = 0
    if RUN_SNAPSHOT in mdrConf:
        if 'times' in mdrConf[RUN_SNAPSHOT]:
            times = mdrConf[RUN_SNAPSHOT]['times']
        if 'sleep' in mdrConf[RUN_SNAPSHOT]:
            seconds = mdrConf[RUN_SNAPSHOT]['sleep']
    for i in range(times):
        mainSnapshot(mdrConf)
        sleep(seconds)


def mainSnapshot(mdrConf):
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
                mdRecords.append((prevJpgFile, cnts))
        prevJpgFile = jpgFile

    if len(mdRecords) > 0:
        jpgFiles = mdrSnapshot.getSnapshotFiles()
        summary = "summary " + str(len(mdRecords)) + '/' + str(len(jpgFiles)) + "\n"
        color = (0,155,0)
        mdrFiles = []
        for jpgFile, cnts in mdRecords:
            summary += jpgFile + ' contours: ' + str(len(cnts)) + '\n'
            im = cv2.imread(jpgFile)
            cv2.drawContours(im, cnts, -1, color, 1)
            cv2.imwrite(jpgFile, im)
            mdrFiles.append(jpgFile)

        saveSnapshotContours(mdrConf, jpgFiles, mdRecords)
        # send mail
        if mdrConf['snapshot']['sendmail']:
            mdrConf['email']['body'] = summary
            mail(mdrConf, mdrFiles)


if __name__ == "__main__":
    mdrConfJsonFile = 'mdr.json'
    if len(sys.argv) > 1:
        mdrConfJsonFile = sys.argv[1]
    mdrConf = json.load(open(mdrConfJsonFile))
    main(mdrConf)
