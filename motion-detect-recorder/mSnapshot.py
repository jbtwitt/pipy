from time import sleep
import datetime
import json
from classes.MdrMail import MdrMail

M_SNAPSHOT = 'snapshot'
def snapshot(mdrConf):
    from picamera import PiCamera
    res = mdrConf[M_SNAPSHOT]['camera']['resolution']
    camera = PiCamera()
    camera.resolution = (res[0], res[1])
    camera.start_preview()
    jpgName = filename(mdrConf)
    camera.capture(jpgName)
    camera.stop_preview()
    return jpgName


def filename(mdrConf):
    timestamp = datetime.datetime.now()
    return mdrConf['camCacheRepository'] + '/snapshot_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'


def main(mdrConf):
    frequency = int(mdrConf[M_SNAPSHOT]['frequency'])
    interval = int(mdrConf[M_SNAPSHOT]['interval'])
    jpgFiles = []
    for i in range(frequency - 1):
        jpgFiles.append(snapshot(mdrConf))
        sleep(interval)  # in second
    mdrConf['email']['body'] = 'interval:' + str(interval)
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()

if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
    # main(mdrConf)
