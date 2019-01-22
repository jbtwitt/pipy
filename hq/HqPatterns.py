from enum import Enum
HqAlertType0 = 'bullish engulfing'
HqAlertType1 = 'nDaysLow within 10 days and bullish engulfing'

class Pattern(Enum):
    NDaysCloseLow = -1           #possible trend reversed
    NDaysCloseHigh = 1           #possible trend reversed
    # NDaysVolumeHigh = 2
    # bull
    BullishEngulfing = 11
    MorningStar = 12
    ThreeLineStrike = 13
    # bear
    Hammer = 13
    BearishEngulfing = -11
    EveningStar = -12

class HqPatterns:
    def __init__(self):
        # self._date = date
        self._patterns = []
        self._bullishEngulfings = []

    def addPattern(self, ticker, hqMeta, pattern, nDaysHL=None):
        obj = {'ticker': ticker,
            'hqMeta': hqMeta,
            'pattern': pattern.name,
            'nDaysHL': nDaysHL}
        self._patterns.append(obj)

    @property
    def patterns(self):
        return self._patterns

if __name__ == '__main__':
    hqPatterns = HqPatterns()
    hqPatterns.addPattern('LABU', Pattern.BullishEngulfing, 0.03)
    print(hqPatterns.patterns)
