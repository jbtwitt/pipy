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

    def collect(self):
        hqMeta = {'ticker':self.ticker, 'hqFile':self.hqFile}
        hqMeta['date'] = self.lastDate()
        hqMeta['HL'] = self.HL(0)
        hqMeta['CL'] = self.CL(0)
        hqMeta['nDaysStraightDown'] = self.nDaysStraightDown(0)
        hqMeta['nDaysStraightDownPrev_1'] = self.nDaysStraightDown(1)
        hqMeta['nDaysStraightUp'] = self.nDaysStraightUp(0)
        return hqMeta

    def nDaysStraightDown(self, startDayIdx):
        nDays = 0
        csv = self.csv
        for i in range(startDayIdx, len(csv.index)):
            if csv.Close[i] > csv.PrevClose[i]:
                break
            nDays = nDays + 1
        return {'nDays':nDays, 'down':self.nDaysChange(startDayIdx, nDays)}

    def nDaysStraightUp(self, startDayIdx):
        nDays = 0
        csv = self.csv
        for i in range(startDayIdx, len(csv.index)):
            if csv.Close[i] < csv.PrevClose[i]:
                break
            nDays = nDays + 1
        return {'nDays':nDays, 'up':self.nDaysChange(startDayIdx, nDays)}

    def nDaysChange(self, startDayIdx, nDays):
        row0 = self.csv.iloc[startDayIdx]
        row1 = self.csv.iloc[startDayIdx + nDays]
        if nDays == 0:
            return (row0.Close - row0.PrevClose) / row1.PrevClose
        return (row0.Close - row1.Close) / row1.Close

    def CL(self, startDayIdx):
        row = self.csv.iloc[startDayIdx]
        return (row.Close - row.Low) / row.PrevClose

    def HL(self, startDayIdx):
        row = self.csv.iloc[startDayIdx]
        return (row.High - row.Low) / row.PrevClose

    def addCols(self, csv):
        csv['PrevClose'] = csv.Close.shift(1)
        # csv['Change'] = (csv.Close - csv.PrevClose) / csv.PrevClose
        # csv['HL'] = (csv.High - csv.Low) / csv.PrevClose
        # csv['CL'] = (csv.Close - csv.Low) / csv.PrevClose
        csv = csv.reindex(index=csv.index[::-1])   # reverse date order
        csv['No'] = range(len(csv.index))
        return csv

    def lastDate(self):
        # return self.csv.index[-1]    # reversed(self.csv.index)(0)
        return self.csv.index[0]
