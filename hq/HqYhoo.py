import re
from urllib.request import urlopen, Request, URLError
from datetime import datetime
import calendar

InitLink = 'https://finance.yahoo.com/quote/AMZN/history?p=AMZN'
HqLink = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'
CrumbRegex = r'CrumbStore":{"crumb":"(.*?)"}'
CookRegex = r'set-cookie: (.*?); '
DateFormat = "%Y-%m-%d"
class HqYhoo:
    crumb = 'not found'
    cookie = 'not found'
    def __init__(self):
        self.initSession()
        print("session init", self.crumb, self.cookie)

    def initSession(self):
        response = urlopen(InitLink)
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
        request = Request(hqLink, headers={'Cookie': self.cookie})
        try:
            response = urlopen(request)
            txt = response.read()
            return txt
        except URLError:
            raise
