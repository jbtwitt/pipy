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
 
def csvInput(ticker):
    csvFile = open(csvFileName.format(getDayFolder(), ticker), "r")
    txt = csvFile.read()
    csvFile.close()
    return txt

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

def plot(ticker, hqDays=70):
    csv = csvInput(ticker)
    hq = csv2Array(csv)
    offset = len(hq) - hqDays
    hq = np.array(hq[offset:])
    # print(hq)
    closeHist = hq[:, 3].astype(np.float)   # close history
    # print(closeHist)
    dayIdxs = range(len(closeHist))

    '''
    hq chart
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(dayIdxs, closeHist)
    # ax.plot(range(len(closeCol)), list(reversed(closeCol)), 'g')    # green
    # ax.plot(range(len(closeCol)), closeCol, 'ko', markersize = 5, label='turning points')   # black

    """
    RDP markers
    """
    to2dim = np.vstack((dayIdxs, closeHist)).T
    delta = max(closeHist) - min(closeHist)

    epsilon = delta / 8
    rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    print(rdpPoints)
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=5, label="(epsilon:%.2f~%.2f%%)" % (epsilon, epsilon*100/closeHist[0]))

    # epsilon = delta / 5
    # rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    # print(rdpPoints)
    # ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ro', markersize=2, label="(epsilon:%.2f~%.2f%%)" % (epsilon, epsilon*100/closeHist[0]))

    fig.suptitle("%s %s %.2f" % (today, ticker, closeHist[0]))
    plt.legend(loc='best')
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
