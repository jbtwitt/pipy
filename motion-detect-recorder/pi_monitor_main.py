import os
from datetime import datetime
from time import sleep
from picamera import PiCamera

REPOS = "/tmp/pi-monitor"
RECYCLE_DAYS = 3
CAMERA_RESOLUTION = [800, 608]

def createFolder():
    for i in range(RECYCLE_DAYS):
        dir = "%s/%d" % (REPOS, i)
        if not os.path.exists(dir):
            os.makedirs(dir)

def getPath(tm=datetime.now(), extName='jpg'):
    return "%s/%d/%s.%s" % (REPOS, (tm.timetuple().tm_yday % RECYCLE_DAYS), tm.strftime("%H%M%S"), extName)

def cameraShot():
    camera = PiCamera()
    try:
        camera.resolution = CAMERA_RESOLUTION
        # warming
        camera.start_preview()
        jpgName = getPath()
        camera.capture(jpgName)
        camera.stop_preview()

        while True:
            sleep(2)
            jpgName = getPath()
            camera.capture(jpgName)
    finally:
        camera.close()

def main():
    createFolder()
    cameraShot()

if __name__ == "__main__":
    main()