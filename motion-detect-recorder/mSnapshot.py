from time import sleep
import datetime
import json
from classes.MdrMail import MdrMail

def snapshot(mdrConf):
    from picamera import PiCamera
    res = mdrConf['camera']['resolution']
    camera = PiCamera()
    camera.resolution = (res[0], res[1])
    camera.start_preview()
    # sleep(5)
    jpgName = filename(mdrConf)
    camera.capture(jpgName)
    camera.stop_preview()
    return jpgName


def filename(mdrConf):
    timestamp = datetime.datetime.now()
    return mdrConf['camCacheRepository'] + '/snapshot_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'


def main(mdrConf):
    jpgFiles = []
    jpgFiles.append(snapshot(mdrConf))
    mdrMail = MdrMail(mdrConf)
    mdrMail.attachImages(jpgFiles)
    mdrMail.send()


if __name__ == "__main__":
    mdrConf = json.load(open('mdr.json'))
    main(mdrConf)
