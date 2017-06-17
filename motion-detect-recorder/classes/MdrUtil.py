import numpy as np

class MdrUtil:
    def countours2ArrStr(cnts):
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


    def arr2Contours(arr):
        contours = []
        for a in arr:
            contours.append(np.array(a))
        return contours
