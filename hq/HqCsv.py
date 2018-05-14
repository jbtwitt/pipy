import pandas as pd

class HqCsv:
    def __init__(self, _ticker, csvFile):
        self._ticker = _ticker
        csv = pd.read_csv(csvFile, index_col=[0], parse_dates=False)
        csv['PrevClose'] = csv.Close.shift(1)
        csv['PrevVolume'] = csv.Volume.shift(1)
        csv['Change'] = (csv.Close - csv.PrevClose)/csv.PrevClose
        csv['VolChange'] = (csv.Volume - csv.PrevVolume)/csv.PrevVolume
        csv['HL'] = (csv.High - csv.Low)/csv.Low
        csv['CL'] = (csv.Close - csv.Low)/csv.Low
        csv['OL'] = (csv.Open - csv.Low)/csv.Low
        df = csv.reindex(index=csv.index[::-1])   # reverse date order
        df['No'] = range(len(df.index))
        self.dataFrame = df

    @property
    def ticker(self):
        return self._ticker

    @property
    def df(self):
        return self.dataFrame

    @property
    def rows(self):
        return self.dataFrame.iloc

if __name__ == "__main__":
    import json
    from datetime import datetime, timedelta
    from hqrobot import CsvFolder, CsvFileName
    ticker = 'ATHX'
    day = (datetime.now() + timedelta(days=-2)).strftime("%Y%m%d")
    hqConf = json.load(open('hqrobot.json'))
    csvFolder = CsvFolder.format(hqConf['repo'], day)
    csvFile = CsvFileName.format(csvFolder, ticker)
    hqCsv = HqCsv(ticker, csvFile)

    idx0 = hqCsv.df.index[0]
    print(idx0)
    df4 = hqCsv.df[0:4].Close.sort_values(ascending=False)
    # df4 = hqCsv.df[0:4].sort_values(by='Close', ascending=True)
    df4['No'] = range(len(df4.index))
    print(df4)
    print(df4.loc[idx0])
    # for row in hqCsv.rows:
    #     print(row.index)
    #     break
