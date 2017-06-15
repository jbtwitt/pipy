from time import sleep
import datetime
import json
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
    main(mdrConf)
