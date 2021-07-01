from datetime import datetime, timedelta

import discord, json
import yfinance as yf

class Stock:
    def __init__(self, symbol):
        data = yf.Ticker(symbol)
        try:
            self.symbol = data.info["symbol"]
            self.name = data.info["shortName"]
            self.currentPrice = float(data.info["regularMarketPrice"])
            self.openingPrice = float(data.info["open"])
            self.dailyChange = round(self.currentPrice - self.openingPrice, 2)
            self.dailyChangePercent = round(((self.dailyChange*100)/self.openingPrice), 2)
            self.volume = int(data.info["volume"])
            self.averageVolume = int(data.info["averageVolume"])
            self.relativeVolume = self.volume / self.averageVolume
            self.logo = data.info["logo_url"]
        except KeyError:
            raise ValueError(f"The symbol {symbol} doesn't exist." +
            "Try using the safelyCreateStock pseudoconstructor.")

users = {}

with open('bot/resources/data/private/userdata.json') as f:
    data = json.loads(f.read())
    users = data
    
def updateUserData():
    with open('bot/resources/data/private/userdata.json', 'w') as fp:
        json.dump(users, fp,  indent=4)
    return True

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
    formatTuple = (time, abs(change), abs(percent))
    if percent > 0:
        if percent > 5:
            if percent > 10:
                if percent > 20:
                    return "{} {:.2f} point gain. (+{:.2f}%!!!)\n"    .format(*formatTuple)
                return "{} {:.2f} point gain. (+{:.2f}%!!)\n".format(*formatTuple)
            return "{} {:.2f} point gain. (+{:.2f}%!)\n".format(*formatTuple)
        return "{} {:.2f} point gain. (+{:.2f}%)\n".format(*formatTuple)
    elif percent < 0:
        return "{} {:.2f} point loss. (-{:.2f}%)\n".format(*formatTuple)
    elif percent == 0:
        return f"{time} change of 0 from open."

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

def getPhaseChangeTiming(phase=(getMarketPhase())):
    now = datetime.now()
    if phase == 0:
        comp = now.replace(hour=4, minute=0, second=0, microsecond=0)
    elif phase == 1:
        comp = now.replace(hour=9, minute=30, second=0, microsecond=0)
    elif phase == 2: 
        comp = now.replace(hour=16, minute=0, second=0, microsecond=0)
    elif phase == 3: 
        comp = now.replace(hour=20, minute=0, second=0, microsecond=0)
    else:
        comp = now.replace(hour=4, minute=0, second=0, microsecond=0)
    totalSeconds = int((comp-now).total_seconds())
    if totalSeconds < 0:
        totalSeconds += 24*60*60 #timedeltas become negative sometimes
    hours, remainder = divmod(totalSeconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0:
        if minutes == 0:
            return f"{seconds}s"
        return f"{minutes}m {seconds}s"
    return f"{hours}h {minutes}m {seconds}s"

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
        ("It's currently after hours.", "after-hours ends"),
        ("The market is currently closed.", "premarket begins")
    ]
    description = f"*{phases[phase][0]}* "
    if phase != 2:
        description += "*Data as of 4pm.*"
    description += f"\n\n{stock.symbol} last traded at **{stock.currentPrice}**, "
    description += f"and opened at {stock.openingPrice}.\n"
    description += parseChange(stock.dailyChange, stock.dailyChangePercent, (phase==2)) + "\n"
    if stock.dailyChange < 0:
        color = discord.Color.from_rgb(188, 69, 69)
    elif stock.dailyChange > 0:
        color = discord.Color.from_rgb(95, 200, 109)
    else:
        color = discord.Color.from_rgb(173, 173, 173)
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=(f"{(getPhaseChangeTiming(phase))} until {phases[phase][1]}."), icon_url=stock.logo)
    #embed.set_image(url=stock.logo)
    return embed

def addRegistration(id):
    id = str(id)
    if id not in users:
        users[id] = {} # add id to userlist
    if "portfolio" in users[str(id)]:
        return False # already created
    updateUserData()
    return True

def userPortfolioExists(id):
    if "portfolio" in users[str(id)]:
        return True
    return False

def createPortfolio(id):
    id = str(id)
    if "portfolio" in users[id]:
        return False
    users[id]["portfolio"] = {}
    updateUserData()
    return True

def existsInPortfolio(name, id):
    return (userPortfolioExists(str(id)) and (name in users[str(id)]["portfolio"]))

def updatePortfolio(stock, id, count):
    id = str(id)
    if not userPortfolioExists(id):
        return "reg"
    stock = safelyCreateStock(stock)
    if stock == None:
        return "sym"
    if count < 0:
        return "neg"
    elif count == 0:
        if existsInPortfolio(stock.name, id):
            users[id]["portfolio"].pop(stock.name)
            updateUserData()
            return "delS"
        else:
            return "delF"
    else:
        users[id]["portfolio"][stock.name] = count
        updateUserData()
        return "ok"

print(createPortfolio(312012475761688578))