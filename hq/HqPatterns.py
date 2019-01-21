from enum import Enum
HqAlertType0 = 'bullish engulfing'
HqAlertType1 = 'nDaysLow within 10 days and bullish engulfing'

class Pattern(Enum):
    NDaysCloseLow = -1           #possible trend reversed
    NDaysCloseHigh = 1           #possible trend reversed
    # NDaysVolumeHigh = 2
    BullishEngulfing = 11    #bull
    MorningStar = 12         #bull
    Hammer = 13
    BearishEngulfing = -11

class HqPatterns:
    def __init__(self):
        # self._date = date
        self._patterns = []
        self._bullishEngulfings = []

    def addPattern(self, ticker, date, pattern, stickOC, nDaysHL=None):
        self._patterns.append({
            'ticker': ticker,
            'date': date,
            'pattern': pattern.name,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    def addBullishEngulfing(self, ticker, stickOC, nDaysHL=None):
        self._bullishEngulfings.append({
            'ticker': ticker,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    @property
    def patterns(self):
        return self._patterns

    @property
    def bullishEngulfings(self):
        return self._bullishEngulfings

if __name__ == '__main__':
    hqPatterns = HqPatterns()
    hqPatterns.addPattern('LABU', Pattern.BullishEngulfing, 0.03)
    print(hqPatterns.patterns)
