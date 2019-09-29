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

today = (datetime.now() + timedelta(days=1)).strftime(DateFormat)
def download(ticker, hqDays):
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

def csvInput(ticker):
    csvFile = open(csvFileName.format(getDayFolder(), ticker), "r")
    txt = csvFile.read()
    csvFile.close()
    return csv2Array(txt)

def plot(ticker, hqDays=90):
    hq = csvInput(ticker)

    shift_left = 0  # this shifts the window (size of hqDays) to left
    offset = len(hq) - hqDays - shift_left
    hq = np.array(hq[offset: offset + hqDays])
    # print(hq)
    closeHist = hq[:, 3].astype(np.float)   # close history
    # print(closeHist)
    dayIdxs = range(len(closeHist))

    """
    RDP markers
    """
    to2dim = np.vstack((dayIdxs, closeHist)).T
    delta = max(closeHist) - min(closeHist)
    epsilon = delta / 4
    # epsilon = min(closeHist) * 0.1  # determine epsilon
    rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    print(rdpPoints)

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

    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ro', markersize=7, label="(epsilon:%.2f)" % (epsilon))

    epsilon = delta / 2
    rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=4, label="(epsilon:%.2f)" % (epsilon))

    fig.suptitle("%s %s %d days" % (today, ticker, hqDays))
    plt.legend(loc='best')

    print(rdpPoints)
    print(rdpPoints.shape)
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
        plot(ticker, hqDays=92)
