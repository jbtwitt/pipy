

import numpy as np
import matplotlib.pyplot as plt
from rdp import rdp
from HqGoog import HqGoog

def plot(ticker, hqDays=60):
    hqGoog = HqGoog(ticker, hqDays)
    closeHist = hqGoog.hqClose()
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
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ko', markersize=5, label="(epsilon:%.2f~%.2f%%)" % (epsilon, epsilon*100/closeHist[0]))

    epsilon = delta / 5
    rdpPoints = np.array(rdp(to2dim.tolist(), epsilon))
    print(rdpPoints)
    ax.plot(rdpPoints[:, 0], rdpPoints[:, 1], 'ro', markersize=2, label="(epsilon:%.2f~%.2f%%)" % (epsilon, epsilon*100/closeHist[0]))

    fig.suptitle("%s %s %.2f" % (hqGoog.hqDate(0), ticker, closeHist[0]))
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
