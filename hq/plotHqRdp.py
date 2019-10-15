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
        """
        HQ 1d array
        """
        # self.volHist = hq[:, 5].astype(np.int)   # volume history
        # print(self.VHist[:6])
        self._CHist = hq[:, 3].astype(np.float)   # close history
        cIdxHist = np.vstack((range(len(self.CHist)), self.CHist)).T.tolist()
        # dayIdxs = range(len(closeHist))
        # to2dim = np.vstack((dayIdxs, self.CHist)).T
        # epsilon = self.lastC * .1
        # rdpList = rdp(to2dim.tolist(), epsilon)
        """
        RDP data
        """
        self.hqEpsilon = self.lastC * .07
        self.hqRdp = rdp(cIdxHist, self.hqEpsilon)
        self.rdpGroups, self.rdpGroupAvgs = self.hqGrouping(self.hqRdp)
        print(self.rdpGroups, self.rdpGroupAvgs)
        # print(self.hqRdp)
        self._lastNGroups, self._lastNGroupAvgs = self.hqGrouping(rdp(cIdxHist[len(cIdxHist) - self.lastN:], self.hqEpsilon/2))
        print(self._lastNGroups, self._lastNGroupAvgs)

    def hqGrouping(self, hqList, delta=0.01):
        avgList = []
        groupList = []
        prev = []   #None
        group = []
        sortedList = sorted(hqList, key=lambda item: item[1])
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
    def lastN(self):
        return 20
    @property
    def lastNGroups(self):
        return self._lastNGroups, self._lastNGroupAvgs
    @property
    def rdpData(self):
        return self.hqRdp, self.hqEpsilon
    @property
    def lastC(self):
        return self._CHist[-1]
    @property
    def CHist(self):
        return self._CHist
    # @property
    # def VHist(self):
    #     return self.volHist

def plot(ticker, hqDays=90):

    hqDetail = HqDetail(ticker)
    '''
    chart color
    ro: red, yo: yellow
    ko: black, bo: blue
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    """
    hq line chart
    """
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
    """
    RDP markers
    """
    rdpList, epsilon = hqDetail.rdpData
    rdpPoints = np.array(rdpList)
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=4, label="epsilon:%.1f%%" % (100*epsilon/hqDetail.lastC))
    """
    RDP group and average
    """
    g, groupAvgList = hqDetail.hqRdpGroups
    for avg in groupAvgList:
        ax.plot((0, len(hqDetail.CHist)), (avg, avg), 'r', label="%.2f %.1f%%" % (avg, 100*(hqDetail.lastC-avg)/hqDetail.lastC))

    g, lastNAvgList = hqDetail.lastNGroups
    for avg in lastNAvgList:
        ax.plot((len(hqDetail.CHist) - hqDetail.lastN, len(hqDetail.CHist)), (avg, avg), 'g', label="%.2f %.1f%%" % (avg, 100*(hqDetail.lastC-avg)/hqDetail.lastC))

    fig.suptitle("%s %.2f %d days" % (ticker, hqDetail.lastC, hqDays))
    plt.legend(loc='best')

    # print(rdpPoints)
    # print(rdpPoints.shape)
    plt.show()

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('tickers', metavar='tickers', type=str, nargs='+', help='ticker list')
    # parser.add_argument('-ticker', help='ticker')
    args = parser.parse_args()
    # print(vars(args)[''])
    print(args.tickers)
    for ticker in args.tickers:
        plot(ticker.upper(), hqDays=192)
