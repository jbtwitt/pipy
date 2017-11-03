"""
"""
from urllib.request import urlopen, Request, URLError
import numpy as np

csvFileName = "/temp/{0}.g.csv"
class HqGoog:
    def __init__(self, ticker, hqDays=60, useCache=False):
        self.ticker = ticker
        if useCache:
            txt = self.csvIutput(self.ticker)
        else:
            txt = self.hqGoogRobot(self.ticker)
        self.lines = txt.split("\n")
        hq = []
        for idx, line in enumerate(self.lines[1:]):  # skip header row
            cols = line.split(',')
            hq.append(cols[1:]) # skip date column
            if idx > hqDays:
                break
        self.npHq = np.array(hq)
        self._hqOpen = self.npHq[:, 0].astype(np.float)   # open history
        self._hqHigh = self.npHq[:, 1].astype(np.float)   # high history
        self._hqLow = self.npHq[:, 2].astype(np.float)   # low history
        self._hqClose = self.npHq[:, 3].astype(np.float)   # close history
        self._hqVolume = self.npHq[:, 4].astype(np.int32)   # volume history

    def hqDate(self, dayIdx=0):
        return self.lines[dayIdx + 1].split(',')[0]

    def hqClose(self):
        return self._hqClose

    def hqHigh(self):
        return self._hqHigh

    def hqLow(self):
        return self._hqLow

    def hqOpen(self):
        return self._hqOpen

    def hqVolume(self):
        return self._hqVolume

    def hqGoogRobot(self, ticker):
        googUrl = "https://www.google.com/finance/historical?q={0}&output=csv"
        try:
            response = urlopen(googUrl.format(ticker))
            # print(str(response.info()))
            txt = response.read().decode("utf-8-sig")  # contain b'\xef\xbb\xbf...
            self.csvOutput(ticker, txt)
            return txt
        except URLError:
            print ("{} failed at attempt".format(ticker))

    def csvOutput(self, ticker, txt):
        csvFile = open(csvFileName.format(ticker), "w")
        csvFile.write(txt)
        csvFile.close()

    def csvIutput(self, ticker):
        csvFile = open(csvFileName.format(ticker), "r")
        txt = csvFile.read()
        csvFile.close()
        return txt

    # show = False
    # def myprint(object):
    #     if (show):
    #         print(object)
