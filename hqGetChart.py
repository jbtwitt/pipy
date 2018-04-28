import datetime
from urllib.request import urlopen, Request, URLError
# from PIL import Image, ImageFilter  # imports the library
from dl.workspace import Workspace
from dl.train_store import TrainStore
from dl.mnst_model import mnstModel

tickers = ['WATT', 'ATHX', 'SVA', 'NVAX', 'NVDA', 'TEUM', 'KODK', 'SNAP']
# tickers = ['WATT']

ws = Workspace('hq', ['up1', 'up2', 'down1', 'down2' 'other'])
model = 'mnst'
modelStore = ws.modelStore(model)

def naming(ticker, store):
    timestamp = datetime.datetime.now()
    # name = store + '/' + ticker + '_' + timestamp.strftime("%Y%m%d_%H%M%S_%f")
    name = store + '/' + ticker + '_' + timestamp.strftime("%Y%m%d")
    return name + '.png', name + '.csv'

def main():
    for ticker in tickers:
        png, csv = naming(ticker, ws.getRootPath())
        print(png, csv)
        csvUrl = "https://finance.google.com/finance/historical?q=" + ticker + "&output=csv"
        # chartUrl = "https://finance.google.com/finance/getchart?q=" + ticker + "&x=NASD&p=5d&i=240"
        chartUrl = "https://finance.google.com/finance/getchart?q=" + ticker + "&p=5d&i=240"
        getUri(chartUrl, png)
        getUri(csvUrl, csv)


def getUri(myUrl, path):
    try:
        # myUrl = "https://finance.google.com/finance/getchart?q=" + ticker + "&x=NASD&p=5d&i=240"
        # print('downloading...')
        response = urlopen(myUrl)
        # print(str(response.info()))
        data = response.read()
        jpgFile = open(path, "wb")
        jpgFile.write(data)
        jpgFile.close()
        response.close()
        # return path
    except URLError:
        print ("url failed at attempt")


# chart = Image.open(path)
# chart.show()
main()