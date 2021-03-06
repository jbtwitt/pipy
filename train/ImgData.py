from PIL import Image, ImageFilter
import numpy as np
import glob

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

class ImgData:
    def __init__(self, emptyFolder, notEmptyFolder):
        np.random.seed(7)
        self.train = self.jpg2Array(emptyFolder, notEmptyFolder)
        # print(self.train)
        print('jpgs labels:', self.train.shape)
        self.batchPointer = 0

    def nextBatch(self, batchSize=1, resizeWidth=100):
        images = []
        labels = []
        for i in range(batchSize):
            jpg = self.train[self.batchPointer][0]
            label = [float(self.train[self.batchPointer][1]), float(self.train[self.batchPointer][2])]
            images.append(imgResize2Array(jpg, resizeWidth))
            labels.append(label)
            self.batchPointer = self.batchPointer + 1
            if self.batchPointer >= len(self.train):
                self.batchPointer = 0
        return np.array(images), np.array(labels)

    def jpg2Array(self, emptyFolder, notEmptyFolder):
        # 2 column labels: first one: empty, second: not empty
        emptyJpgs = glob.glob(emptyFolder + '*.jpg')
        emptyJpgs = np.array([emptyJpgs, np.ones(len(emptyJpgs)), np.zeros(len(emptyJpgs))]).T
        notEmptyJpgs = glob.glob(notEmptyFolder + '*.jpg')
        notEmptyJpgs = np.array([notEmptyJpgs, np.zeros(len(notEmptyJpgs)), np.ones(len(notEmptyJpgs))]).T
        arr = np.concatenate((emptyJpgs, notEmptyJpgs))
        np.random.shuffle(arr)
        return arr

if __name__ == "__main__":
    # emptyFolder = '/pirepo/train/empty/ResizeW100/'
    # notEmptyFolder = '/pirepo/train/not-empty/ResizeW100/'
    # trainData = ImgData(emptyFolder, notEmptyFolder)

    emptyFolder = '/pirepo/test/empty/ResizeW100/'
    notEmptyFolder = '/pirepo/test/not-empty/ResizeW100/'
    testData = ImgData(emptyFolder, notEmptyFolder)
    for i in range(2):
        batch = testData.nextBatch()
        print(batch[0].shape)
        print(batch[1].shape)
        print(batch[0][:10], batch[1])

    applyStore = '/pirepo/garage/apply/'
    jpgs = glob.glob(applyStore + '*.jpg')
    imgArray = img2Array(jpgs[0])
    print(imgArray.shape)
    print(imgArray[:10])

    imgArray = imgResize2Array(jpgs[0], resizeWidth=100)
    print(imgArray.shape)
    print(imgArray[:10])
