import pandas as pd
import json
import math
import os
from datetime import datetime
from HqCsv import HqCsv

class HqMeta:
    def __init__(self, ticker, hqCsvFile):
        self.csv = HqCsv(ticker, hqCsvFile).df
        self.ticker = ticker
        self.hqCsvFile = hqCsvFile
        # hqMeta = self.collect()

    def collect(self, startDayIdx=0):
        self.startDayIdx = startDayIdx
        self.row = self.csv.iloc[startDayIdx]
        hqMeta = {'ticker':self.ticker, 'hqCsvFile':self.hqCsvFile}
        hqMeta['date'] = self.lastDate
        hqMeta['close'] = self.lastClose
        hqMeta['change'] = self.nDaysChange(1)
        hqMeta['prevClose'] = self.row.PrevClose
        hqMeta['HL'] = self.HL
        hqMeta['CL'] = self.CL
        hqMeta['LP'] = self.LP
        hqMeta['VolChange'] = self.VolChange

        hqMeta['H'] = self.H
        hqMeta['L'] = self.L
        hqMeta['O'] = self.O
        hqMeta['C'] = self.lastClose
        hqMeta['RowNo'] = 0.0+self.RowNo

        days = [5, 10, 20, 30, 60, 120, 180, 240]
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
        nDaysCsv = self.csv[self.startDayIdx:self.startDayIdx + nDays]
        ret = {"nDays": nDays}
        # Close HL
        df = nDaysCsv.Close.sort_values(ascending=False)
        ret["cpHighDate"] = df.index[0]
        ret['cpHighDateRowNo'] = nDaysCsv.loc[df.index[0]].No
        ret["cpLowDate"] = df.index[len(df.index)-1]
        ret['cpLowDateRowNo'] = nDaysCsv.loc[ret['cpLowDate']].No
        ret["cpDiff"] = (nDaysCsv.loc[ret['cpHighDate']].Close - nDaysCsv.loc[ret['cpLowDate']].Close)/nDaysCsv.loc[ret['cpLowDate']].Close
        # Volume HL
        df = nDaysCsv.Volume.sort_values(ascending=False)
        ret["vHighDate"] = df.index[0]
        ret['vHighDateRowNo'] = nDaysCsv.loc[ret['vHighDate']].No
        ret["vLowDate"] = df.index[len(df.index)-1]
        # HL HL
        df = nDaysCsv.HL.sort_values(ascending=False)
        ret["hlHighDate"] = df.index[0]
        ret["hlLowDate"] = df.index[len(df.index)-1]
        # LP HL
        # df = nDaysCsv.LP.sort_values(ascending=False)
        # ret["lpHighDate"] = df.index[0]
        # ret["lpLowDate"] = df.index[len(df.index)-1]
        return ret

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
            'upDays': upDays, 'upDiff': self.nDaysChange(upDays),
            'downDays': downDays, 'downDiff': self.nDaysChange(downDays)
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

    # def addCols(self, csv):
    #     csv['PrevClose'] = csv.Close.shift(1)
    #     csv['PrevVolume'] = csv.Volume.shift(1)
    #     csv = csv.reindex(index=csv.index[::-1])   # reverse date order
    #     csv['No'] = range(len(csv.index))
    #     csv['HL'] = (csv.High - csv.Low)/csv.PrevClose
    #     return csv

    @property
    def lastDate(self):
        # return self.csv.index[-1]    # reversed(self.csv.index)(0)
        return self.csv.index[self.startDayIdx]

    @property
    def lastClose(self):
        return self.row.Close

    @property
    def O(self):
        return self.row.Open

    @property
    def H(self):
        return self.row.High

    @property
    def L(self):
        return self.row.Low

    @property
    def HL(self):
        return self.row.HL

    @property
    def CL(self):
        # row = self.csv.iloc[self.startDayIdx]
        return (self.row.Close - self.row.Low) / self.row.PrevClose

    @property
    def LP(self):
        return self.row.LP

    @property
    def VolChange(self):
        return self.row.VolChange

    @property
    def RowNo(self):
        return self.row.No