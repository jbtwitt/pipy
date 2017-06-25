import cv2
import numpy as np
from MotionDetect import CMotionDetect
from skimage.measure import compare_ssim

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


def cropArea(im, mdArea):
    x1 = mdArea[0]
    y1 = mdArea[1]
    x2 = mdArea[2]
    y2 = mdArea[3]
    return im[y1:y2, x1:x2]


def imgCompareContourArea(imSrc, imTgt, cnt):
    x,y,w,h = cv2.boundingRect(cnt)
    if w > 7 and h > 7:
        # somehow compare_ssim throw error if w or h are small
        moments = cv2.moments(cnt)
        cntArea = moments["m00"]
        src = cropArea(imSrc, [x, y, x+w, y+h])
        tgt = cropArea(imTgt, [x, y, x+w, y+h])
        (score, diff) = compare_ssim(src, tgt, multichannel=True, full=True)
        return (score, cntArea / w * h)
    return (None, None)


def imgCompareFound(imSrc, imTgt, cnts):
    for cnt in cnts:
        score, cntAreaRatio = imgCompareContourArea(imSrc, imTgt, cnt)
        # if score < area ratio, object movement found
        if score is not None and score < (1 - cntAreaRatio):
            return True
    return False


def diff2JpgFiles(jpg1, jpg2):
    im1 = cv2.imread(jpg1)
    cMotion = CMotionDetect(im1, alpha=0.4)
    # motion detect
    im2 = cv2.imread(jpg2)
    cnts = cMotion.update(im2)
    if len(cnts) > 0:
        if imgCompareFound(im1, im2, cnts):
            return cnts
    return None


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
