from numpy.lib.arraysetops import isin
import yfinance as yf
from datetime import datetime, timedelta
import discord

class Stock:
    def __init__(self, symbol):
        data = yf.Ticker(symbol)
        try:
            self.symbol = data.info["symbol"]
            self.name = data.info["shortName"]
            self.currentPrice = float(data.info["regularMarketPrice"])
            self.openingPrice = float(data.info["open"])
            self.change = round(self.currentPrice - self.openingPrice, 2)
            self.changePercent = round(((self.change*100)/self.openingPrice), 2)
            self.volume = int(data.info["volume"])
            self.averageVolume = int(data.info["averageVolume"])
            self.relativeVolume = self.volume / self.averageVolume
            self.logo = data.info["logo_url"]
        except KeyError:
            raise ValueError(f"The symbol {symbol} doesn't exist." +
            "Try using the safelyCreateStock pseudoconstructor.")

def safelyCreateStock(symbol):
    data = yf.Ticker(symbol)
    try:
        temp = data.info["symbol"]
    except KeyError:
        return None
    return Stock(symbol)

def parseMarketPhase(phase):
    pass

def parseChange(change, percent, open):
    if open:
        time = "This is a"
    else:
        time = "Today represented a"
    if percent > 0:
        if percent > 5:
            if percent > 10:
                if percent > 20:
                    return "{} {:.2f} point gain. (+{:.2f}%!!!)\n"    .format(time, change, percent)
                return "{} {:.2f} point gain. (+{:.2f}%!!)\n".format(time, change, percent)
            return "{} {:.2f} point gain. (+{:.2f}%!)\n".format(time, change, percent)
        return "{} {:.2f} point gain. (+{:.2f}%)\n".format(time, change, percent)
    elif percent < 0:
        return "{} {:.2f} point loss. (-{:.2f}%)\n".format(time, change, percent)
    elif percent == 0:
        return f"{time} change of 0 from open."

def getPhaseChangeTiming(phase):
    now = datetime.now()
    if phase == 0:
        comp = now.replace(hour=4, minute=0, second=0, microsecond=0)
    elif phase == 1:
        comp = now.replace(hour=9, minute=30, second=0, microsecond=0)
    elif phase == 2: 
        comp = now.replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        comp = now.replace(hour=20, minute=0, second=0, microsecond=0)
    totalSeconds = int((comp-now).total_seconds())
    hours, remainder = divmod(totalSeconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0:
        if minutes == 0:
            return f"{seconds}s"
        return f"{minutes}m:{seconds}s"
    return f"{hours}h:{minutes}m:{seconds}s"

def getMarketPhase(now = datetime.now()):
    preOpen = now.replace(hour=3, minute=30, second=0, microsecond=0)
    marketOpen = now.replace(hour=9, minute=30, second=0, microsecond=0)
    marketClose = now.replace(hour=16, minute=0, second=0, microsecond=0)
    afterHourClose = now.replace(hour=20, minute=0, second=0, microsecond=0)

    if (now < preOpen):
        return 0 # Market closed
    elif (now < marketOpen):
        return 1 # Premarket
    elif (now < marketClose):
        return 2 # Market open
    elif (now < afterHourClose):
        return 3 # After hours
    else:
        return 4 # Market closed

def createStockEmbed(stock):
    if not isinstance(stock, Stock):
        stock = safelyCreateStock(stock)
        if stock == None:
            return stock
    title = f"**{stock.symbol}** - {stock.name}"
    phase = getMarketPhase()
    phases = [
        ("The market is currently closed.", "premarket begins"),
        ("It's currently premarket.", "market open"),
        ("Markets are open.", "market close"),
        ("It's currently after hours.", "after-hours ends")
    ]
    description = f"*{phases[phase][0]}* "
    if phase != 2:
        description += "Data might not be too accurate :frowning:"
    description += f"\n\n{stock.symbol} last traded at **{stock.currentPrice}**, "
    description += f"and opened at {stock.openingPrice}.\n"
    description += parseChange(stock.change, stock.changePercent, (phase==2)) + "\n"
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=(f"{(getPhaseChangeTiming(phase))} until {phases[phase][1]}."), icon_url=stock.logo)
    #embed.set_image(url=stock.logo)
    return embed