import os
import numpy as np
import json
import matplotlib.pyplot as plt
from HqYhoo import HqYhoo, DateFormat
from datetime import datetime, timedelta
from rdp import rdp

#
# rdp: Ramer-Douglas-Peucker Algorithm
#
CONF_FILE = 'hqrobot.json'
csvFileName = "{0}/{1}.y.csv"

def getDayFolder():
    hqConf = json.load(open(CONF_FILE))
    csvRepo = hqConf['repo'] + '/'
    files = [f for f in os.listdir(csvRepo) if os.path.isdir(csvRepo + f)]
    print(files[-1])    # last one of the array is the most recent folder
    return csvRepo + files[-1]

def download(ticker, hqDays):
    today = (datetime.now() + timedelta(days=1)).strftime(DateFormat)
    hqStartDate = (datetime.now() + timedelta(days=-hqDays)).strftime(DateFormat)
    print(ticker, ": date range", hqStartDate, today)
    hqRobot = HqYhoo()
    csv = hqRobot.hqGet(ticker, hqStartDate, today)
    return csv.decode("utf-8")

def csv2Array(csv):
    hq = []
    lines = csv.replace(",-", ",0").split("\n")  # replace missing number
    for idx, line in enumerate(lines[1:]):  # skip header row
        if len(line) == 0:
            break
        cols = line.split(',')
        hq.append(cols[1:]) # skip date column
    return hq

def csvInput(ticker, hqRepo):
    csvFile = open(csvFileName.format(hqRepo, ticker), "r")
    txt = csvFile.read()
    csvFile.close()
    return csv2Array(txt)

def grouper(rdpList, delta=0.01):
    sortArr = sorted(rdpList, key=lambda item: item[1])
    # sortArr = np.sort(arr, axis=0)
    # sortArr = np.sort(rdpPoints[:, 1])
    # print(sortArr)
    prev = None
    group = []
    avgList = []
    for item in sortArr:
        if not prev or (item[1] - prev[1]) / prev[1] <= delta:
            group.append(item)
        else:
            if len(group) > 1:
                avgList.append(np.average(group, axis=0)[1])
            print(sorted(group, key=lambda item: item[0]))
            # print(np.average(group, axis=0)[1])
            group = [item]
        prev = item
    if group:
        if len(group) > 1:
            avgList.append(np.average(group, axis=0)[1])
        print(group)
    return avgList

def plot(ticker, hqDays=90):
    hqRepo = getDayFolder()
    hq = csvInput(ticker, hqRepo)

    shift_left = 0  # this shifts the window (size of hqDays) to left
    offset = len(hq) - hqDays - shift_left
    hq = np.array(hq[offset: offset + hqDays])
    # print(hq)
    closeHist = hq[:, 3].astype(np.float)   # close history
    # print(closeHist)
    latestClose = closeHist[-1]
    dayIdxs = range(len(closeHist))

    """
    RDP markers
    """
    to2dim = np.vstack((dayIdxs, closeHist)).T
    delta = max(closeHist) - min(closeHist)

    '''
    hq chart
    ro: red, yo: yellow
    ko: black, bo: blue
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(dayIdxs, closeHist)
    # ax.plot(range(len(closeCol)), list(reversed(closeCol)), 'g')    # green
    # ax.plot(range(len(closeCol)), closeCol, 'ko', markersize = 5, label='turning points')   # black

    # epsilon = delta / 4
    # # epsilon = min(closeHist) * 0.1  # determine epsilon
    # rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    # # print(rdpPoints)
    # ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ro', markersize=7, label="(epsilon:%.1f%%)" % (100*epsilon/latestClose))

    # epsilon = delta / 2
    epsilon = latestClose * .1
    rdpList = rdp(to2dim.tolist(), epsilon)
    rdpPoints = np.array(rdpList)
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=4, label="(epsilon:%.1f%%)" % (100*epsilon/latestClose))

    # group
    # print(sorted(rdpList, key=lambda item: item[1]))
    groupAvgList = grouper(rdpList)
    # print(groupAvgList)
    for avg in groupAvgList:
        ax.plot((0, len(closeHist)), (avg, avg), 'r', label="%.2f" % avg)
    # return

    fig.suptitle("%s %s %d days" % (hqRepo, ticker, hqDays))
    plt.legend(loc='best')

    # print(rdpPoints)
    # print(rdpPoints.shape)
    plt.show()

import argparse
if __name__ == "__main__":
    # numbers = [123, 124, 128, 160, 167, 213, 215, 230, 245, 255, 257, 400, 401, 402, 430]
    # print(dict(enumerate(grouper(numbers), 1)))
    parser = argparse.ArgumentParser()
    parser.add_argument('tickers', metavar='tickers', type=str, nargs='+', help='ticker list')
    # parser.add_argument('-ticker', help='ticker')
    args = parser.parse_args()
    # print(vars(args)[''])
    print(args.tickers)
    for ticker in args.tickers:
        plot(ticker.upper(), hqDays=192)
