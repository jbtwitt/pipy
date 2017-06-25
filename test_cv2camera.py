import numpy as np
import cv2
from skimage.measure import compare_ssim

def arrs2Contours(arrs):
    contours = []
    for arr in arrs:
        contours.append(np.array(arr))
    return contours


def cropArea(im, mdArea):
    x1 = mdArea[0]
    y1 = mdArea[1]
    x2 = mdArea[2]
    y2 = mdArea[3]
    return im[y1:y2, x1:x2]


def compare(imSrc, imTgt, mdCnts):
    for cnts in mdCnts:
        x,y,w,h = cv2.boundingRect(cnts)
        srcImg = cropArea(imSrc, [x, y, x+w, y+h])
        tgtImg = cropArea(imTgt, [x, y, x+w, y+h])

        # convert the images to grayscale
        grayA = cv2.cvtColor(srcImg, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(tgtImg, cv2.COLOR_BGR2GRAY)

        # compute the Structural Similarity Index (SSIM) between the two
        # images, ensuring that the difference image is returned
        (score, diff) = compare_ssim(grayA, grayB, full=True)
        # diff = (diff * 255).astype("uint8")
        print "SSIM: {}".format(score)


def compareContourArea(imSrc, imTgt, cnts):
    x,y,w,h = cv2.boundingRect(cnts)
    if w > 9 or h > 9:
        # somehow compare_ssim throw error if w or h are small
        srcImg = cropArea(imSrc, [x, y, x+w, y+h])
        tgtImg = cropArea(imTgt, [x, y, x+w, y+h])
        (score, diff) = compare_ssim(srcImg, tgtImg, multichannel=True, full=True)

    # convert the images to grayscale
    # grayA = cv2.cvtColor(srcImg, cv2.COLOR_BGR2GRAY)
    # grayB = cv2.cvtColor(tgtImg, cv2.COLOR_BGR2GRAY)
    # (score, diff) = compare_ssim(grayA, grayB, full=True)
    return score


def testContours():
    import glob
    import json
    win = 'snapshot'
    cv2.namedWindow(win, flags=cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(win, 5, 45)
    dir = '/tmp/snapshot/'
    jsonFiles = glob.glob(dir + '*.json')
    contours = json.load(open(jsonFiles[0]))
    print 'mdRecords: ' + str(len(contours))
    idxs = contours.keys()
    for idx in idxs:
        im = cv2.imread(idx)
        imPrev = cv2.imread(contours[idx]['snapshot'])
        snapshotCnts = arrs2Contours(contours[idx]['contours'])
        print "prev snapshot:" + contours[idx]['snapshot']
        print "snapshot jpg: " + idx
        print "contours: " + str(len(snapshotCnts))
        for cnts in snapshotCnts:
            moments = cv2.moments(cnts)
            area = moments["m00"]
            if area > 0:
                cX = int(moments["m10"] / area)
                cY = int(moments["m01"] / area)
                cv2.circle(im, (cX, cY), 3, (255, 255, 255), -1)
                score = compareContourArea(imPrev, im, cnts)
                print "\tcontour area/center: " + str(area) + " / (" + str(cX) + ', ' + str(cY) + ')' + ' / score - ' + str(score)
            x,y,w,h = cv2.boundingRect(cnts)
            cv2.rectangle(im, (x, y), (x+w, y+h), (0,0,155), 1)

        cv2.drawContours(im, snapshotCnts, -1, (0,155,0), 1)
        cv2.imshow(win, im)


        while(True):
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

def testSnapshot():
    import os
    import classes.MdrUtil as MdrUtil
    dir = '/tmp/snapshot/'
    jpgFiles = os.listdir(dir)
    for i in range(2):
        cnts = MdrUtil.diff2JpgFiles(dir + jpgFiles[i], dir + jpgFiles[i + 1])
        if len(cnts) > 0:
            im = cv2.imread(dir + jpgFiles[i + 1])
            cv2.drawContours(im, cnts, -1, (0,155,0), 1)
            centers = MdrUtil.findContoursCenters(cnts)
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


def testCV2Camera():
    cap = cv2.VideoCapture(0)
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        # cv2.imshow('frame',gray)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    testContours()
    # import motion-detect-recorder.classes.MdrUtil
    # mdrConfJsonFile = 'mdr.json'
    # mdrConf = json.load(open(mdrConfJsonFile))
