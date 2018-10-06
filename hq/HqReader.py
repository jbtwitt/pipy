import pandas as pd

CsvFileNameFormat = "/gitrepo/robotRepo/hq{}/{}.y.csv"
def readRawData(ticker, day):
    csvFile=CsvFileNameFormat.format(day, ticker)
    df = pd.read_csv(csvFile, index_col=[0], parse_dates=False)
    csvShape=df.shape
    df['PrevClose'] = df.Close.shift(1)
    df['PrevVolume'] = df.Volume.shift(1)

    df['VolChange'] = (df.Volume - df.PrevVolume)/df.PrevVolume
    df['OP'] = (df.Open - df.PrevClose) /df.PrevClose
    df['HP'] = (df.High - df.PrevClose)/df.PrevClose
    df['LP'] = (df.Low - df.PrevClose)  /df.PrevClose
    df['CP'] = (df.Close - df.PrevClose)/df.PrevClose
    # df['HL'] = (df.High - df.Low)/df.PrevClose
    df['HL'] = df.HP - df.LP
    # print(df[0:4])
    # print(df.iloc[1:4,8:])
    return df.iloc[1:,8:].values

class HqReader:
    def __init__(self,ticker,day):
        self.ticker=ticker
        self.day=day
        csvFile=CsvFileNameFormat.format(day, ticker)
        df = pd.read_csv(csvFile, index_col=[0], parse_dates=False)
        csvShape=df.shape
        df['PrevClose'] = df.Close.shift(1)
        df['PrevVolume'] = df.Volume.shift(1)

        df['VolChange'] = (df.Volume - df.PrevVolume)/df.PrevVolume
        df['OP'] = (df.Open - df.PrevClose) /df.PrevClose
        df['HP'] = (df.High - df.PrevClose)/df.PrevClose
        df['LP'] = (df.Low - df.PrevClose)  /df.PrevClose
        df['CP'] = (df.Close - df.PrevClose)/df.PrevClose
        # df['HL'] = (df.High - df.Low)/df.PrevClose
        df['HL'] = df.HP - df.LP
        # print(df[0:4])
        print(df.iloc[1:4,8:])

        '''
        Input & Target
        '''
        self.n_input=6
        self.time_steps=10
        x=df.iloc[1:,8:].values
        print(x[0:3])
        print(x.shape)
        print(csvShape)
        print(df.shape)

if __name__ == "__main__":
    day='20181003'
    ticker='LABU'
    rawData=readRawData(ticker, day)
    print(rawData.shape)
    # hqReader = HqReader(ticker, day)
