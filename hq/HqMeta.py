import pandas as pd
import json
import math
import os
from datetime import datetime

class HqMeta:
    def __init__(self, ticker, hqFile):
        csv = pd.read_csv(hqFile, index_col=[0], parse_dates=False)
        self.csv = self.addCols(csv)
        self.ticker = ticker
        self.hqFile = hqFile
        # hqMeta = self.collect()

    def collect(self, startDayIdx=0):
        self.startDayIdx = startDayIdx
        hqMeta = {'ticker':self.ticker, 'hqFile':self.hqFile}
        hqMeta['date'] = self.lastDate
        hqMeta['close'] = self.lastClose
        hqMeta['change'] = self.nDaysChange(1)
        hqMeta['HL'] = self.HL()
        hqMeta['CL'] = self.CL()
        hqMeta['nDaysStraightDown'] = self.nDaysStraightDown()
        # hqMeta['nDaysStraightDownPrev_1'] = self.nDaysStraightDown(1)
        hqMeta['nDaysStraightUp'] = self.nDaysStraightUp()

        hqMeta['nDaysDiff_5'] = self.nDaysDiff(5)
        hqMeta['nDaysDiff_10'] = self.nDaysDiff(10)
        return hqMeta

    def nDaysStraightDown(self):
        nDays = 0
        csv = self.csv
        for i in range(self.startDayIdx, len(csv.index)):
            if csv.Close[i] > csv.PrevClose[i]:
                break
            nDays = nDays + 1
        return {'nDays':nDays, 'down':self.nDaysChange(nDays)}

    def nDaysStraightUp(self):
        nDays = 0
        csv = self.csv
        for i in range(self.startDayIdx, len(csv.index)):
            if csv.Close[i] < csv.PrevClose[i]:
                break
            nDays = nDays + 1
        return {'nDays':nDays, 'up':self.nDaysChange(nDays)}

    def nDaysChange(self, nDays):
        startDayIdx = self.startDayIdx
        row0 = self.csv.iloc[startDayIdx]
        row1 = self.csv.iloc[startDayIdx + nDays]
        if nDays == 0:
            return (row0.Close - row0.PrevClose) / row1.PrevClose
        return (row0.Close - row1.Close) / row1.Close

    def nDaysDiff(self, nDays):
        close0 = self.csv.iloc[self.startDayIdx].Close
        nDaysCsvSort = self.csv[self.startDayIdx:(self.startDayIdx + nDays + 1)].sort_values(by='Close', ascending=False)#.iloc[0]
        nDaysHighest = nDaysCsvSort.iloc[0]
        nDaysLowest = nDaysCsvSort.iloc[len(nDaysCsvSort)-1]
        return {
            'nDaysHighest': int(nDaysHighest.No),
            'highestDate': nDaysCsvSort.index[0],
            'downDiff': (close0-nDaysHighest.Close)/nDaysHighest.Close,
            'nDaysLowest': int(nDaysLowest.No),
            'lowestDate': nDaysCsvSort.index[len(nDaysCsvSort)-1],
            'upDiff': (close0-nDaysLowest.Close)/nDaysLowest.Close,
        }

    def CL(self):
        row = self.csv.iloc[self.startDayIdx]
        return (row.Close - row.Low) / row.PrevClose

    def HL(self):
        row = self.csv.iloc[self.startDayIdx]
        return (row.High - row.Low) / row.PrevClose

    def addCols(self, csv):
        csv['PrevClose'] = csv.Close.shift(1)
        # csv['Change'] = (csv.Close - csv.PrevClose) / csv.PrevClose
        # csv['HL'] = (csv.High - csv.Low) / csv.PrevClose
        # csv['CL'] = (csv.Close - csv.Low) / csv.PrevClose
        csv = csv.reindex(index=csv.index[::-1])   # reverse date order
        csv['No'] = range(len(csv.index))
        return csv

    @property
    def lastDate(self):
        # return self.csv.index[-1]    # reversed(self.csv.index)(0)
        return self.csv.index[self.startDayIdx]

    @property
    def lastClose(self):
        return self.csv.Close[self.startDayIdx]
