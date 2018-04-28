import re
from urllib.request import urlopen, Request, URLError
from datetime import datetime
from datetime import timedelta
import calendar

InitLink = 'https://finance.yahoo.com/quote/AMZN/history?p=AMZN'
HqLink = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'
CrumbRegex = r'CrumbStore":{"crumb":"(.*?)"}'
CookRegex = r'set-cookie: (.*?); '
DateFormat = "%Y-%m-%d"
class HqYhoo:
    def __init__(self):
        self.crumb = 'not found'
        self.cookie = 'not found'
        self.initSession()
        print(self.crumb, self.cookie)

    def initSession(self):
        response = urlopen(InitLink)
        # print(str(response.info()))
        match = re.search(CookRegex, str(response.info()))
        if match != None:
            self.cookie = match.group(1)
        txt = response.read().decode("utf-8-sig")  #it is byte like object before using decode
        match = re.search(CrumbRegex, txt)
        if match != None:
            self.crumb = match.group(1)

    def hqGet(self, ticker, startDate, endDate):
        fromTime = calendar.timegm(datetime.strptime(startDate, DateFormat).timetuple())
        toTime = calendar.timegm(datetime.strptime(endDate, DateFormat).timetuple())
        hqLink = HqLink.format(ticker, fromTime, toTime, self.crumb)
        print(hqLink)
        r = Request(hqLink, headers={'Cookie': self.cookie})
        try:
            response = urlopen(r)
            txt = response.read()
            print("{} downloaded".format(ticker))
            return txt
        except URLError:
            print("{} failed".format(ticker))
        return ''
