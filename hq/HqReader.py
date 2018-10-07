import pandas as pd
import numpy as np

CsvFileNameFormat="/gitrepo/robotRepo/hq{}/{}.y.csv"
VOLUME_REDUCER=1000.0
def readRawData(ticker, day):
    csvFile=CsvFileNameFormat.format(day, ticker)
    df = pd.read_csv(csvFile, index_col=[0], parse_dates=False)
    csvShape=df.shape
    df['PrevClose'] = df.Close.shift(1)
    df['PrevVolume'] = df.Volume.shift(1)

    df['VolChange'] = (df.Volume - df.PrevVolume)/df.PrevVolume/VOLUME_REDUCER
    df['OP'] = (df.Open - df.PrevClose) /df.PrevClose
    df['HP'] = (df.High - df.PrevClose)/df.PrevClose
    df['LP'] = (df.Low - df.PrevClose)  /df.PrevClose
    df['CP'] = (df.Close - df.PrevClose)/df.PrevClose
    # df['HL'] = (df.High - df.Low)/df.PrevClose
    df['HL'] = df.HP - df.LP
    # print(df[0:4])
    print(df.iloc[1:15,8:])
    # print(df.iloc[1:5,12]) # = df[1:5].CP
    # npArray=df.iloc[1:,8:].values
    # return np.rot90(npArray, )
    # df=df.iloc[1:,8:]
    # df = df.T #rotate 90 degree
    # print(df.shape)
    # print(df)
    input_raw_data=df.iloc[1:,8:].values
    # target_raw_data=df.iloc[1:,12]
    target_raw_data=df[1:].CP
    return  input_raw_data, target_raw_data

class HqReader:
    def __init__(self,ticker,day):
        self.ticker=ticker
        self.day=day
        input_raw_data, target_raw_data=readRawData(ticker, day)
        print('input_raw_data shape',input_raw_data.shape)
        print('target_raw_data shape', target_raw_data.shape)
        self.rows, self.n_input = input_raw_data.shape
        # reshape the csv raw data by 90 rotate
        self.input_raw_data=input_raw_data.reshape((1,self.rows,self.n_input))
        self.target_raw_data=target_raw_data
        # print(self.input_reshape(batch_size=2,time_steps=3,n_input=self.n_input))
        # print(self.target_reshape(batch_size=2,n_input=2))
        '''
        Input & Target
        '''
        """
        self.n_input=6
        self.time_steps=3
        x=input_raw_data.reshape((1,rows,n_input))
        print(x.shape)
        # print(x)
        inputSize=2
        batchInput=np.empty((inputSize,self.time_steps,n_input))
        # batchInput=np.array()
        for i in range(inputSize):
            # np.append(batchInput,x[0,i:self.time_steps+i])
            batchInput[i]=x[0,i:self.time_steps+i]
            # print(x[0,i:self.time_steps+i])
        print(batchInput.shape)
        # print(batchInput[-1])
        print(batchInput)
        """

    def split_data(self,train_size,time_steps,n_classes):
        x=self.input_reshape(train_size,time_steps,self.n_input)
        y=self.target_reshape(n_classes)
        return x, y[time_steps:time_steps+train_size]

    def input_reshape(self,batch_size,time_steps,n_input):
        x=np.empty((batch_size,time_steps,n_input))
        for i in range(batch_size):
            x[i]=self.input_raw_data[0,i:time_steps+i]
        return x

    def target_reshape(self,n_classes):
        batch_size=self.rows-n_classes
        y=np.empty((batch_size,n_classes))
        for i in range(batch_size):
            y[i]=self.target_raw_data[i:i+n_classes]
        return y

if __name__ == "__main__":
    day='20181003'
    ticker='LABU'
    hqReader=HqReader(ticker, day)
    train_x,train_y=hqReader.split_data(train_size=100,time_steps=time_steps,n_classes=n_classes)
    print(train_x.shape)
    print(train_y.shape)
    # print(train_x[0])
    # print(train_y[0])
