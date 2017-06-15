import os
import datetime
from picamera import PiCamera

M_SNAPSHOT = 'snapshot'
class MdrSnapshot:
    def __init__(self, mdrConf):
        self.mdrConf = mdrConf
        self.repository = mdrConf['snapshotRepository']
        self.snapshotFiles = []
        if not os.path.exists(self.repository):
            os.makedirs(self.repository)
        else:
            self.cleanRepository()


    def snapshotFilename(self):
        timestamp = datetime.datetime.now()
        return self.repository + '/at_' + timestamp.strftime("%Y%m%d_%H%M%S_%f") + '.jpg'


    def getSnapshotFiles(self):
        return self.snapshotFiles


    def delSnapshotFiles(self):
        for f in self.snapshotFiles:
            os.remove(f)


    def cleanRepository(self):
        snapshotFiles = os.listdir(self.repository)
        for f in snapshotFiles:
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
    mdrConf = json.load(open('../mdr.json'))
    mdrSnapshot = MdrSnapshot(mdrConf)