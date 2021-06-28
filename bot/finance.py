from numpy.lib.arraysetops import isin
import yfinance as yf
from datetime import datetime

class Stock:
    def __init__(self, symbol):
        data = yf.Ticker(symbol)
        self.symbol = data.info["symbol"]
        self.name = data.info["shortName"]
        self.currentPrice = float(data.info["regularMarketPrice"])
        self.openPrice = float(data.info["open"])
        self.change = round(self.currentPrice - self.openPrice, 2)
        self.changePercent = round(((self.change*100)/self.openPrice), 2)
        self.volume = int(data.info["volume"])
        self.averageVolume = int(data.info["averageVolume"])
        self.relativeVolume = self.volume / self.averageVolume


def getMarketPhase(now = datetime.now()):
    preOpen = now.replace(hour=3, minute=30, second=0, microsecond=0)
    marketOpen = now.replace(hour=9, minute=30, second=0, microsecond=0)
    marketClose = now.replace(hour=16, minute=0, second=0, microsecond=0)
    afterHourClose = now.replace(hour=20, minute=0, second=0, microsecond=0)

    if (now < preOpen):
        return("Market closed")
    elif (now < marketOpen):
        return("Premarket")
    elif (now < marketClose):
        return("Market open")
    elif (now < afterHourClose):
        return("After hours")
    else:
        return("Market closed")

gme = Stock("gme")
print(gme)

print(getMarketPhase())