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
        self.dataFrame = csv.reindex(index=csv.index[::-1])   # reverse date order

    @property
    def ticker(self):
        return self._ticker

    @property
    def df(self):
        return self.dataFrame

    @property
    def rows(self):
        return self.dataFrame.loc