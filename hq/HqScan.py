from datetime import datetime
from datetime import timedelta
from time import sleep
import json
import os
from HqYhoo import HqYhoo
from HqYhoo import DateFormat
from HqMeta import HqMeta
from HqPatterns import HqPatterns, Pattern

CsvFolder = "{}/hq{}"
CsvFileName = "{}/{}.y.csv"

def hqScanMain(hqConf, day, tickerList="tickers", startDayIdx=0):
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    # tickers = hqConf[tickerList]
    hqPatterns = hqStartScan(hqConf[tickerList], csvFolder, startDayIdx)
    print('bullish engulfing', hqPatterns.bullishEngulfings)
    print('morning star', hqPatterns.morningStars)
    print(hqPatterns.patterns)

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

def hqTickerScanMain(hqConf, day, ticker, startDayIdx=0):
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    hqPatterns = hqTickerScan(ticker, csvFolder, startDayIdx, 60)
    # print(hqPatterns.patterns)
    for pattern in hqPatterns.patterns:
        print(pattern['date'], pattern['pattern'], pattern['nDaysHL']['nDays'])

def hqTickerScan(ticker, csvFolder, startDayIdx=0, nDays=20):
    hqPatterns = HqPatterns()
    hqFile = CsvFileName.format(csvFolder, ticker)
    if os.path.exists(hqFile):
        hqDailyMetas = getHqDailyMetas(ticker, hqFile, nDays+startDayIdx+5)
        for i in range(startDayIdx, startDayIdx + nDays):
            matchPatterns(hqPatterns, hqDailyMetas, i)
    return hqPatterns

def matchPatterns(hqPatterns, hqDailyMetas, dayIdx=0, nDaysRange=5):
    currMeta = hqDailyMetas[dayIdx]
    prevMeta = hqDailyMetas[dayIdx + 1]
    ticker = currMeta['ticker']
    # nDaysVolumeHigh
    # for i in range[30]:
    #     meta = hqDailyMetas[i]
    #     for nDaysHL in reversedmeta['nDaysHLs']:
    #         if (nDaysHL['vHighDateRowNo'] - currMeta['RowNo'])
    stickOC = (currMeta['C'] - currMeta['O']) / prevMeta['C']
    """
    # nDaysCloseLow:
    for nDaysHL in reversed(currMeta['nDaysHLs']):
        if (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) == 1:
            hqPatterns.addPattern(ticker, currMeta['date'], Pattern.NDaysCloseLow, stickOC, nDaysHL)
            break
    # nDaysCloseHigh:
    for nDaysHL in reversed(currMeta['nDaysHLs']):
        if (nDaysHL['cpHighDateRowNo'] - currMeta['RowNo']) == 1:
            hqPatterns.addPattern(ticker, currMeta['date'], Pattern.NDaysCloseHigh, stickOC, nDaysHL)
            break
    """
    # bullish engulfing
    bullishEngulfing = ((currMeta['C'] > currMeta['O'] and prevMeta['C'] < prevMeta['O'])  #curr green; prev red
                    and (currMeta['H'] >= prevMeta['H'] and currMeta['L'] <= prevMeta['L']) #HL engulf
                    and (currMeta['O'] < prevMeta['C'] and currMeta['C'] > prevMeta['O']))  #OC engulf
    if bullishEngulfing:
        for nDaysHL in reversed(currMeta['nDaysHLs']):
            if (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) <= nDaysRange:  #within days
                # hqPatterns.addBullishEngulfing(ticker, stickOC, nDaysHL)
                hqPatterns.addPattern(ticker, currMeta['date'], Pattern.BullishEngulfing, stickOC, nDaysHL)
                break
    # morning star
    prev2Meta = hqDailyMetas[dayIdx + 2]
    morningStar = ((currMeta['O'] > prevMeta['C'] and currMeta['C'] > currMeta['O'])
                    and currMeta['HL'] > prevMeta['HL']
                    and prevMeta['O'] < prev2Meta['C']
                    and prev2Meta['HL'] > prevMeta['HL']
                    and prev2Meta['C'] < prev2Meta['O']
                    and (prev2Meta['O'] - prev2Meta['C']) > prevMeta['HL']
                    and (currMeta['C'] > prev2Meta['O'] or (currMeta['H'] - currMeta['C'])/prevMeta['C'] < 0.01))
    if morningStar:
        stickOC = (currMeta['C'] - currMeta['O']) / prevMeta['C']
        for nDaysHL in reversed(prev2Meta['nDaysHLs']):
            if (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) == 2:
                hqPatterns.addPattern(ticker, currMeta['date'], Pattern.MorningStar, stickOC, nDaysHL)
                break
    # bearish engulfing
    bearishEngulfing = ((currMeta['C'] < currMeta['O'] and prevMeta['C'] > prevMeta['O'])  #curr red; prev green
                    and (currMeta['H'] >= prevMeta['H'] and currMeta['L'] <= prevMeta['L']) #HL engulf
                    and (currMeta['O'] > prevMeta['C'] and currMeta['C'] < prevMeta['O']))  #OC engulf
    if bearishEngulfing:
        for nDaysHL in reversed(currMeta['nDaysHLs']):
            if (nDaysHL['cpHighDateRowNo'] - currMeta['RowNo']) <= nDaysRange:  #within days
                hqPatterns.addPattern(ticker, currMeta['date'], Pattern.BearishEngulfing, stickOC, nDaysHL)
                break

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
    day = '20190118'
    hqConf = json.load(open('hqrobot.json'))
    repo = CsvFolder.format(hqConf["repo"], day)
    if not os.path.exists(repo):
        print('downloading ...', repo)
        hqDownload(hqConf, day)
        hqDownload(hqConf, day, 'etf')
    print(day, 'hq date folder')
    # hqScanMain(hqConf, day, 'tickers', startDayIdx=0)
    # hqScanMain(hqConf, day, 'etf')
    hqTickerScanMain(hqConf, day, 'GEVO', 12)
