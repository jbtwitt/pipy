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
    hqPatterns = HqPatterns(day)
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    tickers = hqConf[tickerList]
    for ticker in tickers:
        # ticker = 'GEVO'
        hqFile = CsvFileName.format(csvFolder, ticker)
        if os.path.exists(hqFile):
            hqDailyMetas = getHqDailyMetas(ticker, hqFile, 30)
            # print(len(hqDailyMetas))
            alerts = matchPatterns(hqPatterns, hqDailyMetas, startDayIdx)
            if len(alerts['bullish']) > 0:
                print(ticker, alerts['bullish'])
            # break
    print(hqPatterns.bullishEngulfings)

HqAlertType0 = 'bullish engulfing'
HqAlertType1 = 'nDaysLow within 10 days and bullish engulfing'
# HqPattern_BullishEngulfing
def matchPatterns(hqPatterns, hqDailyMetas, dayIdx=0):
    bullishAlerts = []
    for i in range(dayIdx,dayIdx+1):
        currMeta = hqDailyMetas[i]
        prevMeta = hqDailyMetas[i+1]
        bullishEngulfing = ((currMeta['C'] >= currMeta['O'] and prevMeta['C'] < prevMeta['O'])  #curr green; prev red
                        and (currMeta['H'] >= prevMeta['H'] and currMeta['L'] <= prevMeta['L']) #HL engulf
                        and (currMeta['O'] < prevMeta['C'] and currMeta['C'] > prevMeta['O']))  #OC engulf
        if bullishEngulfing:
            stickOC = (currMeta['C'] - currMeta['O']) / prevMeta['C']
            bullishAlerts.append({'type': HqAlertType0})
            nDays = 0
            for nDaysHL in currMeta['nDaysHLs']:
                if (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) <= 10.0:  #in 10 days
                    nDays = nDaysHL['nDays']
                    nDaysLow = (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo'])
                    nDaysLow = nDaysHL['cpLowDate']

                # if nDaysHL['nDays'] >= 60 and (nDaysHL['cpLowDateRowNo'] - currMeta['RowNo']) <= 10.0:  #in 10 days
                    # print('nDaysLow >= 180 Alert:', currMeta['ticker'],
                    #     currMeta['date'], currMeta['H'], currMeta['L'], currMeta['RowNo'])
                    # bullishAlerts.append({'type': 'nDaysLow >= 60 days within 10 days and bullish engulfing'})
            if nDays > 0:
                bullishAlerts.append({'type': HqAlertType1, 'nDays': nDays})
                hqPatterns.addBullishEngulfing(currMeta['ticker'], stickOC, nDaysLow)
            else:
                hqPatterns.addBullishEngulfing(currMeta['ticker'], stickOC)
    return {'bullish': bullishAlerts}

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
    hqConf = json.load(open('hqrobot.json'))
    repo = CsvFolder.format(hqConf["repo"], day)
    if not os.path.exists(repo):
        print('downloading ...', repo)
        hqDownload(hqConf, day)
        hqDownload(hqConf, day, 'etf')
    print(day, 'hq date folder')
    hqScanMain(hqConf, day)
    # hqScanMain(hqConf, day, 'etf')
