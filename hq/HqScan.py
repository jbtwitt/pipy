from datetime import datetime
from datetime import timedelta
from time import sleep
import json
import os
from HqYhoo import HqYhoo
from HqYhoo import DateFormat
from HqMeta import HqMeta
from HqPatterns import HqPatterns

CsvFolder = "{}/hq{}"
CsvFileName = "{}/{}.y.csv"

def hqScanMain(hqConf, day, tickerList="tickers", startDayIdx=0):
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    # tickers = hqConf[tickerList]
    hqPatterns = hqStartScan(hqConf[tickerList], csvFolder, startDayIdx)
    print(hqPatterns.bullishEngulfings)

def hqStartScan(tickers, csvFolder, startDayIdx=0, nDays=5):
    hqPatterns = HqPatterns()
    for ticker in tickers:
        # ticker = 'GEVO'
        hqFile = CsvFileName.format(csvFolder, ticker)
        if os.path.exists(hqFile):
            hqDailyMetas = getHqDailyMetas(ticker, hqFile, nDays+startDayIdx)
            # print(len(hqDailyMetas))
            matchPatterns(hqPatterns, hqDailyMetas, startDayIdx)
            # break
    return hqPatterns

def matchPatterns(hqPatterns, hqDailyMetas, dayIdx=0, nDaysRange=5):
    currMeta = hqDailyMetas[dayIdx]
    prevMeta = hqDailyMetas[dayIdx + 1]
    bullishEngulfing = ((currMeta['C'] >= currMeta['O'] and prevMeta['C'] < prevMeta['O'])  #curr green; prev red
                    and (currMeta['H'] >= prevMeta['H'] and currMeta['L'] <= prevMeta['L']) #HL engulf
                    and (currMeta['O'] < prevMeta['C'] and currMeta['C'] > prevMeta['O']))  #OC engulf
    if bullishEngulfing:
        stickOC = (currMeta['C'] - currMeta['O']) / prevMeta['C']
        _nDaysHL = None
        for nDaysHL in reversed(currMeta['nDaysHLs']):
            if (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) <= nDaysRange:  #within days
                _nDaysHL = nDaysHL
                break
        if _nDaysHL != None:
            hqPatterns.addBullishEngulfing(currMeta['ticker'], stickOC, _nDaysHL)
        else:
            hqPatterns.addBullishEngulfing(currMeta['ticker'], stickOC)

def getHqDailyMetas(ticker, csvFile, nDays=50):
    hqMeta = HqMeta(ticker, csvFile)
    hqDailyMetas = []
    for dayIdx in range(nDays):
        hqDailyMetas.append(hqMeta.collect(dayIdx))
    return hqDailyMetas

def hqDownload(hqConf, day, tickerList="tickers"):
    tickers = hqConf[tickerList]
    hqDays = 7 * hqConf["hqDays"] / 5
    # repo = hqConf["repo"] + '/hq' + datetime.now().strftime("%Y%m%d")
    repo = CsvFolder.format(hqConf["repo"], day)
    if not os.path.exists(repo):
        os.makedirs(repo)
    today = (datetime.now() + timedelta(days=1)).strftime(DateFormat)
    startDate = (datetime.now() + timedelta(days=-hqDays)).strftime(DateFormat)
    print("date range", startDate, today)
    hqRobot = HqYhoo()
    for ticker in tickers:
        try:
            csv = hqRobot.hqGet(ticker, startDate, today)
            output = CsvFileName.format(repo, ticker)
            with open(output, 'wb') as f:
                f.write(csv)
            print("{} ...".format(ticker))
        except:
            print("{} failed".format(ticker))
            break
        sleep(hqConf["sleep"])

if __name__ == '__main__':
    day = (datetime.now() + timedelta(days=-0)).strftime("%Y%m%d")
    # day = '20190102'
    hqConf = json.load(open('hqrobot.json'))
    repo = CsvFolder.format(hqConf["repo"], day)
    if not os.path.exists(repo):
        print('downloading ...', repo)
        hqDownload(hqConf, day)
        hqDownload(hqConf, day, 'etf')
    print(day, 'hq date folder')
    hqScanMain(hqConf, day, 'tickers', startDayIdx=0)
    # hqScanMain(hqConf, day, 'etf')
