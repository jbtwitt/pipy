from enum import Enum
HqAlertType0 = 'bullish engulfing'
HqAlertType1 = 'nDaysLow within 10 days and bullish engulfing'

class Pattern(Enum):
    NDaysLow = 0
    BullishEngulfing = 1
    MorningStar = 2

class HqPatterns:
    def __init__(self):
        # self._date = date
        self._patterns = []
        self._bullishEngulfings = []
        self._bearishEngulfings = []
        self._morningStars = []

    def addPattern(self, ticker, pattern, stickOC, nDaysHL=None):
        self._patterns.append({
            'ticker': ticker,
            'pattern': pattern.name,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    def addBullishEngulfing(self, ticker, stickOC, nDaysHL=None):
        self._bullishEngulfings.append({
            'ticker': ticker,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    def addMorningStar(self, ticker, stickOC, nDaysHL=None):
        self._morningStars.append({
            'ticker': ticker,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    @property
    def patterns(self):
        return self._patterns

    @property
    def bearishEngulfings(self):
        return self._bearishEngulfings

    @property
    def bullishEngulfings(self):
        return self._bullishEngulfings

    @property
    def morningStars(self):
        return self._morningStars

if __name__ == '__main__':
    hqPatterns = HqPatterns()
    hqPatterns.addPattern('LABU', Pattern.BullishEngulfing, 0.03)
    print(hqPatterns.patterns)
