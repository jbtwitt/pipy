import numpy as np
import matplotlib.pyplot as plt
from rdp import rdp
from HqGoog import HqGoog
from HqYhoo import HqYhoo
from HqYhoo import DateFormat
from datetime import datetime
from datetime import timedelta

# rdp: Ramer-Douglas-Peucker Algorithm

today = (datetime.now() + timedelta(days=1)).strftime(DateFormat)
csvFileName = "/gitrepo/robotRepo/hq20190926/{0}.y.csv"
def csvInput(ticker):
    csvFile = open(csvFileName.format(ticker), "r")
    txt = csvFile.read()
    csvFile.close()
    return txt

def download(hqDays):
    hqStartDate = (datetime.now() + timedelta(days=-hqDays)).strftime(DateFormat)
    print(ticker, ": date range", hqStartDate, today)
    hqRobot = HqYhoo()
    csv = hqRobot.hqGet(ticker, hqStartDate, today)
    return csv

def plot(ticker, hqDays=70):
    # hqGoog = HqGoog(ticker, hqDays)
    # closeHist = hqGoog.hqClose()
    # dayIdxs = range(len(closeHist))

    hq = []
    csv = csvInput(ticker)
    # print(csv)
    # lines = csv.decode("utf-8").replace(",-", ",0").split("\n")  # replace missing number
    lines = csv.replace(",-", ",0").split("\n")  # replace missing number
    for idx, line in enumerate(lines[1:]):  # skip header row
        if len(line) == 0:
            break
        cols = line.split(',')
        hq.append(cols[1:]) # skip date column
        # if idx > hqDays:
        #     break
    offset = len(hq) - hqDays
    hq = np.array(hq[offset:])
    # print(hq)
    closeHist = hq[:, 3].astype(np.float)   # close history
    # print(closeHist)
    dayIdxs = range(len(closeHist))
    # return

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
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=5, label="(epsilon:%.2f~%.2f%%)" % (epsilon, epsilon*100/closeHist[0]))

    epsilon = delta / 5
    rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    print(rdpPoints)
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ro', markersize=2, label="(epsilon:%.2f~%.2f%%)" % (epsilon, epsilon*100/closeHist[0]))

    fig.suptitle("%s %s %.2f" % (today, ticker, closeHist[0]))
    plt.legend(loc='best')
    plt.show()

# tickers = ['WATT', 'ATHX', 'SVA', 'ERX', 'AMZN', 'LABU']
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('tickers', metavar='tickers', type=str, nargs='+', help='ticker list')
    # parser.add_argument('-ticker', help='ticker')
    args = parser.parse_args()
    # print(vars(args)[''])
    print(args.tickers)
    for ticker in args.tickers:
        plot(ticker, hqDays=90)
