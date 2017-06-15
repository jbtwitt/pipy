from time import sleep
import datetime
import json
import cv2
from classes.MdrMail import MdrMail

M_SNAPSHOT = 'snapshot'
def snapshot(mdrConf):
    from picamera import PiCamera
    res = mdrConf[M_SNAPSHOT]['camera']['resolution']
    jpgName = filename(mdrConf)
    camera = PiCamera()
    try:
        camera.resolution = (res[0], res[1])
        camera.start_preview()
        camera.capture(jpgName)
        camera.stop_preview()
    finally:
        camera.close()
    return jpgName


def filename(mdrConf):
    timestamp = datetime.datetime.now()
    return mdrConf['camCacheRepository'] + '/snapshot_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'


def mail(mdrConf, jpgFiles):
    mdrConf['email']['body'] = 'interval:' + str(mdrConf[M_SNAPSHOT]['frequency'])
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()


def mdrMain(mdrConf):
    from classes.MotionDetect import CMotionDetect
    jpgFiles = []
    # motion detect
    jpgFile = snapshot(mdrConf)
    im = cv2.imread(jpgFile)
    cMotion = CMotionDetect(im, alpha=0.4)

    jpgFiles.append(jpgFile)

    frequency = mdrConf[M_SNAPSHOT]['frequency'] - 1
    interval = mdrConf[M_SNAPSHOT]['interval']
    for i in range(frequency):
        sleep(interval)  # in second
        # motion detect
        jpgFile = snapshot(mdrConf)
        im = cv2.imread(jpgFile)
        cnts = cMotion.update(im)

        jpgFiles.append(jpgFile)
        if len(cnts) > 0:
            print 'md found ...'
            # nparr = []
            # for a in cnts:
            #     nparr.append(np.array(a))
            cv2.drawContours(im, cnts, -1, (0,155,0), 1)
            cv2.imwrite(jpgFile)

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
