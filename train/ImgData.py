from PIL import Image, ImageFilter
import numpy as np
import glob

class ImgData:
    def __init__(self, emptyFolder, notEmptyFolder):
        np.random.seed(7)
        self.train = self.jpg2Array(emptyFolder, notEmptyFolder)
        print(self.train)
        print(self.train.shape)
        self.img2Array(self.train[0])

    def jpg2Array(self, emptyFolder, notEmptyFolder):
        emptyJpgs = glob.glob(emptyFolder + '*.jpg')
        emptyJpgs = np.array([emptyJpgs, np.zeros(len(emptyJpgs))]).T
        notEmptyJpgs = glob.glob(notEmptyFolder + '*.jpg')
        notEmptyJpgs = np.array([notEmptyJpgs, np.ones(len(notEmptyJpgs))]).T
        arr = np.concatenate((emptyJpgs, notEmptyJpgs))
        np.random.shuffle(arr)
        return arr

    def img2Array(self, jpg):
        original = Image.open(jpg[0])
        imgArray = np.asarray(original).flatten()
        print(imgArray.shape)
        imgArray = imgArray / 255   # encode
        print(imgArray[:100])
        # imgArray = imgArray * 255 # decode
        # print(imgArray[0])

if __name__ == "__main__":
    emptyFolder = '/pirepo/train/empty/ResizeW100/'
    notEmptyFolder = '/pirepo/train/not-empty/ResizeW100/'
    trainData = ImgData(emptyFolder, notEmptyFolder)
    emptyFolder = '/pirepo/test/empty/ResizeW100/'
    notEmptyFolder = '/pirepo/test/not-empty/ResizeW100/'
    testData = ImgData(emptyFolder, notEmptyFolder)
