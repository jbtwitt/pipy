import numpy as np
import pandas as pd

class HqData:
  def __init__(self, ticker='VSTM', hqdate='hq20200114'):
    self.ticker = ticker
    self.hqdate = hqdate
    csv_path = r'\jbdata\hqrobot\csv\%s\%s.y.csv' % (hqdate, ticker)
    df = pd.read_csv(csv_path)

    df['PrevClose'] = df["Adj Close"].shift(1)
    df['PrevVolume'] = df.Volume.shift(1)

    df['OP'] = (df.Open - df.PrevClose) / df.PrevClose
    df['CP'] = (df["Adj Close"] - df.PrevClose) / df.PrevClose
    df['HP'] = (df.High - df.PrevClose)  / df.PrevClose
    df['LP'] = (df.Low - df.PrevClose)  / df.PrevClose
    df['HL'] = (df.High - df.Low) / df.PrevClose
    df['VolChange'] = (df.Volume - df.PrevVolume) / df.PrevVolume
    self.df = df

  def getFeatureData(self, cols=['OP', 'CP', 'HP', 'LP']):
    # hq_features = df[['OP', 'CP', 'HP', 'LP', 'HL', 'VolChange']]
    featureData = self.df[cols]
    featureData.index = self.df.Date
    print(featureData.head())
    print(featureData.tail())
    # remove first row with NaN values
    return featureData.values[1:]

  def timeSeriesData(self, xCols, yCols, trainSize=800, valSize=200, tsSize=10, futureTsSize=1):
    x_data = self.getFeatureData(xCols)
    y_labels = self.getFeatureData(yCols)
    print("dataset shape", x_data.shape)
    print(x_data[0:3])
    print("lable shape", y_labels.shape)
    print(y_labels[len(y_labels) - 3:])

    def genData(idx_start, idx_end):
      x, y = ([], [])
      for i in range(idx_start, idx_end):
        end = i + tsSize
        x.append(x_data[range(i, end)])
        y.append(y_labels[range(end, end + futureTsSize)])
      return x, y

    i_start = len(x_data) - tsSize - trainSize -valSize - (futureTsSize - 1)
    i_end = i_start + trainSize
    x_train, y_train = genData(i_start, i_end)

    i_start = i_end
    i_end = len(x_data) - tsSize - (futureTsSize - 1)
    x_val, y_val = genData(i_start, i_end)

    return np.array(x_train), np.array(y_train), np.array(x_val), np.array(y_val)


def test():
  hqDataClass = HqData()
  trainSize, valSize, tsSize, futureTsSize = (900, 300, 10, 2)
  x_train, y_train, x_val, y_val = hqDataClass.timeSeriesData(
            ['OP', 'CP', 'HP', 'LP'], ['CP'], trainSize, valSize, tsSize, futureTsSize)
  print(x_train.shape, y_train.shape, x_val.shape, y_val.shape)
  print("x_train last row", x_train[-1], y_train[-1])
  print("x_val first row", x_val[1])
  print("x_val last row", x_val[-1], y_val[-1])

def testGetFeatureDate():
  hqdate = 'hq20200114'
  ticker = 'ATHX'
  hqDataClass = HqData(ticker, hqdate)
  dataset = hqDataClass.getFeatureData()
  print("dataset shape", dataset.shape)
  print(dataset[0:3])

  labels = hqDataClass.getFeatureData(['CP'])
  print("lable shape", labels.shape)
  print(labels[0:3])

if __name__ == "__main__":
    test()
    testGetFeatureDate()