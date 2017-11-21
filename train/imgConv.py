from PIL import Image, ImageFilter  # imports the library
import numpy as np
import os
import glob
import sys

# blurred = original.filter(ImageFilter.BLUR) # blur the image
# blurred.show()

def getResizeFolder(folder, resizeWidth):
    outputFolder = "%sResizeW%d/" % (folder, resizeWidth)
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    return outputFolder
    
def imgResizeGray(folder, imgName, resizeWidth=100):
    # """ resize & gray
    outputFolder = getResizeFolder(folder, resizeWidth)
    original = Image.open(folder + imgName)
    # print(original.size)
    resize = resizeWidth, int(original.size[1]*resizeWidth/original.size[0])
    # print(resize)
    original.thumbnail(resize, Image.ANTIALIAS)
    gray = original.convert('L')
    gray.save("%sresizeW%d_%s" % (outputFolder, resizeWidth, imgName))
    # gray.show()
    # """

def main(imgFolder):
    # jpgFiles = os.listdir(imgFolder)
    jpgFiles = glob.glob(imgFolder + '*.jpg')
    # print(jpgFiles)
    for jpg in jpgFiles:
        folder, filename = os.path.split(jpg)
        # print(folder, filename)
        imgResizeGray(folder + '/', filename)
        print("resize done", jpg)


if __name__ == "__main__":
    imgFolder = '/pirepo/train/not-empty/'
    if len(sys.argv) > 1:
        imgFolder = sys.argv[1]
    main(imgFolder)
    