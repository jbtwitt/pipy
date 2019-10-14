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
    sortedList = sorted(rdpList, key=lambda item: item[1])
    # sortArr = np.sort(arr, axis=0)
    # sortArr = np.sort(rdpPoints[:, 1])
    # print(sortArr)
    prev = []   #None
    group = []
    avgList = []
    for item in sortedList:
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

class HqDetail:
    def __init__(self, ticker):
        self.ticker = ticker
        self.init()

    def init(self, hqDays=192):
        hqRepo = getDayFolder()
        hq = csvInput(ticker, hqRepo)
        print(len(hq))
        shift_left = 0  # this shifts the window (size of hqDays) to left
        offset = len(hq) - hqDays - shift_left
        hq = np.array(hq[offset: offset + hqDays])
        # print(hq)
        self.volHist = hq[:, 5].astype(np.int)   # volume history
        self.closeHist = hq[:, 3].astype(np.float)   # close history
        # dayIdxs = range(len(closeHist))
        # to2dim = np.vstack((dayIdxs, self.CHist)).T
        # epsilon = self.lastC * .1
        # rdpList = rdp(to2dim.tolist(), epsilon)
        """
        RDP points
        """
        self._epsilon = self.lastC * .1
        self.hqRdp = rdp(np.vstack((range(len(self.CHist)), self.CHist)).T.tolist(), self._epsilon)
        self.rdpGroups, self.rdpGroupAvgs = self.groupHqRdp()
        print(self.rdpGroups)
        print(self.rdpGroupAvgs)
        # print(closeHist)
        # print(self.myRdp)
        # print(self.VHist[:6])

    def groupHqRdp(self, delta=0.01):
        avgList = []
        groupList = []
        prev = []   #None
        group = []
        sortedList = sorted(self.rdpList, key=lambda item: item[1])
        for item in sortedList:
            if not prev or (item[1] - prev[1]) / prev[1] <= delta:
                group.append(item)
            else:
                if len(group) > 1:
                    avgList.append(np.average(group, axis=0)[1])
                groupList.append(sorted(group, key=lambda item: item[0]))
                group = [item]
            prev = item
        if group:
            if len(group) > 1:
                avgList.append(np.average(group, axis=0)[1])
            groupList.append(sorted(group, key=lambda item: item[0]))
        return (groupList, avgList)

    @property
    def hqRdpGroups(self):
        return self.rdpGroups, self.rdpGroupAvgs
    @property
    def epsilon(self):
        return self._epsilon
    @property
    def rdpList(self):
        return self.hqRdp
    @property
    def lastC(self):
        return self.closeHist[-1]
    @property
    def CHist(self):
        return self.closeHist
    @property
    def VHist(self):
        return self.volHist

def plot(ticker, hqDays=90):
    # hqRepo = getDayFolder()
    # hq = csvInput(ticker, hqRepo)

    # shift_left = 0  # this shifts the window (size of hqDays) to left
    # offset = len(hq) - hqDays - shift_left
    # hq = np.array(hq[offset: offset + hqDays])
    # # print(hq)
    # closeHist = hq[:, 3].astype(np.float)   # close history
    # # print(closeHist)
    # latestClose = closeHist[-1]
    # dayIdxs = range(len(closeHist))

    """
    RDP markers
    """
    # to2dim = np.vstack((dayIdxs, closeHist)).T
    # delta = max(closeHist) - min(closeHist)

    hqDetail = HqDetail(ticker)
    '''
    hq chart
    ro: red, yo: yellow
    ko: black, bo: blue
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(range(len(hqDetail.CHist)), hqDetail.CHist)
    # ax.plot(range(len(closeCol)), list(reversed(closeCol)), 'g')    # green
    # ax.plot(range(len(closeCol)), closeCol, 'ko', markersize = 5, label='turning points')   # black

    # epsilon = delta / 4
    # # epsilon = min(closeHist) * 0.1  # determine epsilon
    # rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    # # print(rdpPoints)
    # ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ro', markersize=7, label="(epsilon:%.1f%%)" % (100*epsilon/latestClose))

    # epsilon = delta / 2
    # epsilon = latestClose * .1
    # rdpList = rdp(to2dim.tolist(), epsilon)
    rdpList = hqDetail.rdpList
    rdpPoints = np.array(rdpList)
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=4, label="(epsilon:%.1f%%)" % (100*hqDetail.epsilon/hqDetail.lastC))

    # group
    # print(sorted(rdpList, key=lambda item: item[1]))
    # groupAvgList = grouper(rdpList)
    hqRdpGroup, groupAvgList = hqDetail.hqRdpGroups
    # print(groupAvgList)
    for avg in groupAvgList:
        ax.plot((0, len(hqDetail.CHist)), (avg, avg), 'r', label="%.2f" % avg)
    # return

    fig.suptitle("%s %d days" % (ticker, hqDays))
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
