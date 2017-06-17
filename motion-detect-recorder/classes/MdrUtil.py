import cv2
import numpy as np
from MotionDetect import CMotionDetect

def arrs2Contours(arrs):
    contours = []
    for arr in arrs:
        contours.append(np.array(arr))
    return contours


def contours2ArrsStr(cnts):
    arrsStr = '['
    for idx, cnt in enumerate(cnts):
        cntStr = '['
        for i, item in enumerate(cnt):
            if i == 0:
                cntStr += np.array2string(item, separator=',')
            else:
                cntStr += ',' + np.array2string(item, separator=',')
        if idx == 0:
            arrsStr += cntStr.replace(' ','') + ']'
        else:
            arrsStr += ',' + cntStr + ']'
    arrsStr += ']'
    return arrsStr

def diff2JpgFiles(jpg1, jpg2):
    im = cv2.imread(jpg1)
    cMotion = CMotionDetect(im, alpha=0.4)
    # motion detect
    im = cv2.imread(jpg2)
    cnts = cMotion.update(im)
    return cnts


def findContoursCenters(cnts):
    centers = []
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        centers.append([cX, cY])
    return centers


if __name__ == "__main__":
    import os
    dir = '/tmp/snapshot/'
    jpgFiles = os.listdir(dir)
    print jpgFiles

    import json
    for i in range(2):
        cnts = diff2JpgFiles(dir + jpgFiles[i], dir + jpgFiles[i + 1])
        if len(cnts) > 0:
            im = cv2.imread(dir + jpgFiles[i + 1])
            cv2.drawContours(im, cnts, -1, (0,155,0), 1)
            centers = findContoursCenters(cnts)
            for c in centers:
                cv2.circle(im, (c[0], c[1]), 3, (255, 255, 255), -1)
            cv2.imwrite('/tmp/test_' + str(i) + '.jpg', im)
            print 'contours: ' + str(len(cnts))
            # test contours to string
            jsonStr = '{"cnts":' + contours2ArrsStr(cnts) + '}'
            jsonObj = json.loads(jsonStr)
            im = cv2.imread(dir + jpgFiles[i + 1])
            cv2.drawContours(im, arrs2Contours(jsonObj['cnts']), -1, (0,155,0), 1)
            cv2.imwrite('/tmp/test_' + str(i) + str(i) + '.jpg', im)
