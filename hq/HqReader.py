import pandas as pd
import numpy as np

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
    print(df.iloc[1:5,8:])
    # npArray=df.iloc[1:,8:].values
    # return np.rot90(npArray, )
    # df=df.iloc[1:,8:]
    # df = df.T #rotate 90 degree
    # print(df.shape)
    # print(df)
    return df.iloc[1:,8:].values

class HqReader:
    def __init__(self,ticker,day):
        self.ticker=ticker
        self.day=day
        rawData=readRawData(ticker, day)
        rows, n_input = rawData.shape
        print(rawData.shape, rows, n_input)
        # print(rawData)
        '''
        Input & Target
        '''
        self.n_input=6
        self.time_steps=3
        x=rawData.reshape((1,rows,n_input))
        print(x.shape)
        # print(x)
        print(x[0,0:self.time_steps].shape)
        inputSize=2
        batchInput=np.empty((inputSize,self.time_steps,n_input))#,dtype=float)
        # batchInput=np.array()
        for i in range(inputSize):
            # np.append(batchInput,x[0,i:self.time_steps+i])
            batchInput[i]=x[0,i:self.time_steps+i]
            # print(x[0,i:self.time_steps+i])
        print(batchInput.shape)
        # print(batchInput[-1])
        print(batchInput)

if __name__ == "__main__":
    day='20181003'
    ticker='LABU'
    hqReader = HqReader(ticker, day)
