import os
import cv2
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
        self.grayColor = False
        if 'grayColor' in mdrConf[M_SNAPSHOT]['camera']:
            self.grayColor = mdrConf[M_SNAPSHOT]['camera']['grayColor']


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
            if self.grayColor == True:
                camera.color_effects = (128, 128)
            camera.start_preview()
            camera.capture(jpgName)
            camera.stop_preview()
            if self.grayColor == True:
                im = cv2.imread(jpgName)
                im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                cv2.imwrite(jpgName, im)
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
    import json
    mdrConf = json.load(open('../mdr.json'))
    mdrSnapshot = MdrSnapshot(mdrConf)
    print mdrSnapshot.repository