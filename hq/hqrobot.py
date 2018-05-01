from datetime import datetime
from datetime import timedelta
from time import sleep
import json
import os
from HqYhoo import HqYhoo
from HqYhoo import DateFormat

CsvFolder = "{}/hq{}"
CsvFileName = "{}/{}.y.csv"
def main(hqConf):
    tickers = hqConf["tickers"]
    hqDays = 7 * hqConf["hqDays"] / 5
    # repo = hqConf["repo"] + '/hq' + datetime.now().strftime("%Y%m%d")
    repo = CsvFolder.format(hqConf["repo"], datetime.now().strftime("%Y%m%d"))
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

"""
https://query1.finance.yahoo.com/v7/finance/download/LABU?period1=1522195963&period2=1524874363&interval=1d&events=history&crumb=SvxJY.f67nr
https://query1.finance.yahoo.com/v7/finance/download/ATHX?period1=1522196132&period2=1524874532&interval=1d&events=history&crumb=SvxJY.f67nr
"""
if __name__ == '__main__':
    main(json.load(open('hqrobot.json')))
