from datetime import datetime
from datetime import timedelta
from time import sleep
import json
import os
from HqYhoo import HqYhoo
from HqYhoo import DateFormat
from HqMeta import HqMeta
from HqAlert import HqAlert

CsvFolder = "{}/hq{}"
CsvFileName = "{}/{}.y.csv"

def hqScanMain(hqConf, day, tickerList="tickers", startDayIdx=0):
    # print(hqConf)
    tickers = hqConf[tickerList]
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    for ticker in tickers:
        # ticker = 'GEVO'
        hqFile = CsvFileName.format(csvFolder, ticker)
        if os.path.exists(hqFile):
            hqDailyMetas = getHqDailyMetas(ticker, hqFile, 30)
            # print(len(hqDailyMetas))
            alerts = FilterGevo20181225(hqDailyMetas, startDayIdx)
            if len(alerts['bullish']) > 0:
                print(ticker, alerts['bullish'])
            # break

HqAlertType0 = 'bullish engulfing'
HqAlertType1 = 'nDaysLow >= 60 days within 10 days and bullish engulfing'
HqAlertType2 = 'nDaysLow between 5 and 30 days within 10 days and bullish engulfing'
def FilterGevo20181225(hqDailyMetas, dayIdx=0):
    bullishAlerts = []
    for i in range(dayIdx,dayIdx+1):
        currMeta = hqDailyMetas[i]
        prevMeta = hqDailyMetas[i+1]
        bullishEngulfing = ((currMeta['C'] >= currMeta['O'] and prevMeta['C'] < prevMeta['O'])  #curr green; prev red
                        and (currMeta['H'] >= prevMeta['H'] and currMeta['L'] <= prevMeta['L']) #HL engulf
                        and (currMeta['O'] < prevMeta['C'] and currMeta['C'] > prevMeta['O']))  #OC engulf
        if bullishEngulfing:
            # bullishAlerts.append({'type': 'bullish engulfing'})
            bullishAlerts.append({'type': HqAlertType0})
            for nDaysHL in currMeta['nDaysHLs']:
                if nDaysHL['nDays'] >= 60 and (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) <= 10.0:  #in 10 days
                    # print('nDaysLow >= 180 Alert:', currMeta['ticker'],
                    #     currMeta['date'], currMeta['H'], currMeta['L'], currMeta['RowNo'])
                    # bullishAlerts.append({'type': 'nDaysLow >= 60 days within 10 days and bullish engulfing'})
                    bullishAlerts.append({'type': HqAlertType1})
                    break
            for nDaysHL in currMeta['nDaysHLs']:
                flag = ((nDaysHL['nDays'] >= 5 and nDaysHL['nDays'] <= 30)
                        and (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) <= 10.0)  #in 10 days
                if flag:
                    bullishAlerts.append({'type': HqAlertType2})
                    break
    return {'bullish': bullishAlerts}

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
    # day = '20190117'
    hqConf = json.load(open('hqrobot.json'))
    repo = CsvFolder.format(hqConf["repo"], day)
    if not os.path.exists(repo):
        print('downloading ...', repo)
        hqDownload(hqConf, day)
        hqDownload(hqConf, day, 'etf')
    print(day, 'hq date folder')
    hqScanMain(hqConf, day)
    hqScanMain(hqConf, day, 'etf')
