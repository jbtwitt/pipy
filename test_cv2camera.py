import numpy as np
import cv2

def arrs2Contours(arrs):
    contours = []
    for arr in arrs:
        contours.append(np.array(arr))
    return contours


def testContours():
    import glob
    import json
    dir = '/tmp/snapshot/'
    jsonFiles = glob.glob(dir + '*.json')
    contours = json.load(open(jsonFiles[0]))
    idxs = contours.keys()
    for idx in idxs:
        snapshotCnts = arrs2Contours(contours[idx])
        for cnts in snapshotCnts:
            moments = cv2.moments(cnts)
            cX = int(moments["m10"] / moments["m00"])
            cY = int(moments["m01"] / moments["m00"])
            print "snapshot jpg:" + idx
            print "contour center: " + str(cX) + ', ' + str(cY)
            print "contour area: " + str(moments['m00'])

        im = cv2.imread(idx)
        cv2.drawContours(im, cnts, -1, (0,155,0), 1)
        cv2.imshow('frame', im)
        while(True):
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

def testSnapshot():
    import os
    dir = '/tmp/snapshot/'
    jpgFiles = os.listdir(dir)
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
