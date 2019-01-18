from datetime import datetime
from datetime import timedelta
from time import sleep
import json
import os
from HqYhoo import HqYhoo
from HqYhoo import DateFormat
from HqMeta import HqMeta

CsvFolder = "{}/hq{}"
CsvFileName = "{}/{}.y.csv"

def hqScanMain(hqConf, day, tickerList="tickers"):
    # print(hqConf)
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    for i in range(1):
        ticker = 'GEVO'
        hqFile = CsvFileName.format(csvFolder, ticker)
        if os.path.exists(hqFile):
            hqDailyMetas = getHqDailyMetas(ticker, hqFile, 30)
            # print(len(hqDailyMetas))
            FilterGevo20181225(hqDailyMetas, 0)

def FilterGevo20181225(hqDailyMetas, dayIdx=0):
    for i in range(dayIdx,dayIdx+20):
        currMeta = hqDailyMetas[i]
        prevMeta = hqDailyMetas[i+1]
        # print(currMeta['date'], currMeta['O'], currMeta['close'], currMeta['H'], currMeta['L'])
        bullishEngulfing = ((currMeta['C'] >= currMeta['O'] and prevMeta['C'] < prevMeta['O'])  #curr green; prev red
                        and (currMeta['H'] >= prevMeta['H'] and currMeta['L'] <= prevMeta['L']) #HL engulf
                        and (currMeta['O'] < prevMeta['C'] and currMeta['C'] > prevMeta['O']))  #OC engulf
        if bullishEngulfing:
            print(currMeta['date'], currMeta['H'], currMeta['L'], currMeta['RowNo'])
            for nDaysHL in currMeta['nDaysHLs']:
                print(nDaysHL['nDays'], nDaysHL['cpLowDate'], nDaysHL['cpLowDateRowNo'] - currMeta['RowNo'])

def FilterGevo20190102(hqDailyMetas):
    for hqMeta in hqDailyMetas:
        print(hqMeta['date'], hqMeta['close'])
        print(hqMeta['nDaysStraight'], hqMeta['nDaysStraight']['upDays'])

def getHqDailyMetas(ticker, csvFile, nDays=50):
    # csvFolder = CsvFolder.format(hqConf['repo'], day)
    # csvFile = CsvFileName.format(csvFolder, ticker)
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
    day = '20190117'
    print(day, 'hq date folder')
    hqScanMain(json.load(open('hqrobot.json')), day, 'etf')
