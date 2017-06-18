import os
import datetime
from picamera import PiCamera
import MdrUtil as MdrUtil

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
        self.mdArea = None
        if 'mdArea' in mdrConf['snapshot']:
            self.mdArea = mdrConf[M_SNAPSHOT]['mdArea']
        res = mdrConf[M_SNAPSHOT]['camera']['resolution']
        self.resolution = (res[0], res[1])


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
            os.remove(self.repository + '/' + f)


    def cameraSnapshot(self):
        """Snapshot: init camera, take a picture and close camera
        """
        camera = PiCamera()
        jpgName = self.snapshotFilename()
        try:
            camera.resolution = self.resolution
            camera.start_preview()
            camera.capture(jpgName)
            camera.stop_preview()
            if not self.mdArea == None:
                im = cv2.imread(jpgName)
                im = MdrUtil.cropArea(im, self.mdArea)
                cv2.imwrite(jpgName, im)
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