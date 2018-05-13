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
        hqMeta['HL'] = self.HL
        hqMeta['CL'] = self.CL

        hqMeta['nDaysStraight'] = self.nDaysStraight()

        nDaysDiffs = []
        for days in [5, 10, 20]:
            nDaysDiffs.append(self.nDaysDiff(days))
        hqMeta['nDaysDiffs'] = nDaysDiffs

        return hqMeta

    def nDaysStraight(self):
        downDays = 0
        for i in range(self.startDayIdx, len(self.csv.index)):
            if self.csv.Close[i] > self.csv.PrevClose[i]:
                break
            downDays = downDays + 1
        upDays = 0
        for i in range(self.startDayIdx, len(self.csv.index)):
            if self.csv.Close[i] < self.csv.PrevClose[i]:
                break
            upDays = upDays + 1
        return {
            'upDays': upDays, 
            'upDiff': self.nDaysChange(upDays),
            'downDays': downDays, 
            'downDiff': self.nDaysChange(downDays)
        }

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
            'nDays': nDays,
            'nDaysHighest': int(nDaysHighest.No),
            'highestDate': nDaysCsvSort.index[0],
            'downDiff': (close0-nDaysHighest.Close)/nDaysHighest.Close,
            'nDaysLowest': int(nDaysLowest.No),
            'lowestDate': nDaysCsvSort.index[len(nDaysCsvSort)-1],
            'upDiff': (close0-nDaysLowest.Close)/nDaysLowest.Close,
        }

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

    @property
    def HL(self):
        row = self.csv.iloc[self.startDayIdx]
        return (row.High - row.Low) / row.Low   # row.PrevClose

    @property
    def CL(self):
        row = self.csv.iloc[self.startDayIdx]
        return (row.Close - row.Low) / row.Low  # row.PrevClose
