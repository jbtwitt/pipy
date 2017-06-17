import cv2
import numpy as np
from MotionDetect import CMotionDetect

def arrs2Contours(arrs):
    contours = []
    for arr in arrs:
        contours.append(np.array(arr))
    return contours


def countours2ArrsStr(cnts):
    # cntFile = open(path + '.json', "w")
    # cntFile.write('{"f' + mdrTs + '.jpg":[')
    arrStr = '['
    for idx, cnt in enumerate(cnts):
        cntStr = '['
        for i, item in enumerate(cnt):
            if i == 0:
                cntStr += np.array2string(item, separator=',')
            else:
                cntStr += ',' + np.array2string(item, separator=',')
        if idx == 0:
            # cntFile.write(cntStr.replace(' ','') + ']')
            arrStr += cntStr.replace(' ','') + ']'
        else:
            # cntFile.write(',' + cntStr + ']')
            arrStr += ',' + cntStr + ']'
    arrStr += ']'
    # cntFile.write(']}')
    # cntFile.close

def diff2JpgFiles(jpg1, jpg2):
    im = cv2.imread(jpg1)
    cMotion = CMotionDetect(im, alpha=0.4)
    # motion detect
    im = cv2.imread(jpg2)
    cnts = cMotion.update(im)
    return cnts


if __name__ == "__main__":
    import os
    dir = '/tmp/snapshot/'
    jpgFiles = os.listdir(dir)
    print jpgFiles
    cnts = diff2JpgFiles(dir + jpgFiles[0], dir + jpgFiles[1])
    if len(cnts) > 0:
        im = cv2.imread(dir + jpgFiles[1])
        cv2.drawContours(im, cnts, -1, (0,155,0), 1)
        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(im, (cX, cY), 3, (255, 255, 255), -1)
        cv2.imwrite('test.jpg', im)
    print countours2ArrsStr(cnts)