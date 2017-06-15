import os
import datetime
from picamera import PiCamera

M_SNAPSHOT = 'snapshot'
class MdrSnapshot:
    def __init__(self, mdrConf):
        self.mdrConf = mdrConf
        self.snapshotFiles = []


    def snapshotFilename(self):
        timestamp = datetime.datetime.now()
        return self.mdrConf['camCacheRepository'] + '/snapshot_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'


    def getSnapshotFiles():
        return self.snapshotFiles


    def delSnapshotFiles(files):
        for f in self.snapshotFiles:
            os.remove(f)


    def cameraSnapshot(self):
        """Snapshot: init camera, take a picture and close camera
        """
        camera = PiCamera()
        jpgName = self.snapshotFilename()
        resolution = self.mdrConf[M_SNAPSHOT]['camera']['resolution']
        try:
            camera.resolution = (resolution[0], resolution[1])
            camera.start_preview()
            camera.capture(jpgName)
            camera.stop_preview()
            self.snapshotFiles.append(jpgName)
        finally:
            camera.close()
        return jpgName


    def freeSpace(dir='/'):
        fs = os.statvfs(dir)
        return (fs.f_bavail * fs.f_frsize) / 1024


if __name__ == "__main__":
    # from MdrUtil import freeSpace
    # print freeSpace()
    print os.listdir('.')
