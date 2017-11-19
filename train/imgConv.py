from PIL import Image, ImageFilter  # imports the library
import numpy as np
import os
import sys

# blurred = original.filter(ImageFilter.BLUR) # blur the image
# blurred.show()

def imgResizeGray(folder, imgName, resizeWidth=100):
    # """ resize & gray
    original = Image.open(folder + imgName)
    # print(original.size)
    resize = resizeWidth, int(original.size[1]*resizeWidth/original.size[0])
    # print(resize)
    original.thumbnail(resize, Image.ANTIALIAS)
    gray = original.convert('L')
    gray.save("%s_resizeW%d_%s" % (folder, resizeWidth, imgName))
    # gray.show()
    # """

def main(imgFolder):
    jpgFiles = os.listdir(imgFolder)
    # print(jpgFiles)
    for jpg in jpgFiles:
        imgResizeGray(imgFolder, jpg)
        print("resize done", jpg)


if __name__ == "__main__":
    imgFolder = '/pirepo/train/not-empty/'
    if len(sys.argv) > 1:
        imgFolder = sys.argv[1]
    main(imgFolder)