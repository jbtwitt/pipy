HqAlertType0 = 'bullish engulfing'
HqAlertType1 = 'nDaysLow within 10 days and bullish engulfing'

class HqPatterns:
    def __init__(self):
        # self._date = date
        self._bullishEngulfings = []
        self._bearishEngulfings = []
        self._morningStar = []

    def addBullishEngulfing(self, ticker, stickOC, nDaysHL=None):
        self._bullishEngulfings.append({
            'ticker': ticker,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    def addMorningStar(self, ticker, stickOC, nDaysHL=None):
        self._morningStar.append({
            'ticker': ticker,
            'stickOC': stickOC,
            'nDaysHL': nDaysHL})

    @property
    def bearishEngulfings(self):
        return self._bearishEngulfings

    @property
    def bullishEngulfings(self):
        return self._bullishEngulfings

    @property
    def morningStars(self):
        return self._morningStar

if __name__ == '__main__':
    hqPatterns = HqPatterns(20190102)
    hqPatterns.addBullishEngulfing('LABU',1)
    hqPatterns.addBullishEngulfing('TQQQ', 1,2)
    print(hqPatterns.bullishEngulfings)
