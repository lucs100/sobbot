import yfinance as yf
from datetime import datetime

#class??????

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

def getTicker(symbol):
    return yf.Ticker(symbol)

def getBasicData(ticker):
    data = dict([])
    data["symbol"] = ticker.info["symbol"]
    data["name"] = ticker.info["shortName"]
    data["price"] = float(ticker.info["regularMarketPrice"])
    data["open"] = float(ticker.info["open"])
    data["change"] = round(data["price"] - data["open"], 2)
    data["changePercent"] = round(((data["change"]*100)/data["open"]), 2)
    data["volume"] = int(ticker.info["volume"])
    data["avgVolume"] = int(ticker.info["averageVolume"])
    data["relativeVolume"] = data["volume"] / data["avgVolume"]
    return data

gme = getTicker("gme")
print(getBasicData(gme))

print(getMarketPhase())