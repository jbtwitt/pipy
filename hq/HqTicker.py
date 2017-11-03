import numpy as np
from HqGoog import HqGoog

# class Hq:
#     def __init__(self, ticker, hqDate, close, high, low):
#         self.ticker = ticker
#         self.date = hqDate
#         self.close = close
#         self.high = high
#         self.low = low

class HqTicker:
    def __init__(self, ticker, hqDays=60, useCache=False):
        self.ticker = ticker
        self.hqGoog = HqGoog(self.ticker, hqDays, useCache)
        print("%s %s %.2f" % (self.ticker, self.hqGoog.hqDate(), self.hqGoog.hqClose()[0]))

    def npOHLCV(self, startDay=0):
        open = self.hqGoog.hqOpen()[startDay:]
        high = self.hqGoog.hqHigh()[startDay:]
        low = self.hqGoog.hqLow()[startDay:]
        close = self.hqGoog.hqClose()[startDay:]
        volume = self.hqGoog.hqVolume()[startDay:]
        return np.array([open, high, low, close, volume]).T

    def npOHLCVpC(self, startDay=0):
        ohlcv = self.npOHLCV(startDay)
        prevClose = self.hqGoog.hqClose()[startDay+1:]
        return np.column_stack([ohlcv[:len(prevClose)], prevClose])  # attach a column

    def npOHLCV_Test(self, startDay=0):
        open = self.hqGoog.hqOpen()[startDay:]
        high = self.hqGoog.hqHigh()[startDay:]
        low = self.hqGoog.hqLow()[startDay:]
        close = self.hqGoog.hqClose()[startDay:]
        volume = self.hqGoog.hqVolume()[startDay:]
        return np.array([open, high, low, close, volume, high-low]).T

    def nextDaysCloseByVolume(self, nextDays=1):
        startDay = nextDays
        close = self.hqGoog.hqClose()[startDay:]
        nextClose = self.hqGoog.hqClose()[:len(close)]
        volume = self.hqGoog.hqVolume()[startDay:]
        return np.array([volume, close, nextClose, nextClose-close, (nextClose-close)>0]).T

    def prepareForcastData(self, targetDay=0):
        startDay = targetDay + 1
        open = self.hqGoog.hqOpen()[startDay:]
        high = self.hqGoog.hqHigh()[startDay:]
        low = self.hqGoog.hqLow()[startDay:]
        close = self.hqGoog.hqClose()[startDay:]
        volume = self.hqGoog.hqVolume()[startDay:]
        targetClose = self.hqGoog.hqClose()[:len(close)]
        # print(close.shape)
        # print(self.hqGoog.hqClose().shape)
        # print(targetClose.shape)
        # print(targetClose[:5])
        # print(close[:3])
        return np.array([open, high, low, close, volume, targetClose]).T
        # endIdx = startDay + hqDays - 1
        # prevClose = self.hqGoog.hqClose()[startDay+1:endIdx+1]       # shift one
        # prevVolume = self.hqGoog.hqVolume()[startDay+1:endIdx+1]     # shift one

        # volatile = self.hqGoog.hqHigh()[startDay:endIdx] - self.hqGoog.hqLow()[startDay:endIdx]
        # change = (self.hqGoog.hqClose()[startDay:endIdx] - prevClose) / prevClose
        # volume = (self.hqGoog.hqVolume()[startDay:endIdx] - prevVolume) / prevVolume

        # print(change[:3])
        # print(volume[:3])
        # trainX

    # def old(self, startDay=0, hqDays=5):
        # for i in range(startDay, startDay+hqDays):
        #     hqClose = self.hqGoog.hqClose()[i]
        #     hqHigh = self.hqGoog.hqHigh()[i]
        #     hqLow = self.hqGoog.hqLow()[i]
        #     hqVolume = self.hqGoog.hqVolume()[i]
        #     prevVolume = self.hqGoog.hqVolume()[i + 1]
        #     prevClose = self.hqGoog.hqClose()[i + 1]
        #     # hq = Hq(self.ticker, self.hqGoog.hqDate(), hqClose[0], hqHigh[0], hqLow[0])
        #     # print(hq)
        #     change = (hqClose - prevClose) / prevClose
        #     volatile = (hqHigh - hqLow) / prevClose
        #     changeVol = (hqVolume - prevVolume) / prevVolume
        #     # print("%d volatile: %.2f%%" % (i, 100.0*volatile))
        #     # print("%d close volatile: %.2f%%" % (i, 100.0*(hqClose - hqLow)/prevClose))
        #     trainX.append([volatile, changeVol])
        #     trainY.append(change)

if __name__ == "__main__":
    ticker = 'IPGP'
    hqDays = 90
    hqTicker = HqTicker(ticker, hqDays, useCache=True)
    ohlcv = hqTicker.npOHLCV(startDay=0)
    ohlcvpc = hqTicker.npOHLCVpC(startDay=0)
    print(ohlcv.shape, ohlcvpc.shape)
    print(ohlcvpc[:2])
    nextCloseByVol = hqTicker.nextDaysCloseByVolume(nextDays=1)
    print(nextCloseByVol.shape)
    print(nextCloseByVol[:3])
    nextCloseByVol = hqTicker.nextDaysCloseByVolume(nextDays=2)
    print(nextCloseByVol.shape)
    print(nextCloseByVol[:3])
    t = np.array([1,2,3])
    print(t>1)
