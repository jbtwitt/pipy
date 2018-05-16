import pandas as pd
import json
import math
import os
from datetime import datetime

class HqMeta:
    def __init__(self, ticker, hqCsvFile):
        csv = pd.read_csv(hqCsvFile, index_col=[0], parse_dates=False)
        self.csv = self.addCols(csv)
        self.ticker = ticker
        self.hqCsvFile = hqCsvFile
        # hqMeta = self.collect()

    def collect(self, startDayIdx=0):
        self.startDayIdx = startDayIdx
        hqMeta = {'ticker':self.ticker, 'hqCsvFile':self.hqCsvFile}
        hqMeta['date'] = self.lastDate
        hqMeta['close'] = self.lastClose
        hqMeta['change'] = self.nDaysChange(1)
        hqMeta['HL'] = self.HL
        hqMeta['CL'] = self.CL
        hqMeta['volChange'] = self.volChange

        days = [5, 10, 20, 30, 60, 120, 180]
        nDaysHLs = []
        for nDays in days:
            nDaysHLs.append(self.nDaysHL(nDays))
        hqMeta['nDaysHLs'] = nDaysHLs

        hqMeta['nDaysStraight'] = self.nDaysStraight()

        nDaysDiffs = []
        for nDays in [5, 10, 20]:
            nDaysDiffs.append(self.nDaysDiff(nDays))
        hqMeta['nDaysDiffs'] = nDaysDiffs

        return hqMeta

    def nDaysHL(self, nDays):
        # Close HL
        df = self.csv[self.startDayIdx:self.startDayIdx + nDays].Close.sort_values(ascending=False)
        # df4 = hqCsv.df[0:4].sort_values(by='Close', ascending=True)
        returnValue = {"nDays": nDays, "HighDate": df.index[0], "LowDate": df.index[len(df.index)-1]}
        # Volume HL
        df = self.csv[self.startDayIdx:self.startDayIdx + nDays].Volume.sort_values(ascending=False)
        returnValue["vHighDate"] = df.index[0]
        returnValue["vLowDate"] = df.index[len(df.index)-1]
        # HL HL
        df = self.csv[self.startDayIdx:self.startDayIdx + nDays].HL.sort_values(ascending=False)
        returnValue["hlHighDate"] = df.index[0]
        returnValue["hlLowDate"] = df.index[len(df.index)-1]
        return returnValue

    def nDaysStraight(self):
        for i in range(self.startDayIdx, len(self.csv.index)):
            if self.csv.Close[i] > self.csv.PrevClose[i]:
                break
        downDays = i - self.startDayIdx
        for i in range(self.startDayIdx, len(self.csv.index)):
            if self.csv.Close[i] < self.csv.PrevClose[i]:
                break
        upDays = i - self.startDayIdx
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
        csv['PrevVolume'] = csv.Volume.shift(1)
        csv = csv.reindex(index=csv.index[::-1])   # reverse date order
        csv['No'] = range(len(csv.index))
        csv['HL'] = (csv.High - csv.Low)/csv.Low
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
        return self.csv.HL[self.startDayIdx]

    @property
    def CL(self):
        row = self.csv.iloc[self.startDayIdx]
        return (row.Close - row.Low) / row.Low  # row.PrevClose

    @property
    def volChange(self):
        row = self.csv.iloc[self.startDayIdx]
        return (row.Volume - row.PrevVolume) / row.PrevVolume
