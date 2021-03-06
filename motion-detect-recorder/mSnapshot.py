import sys
import cv2
import json
import datetime
from time import sleep
from classes.MdrMail import MdrMail
import classes.MdrUtil as MdrUtil
import os
import shutil

def mail(mdrConf, mdRecords):
    if len(mdRecords) > 0:
        color = (0,155,0)
        mdrFiles = []
        for prevJpgFile, snapshotFile, cnts in mdRecords:
            im = cv2.imread(snapshotFile)
            cv2.drawContours(im, cnts, -1, color, 1)
            jpgFile = snapshotFile.replace('.jpg', '_.jpg')
            cv2.imwrite(jpgFile, im)
            mdrFiles.append(jpgFile)
        mdrMail = MdrMail(mdrConf)
        mdrMail.attachImages(mdrFiles)
        mdrMail.send()


def getContourFilename(mdrConf):
    repository = mdrConf['snapshotRepository']
    timestamp = datetime.datetime.now()
    return repository + '/contour_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.json'


def mdRecord2Json(mdRecord):
    prevJpgFile, jpgFile, jpgDiffCnts = mdRecord
    return (
        '"' + jpgFile + '":{'
            '"contours":' + MdrUtil.contours2ArrsStr(jpgDiffCnts) + ','
            '"snapshot":"' + prevJpgFile + '"'
        '}'
    )


def saveSnapshotContours(mdrConf, mdRecords):
    cntFile = open(getContourFilename(mdrConf), "w")
    jsonStr = ''
    i = 1
    for mdRecord in mdRecords:
        jsonStr += mdRecord2Json(mdRecord)
        if i < len(mdRecords):
            jsonStr += ','
        i += 1
    cntFile.write('{' + jsonStr + '}')
    cntFile.close


RUN_SNAPSHOT = 'run-snapshot'
tarCmd = ""
def main(mdrConf):
    seconds = 1
    exitCmd = None
    if RUN_SNAPSHOT in mdrConf:
        runConf = mdrConf[RUN_SNAPSHOT]
        if 'exit' in runConf:
            exitCmd = runConf['exit']
        if 'sleep' in runConf:
            seconds = runConf['sleep']
        if 'daily' in runConf and runConf['daily']:
            rootFolder = mdrConf['snapshotRepository']
            dayFolder = datetime.datetime.now().strftime("%Y%m%d")
            tarCmd = "cd " + rootFolder + "; tar zcf " + dayFolder + ".tar.gz " + dayFolder
            mdrConf['snapshotRepository'] = rootFolder + '/' + dayFolder

    while(True):
        mainSnapshot(mdrConf)
        if ('daily' in runConf and runConf['daily']) or exitCmd is None:
            if runConf['daily']:
                os.system(tarCmd)   # archive daily jpgs
                shutil.rmtree(mdrConf['snapshotRepository'])    # clean jpgs
            break
        else:
            if os.path.exists(exitCmd):
                os.remove(exitCmd)
                break
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
            if cnts is not None:
                mdRecords.append((prevJpgFile, jpgFile, cnts))
        prevJpgFile = jpgFile

    if len(mdRecords) > 0:
        jpgFiles = mdrSnapshot.getSnapshotFiles()
        summary = "summary " + str(len(mdRecords)) + '/' + str(len(jpgFiles)) + "\n"
        for prevJpgFile, jpgFile, cnts in mdRecords:
            summary += jpgFile + ' contours: ' + str(len(cnts)) + '\n'

        saveSnapshotContours(mdrConf, mdRecords)
        # send mail
        if mdrConf['snapshot']['sendmail']:
            mdrConf['email']['body'] = summary
            mail(mdrConf, mdRecords)


if __name__ == "__main__":
    mdrConfJsonFile = 'mdr.json'
    if len(sys.argv) > 1:
        mdrConfJsonFile = sys.argv[1]
    mdrConf = json.load(open(mdrConfJsonFile))
    main(mdrConf)
