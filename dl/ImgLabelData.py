from PIL import Image, ImageFilter
import numpy as np
import glob
from workspace import Workspace

def imgResize2Array(jpg, resizeWidth):
    original = Image.open(jpg)

    resize = resizeWidth, int(original.size[1]*resizeWidth/original.size[0])
    # print(resize)
    original.thumbnail(resize, Image.ANTIALIAS)

    imgArray = np.asarray(original).flatten()
    # print(imgArray.shape)
    imgArray = imgArray / 255   # encode
    # print(imgArray[:100])
    # imgArray = imgArray * 255 # decode
    # print(imgArray[0])
    return imgArray

def img2Array(jpg):
    original = Image.open(jpg)
    imgArray = np.asarray(original).flatten()
    # print(imgArray.shape)
    imgArray = imgArray / 255   # encode
    # print(imgArray[:100])
    # imgArray = imgArray * 255 # decode
    # print(imgArray[0])
    return imgArray

class ImgLabelData:
    def __init__(self, workspace):
        self.workspace = workspace
        np.random.seed(7)
        self.train = self.jpg2Array(self.workspace)
        # print(self.train)
        print('jpgs labels:', self.train.shape)
        self.batchPointer = 0

    def nextBatch(self, batchSize=1, resizeWidth=100):
        images = []
        labels = []
        for i in range(batchSize):
            jpg = self.train[self.batchPointer][0]
            label = self.train[self.batchPointer][1:].astype(float)
            images.append(imgResize2Array(jpg, resizeWidth))
            labels.append(label)
            self.batchPointer = self.batchPointer + 1
            if self.batchPointer >= len(self.train):
                self.batchPointer = 0
        return np.array(images), np.array(labels)

    def jpg2Array(self, workspace):
        labels = workspace.getLabels()
        labelsLen = len(workspace.getLabels())
        arr = np.empty((0, labelsLen+1), dtype=object)
        for i in range(labelsLen):
            learnLabelStore = workspace.getLearnLabelStore(i)
            jpgs = glob.glob(learnLabelStore + '/*.jpg')
            # label array with extra column for jpg file
            vecs = np.empty((len(jpgs), labelsLen+1), dtype=object)
            vecs[:,] = "0"
            vecs[:,i+1] = "1"
            vecs[:, 0] = jpgs
            # print(vecs, vecs.shape)
            arr = np.concatenate((arr, vecs))
        np.random.shuffle(arr)
        return arr

if __name__ == "__main__":
    labels = ['car-brother', 'car-vivian', 'empty', 'others']
    ws = Workspace('nono-parking-lot', labels)
    labelImgData = ImgLabelData(ws)
    print(labelImgData.nextBatch(batchSize=2, resizeWidth=88))
