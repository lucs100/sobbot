from datetime import datetime, timedelta
from forex_python.converter import CurrencyRates as fx
import discord, json
import asyncio
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
            self.currency = data.info["currency"]
        except KeyError:
            raise ValueError(f"The symbol {symbol} doesn't exist." +
            "Try using the safelyCreateStock pseudoconstructor.")

users = {}

with open('bot/resources/data/private/userdata.json') as f:
    data = json.loads(f.read())
    users = data

def getStockPrice(symbol):
    return yf.Ticker(symbol).info["regularMarketPrice"]
    
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

def parseChangeColor(value): # eventually make this change saturation based on magnitude
    if value < 0:
        return discord.Color.from_rgb(188, 69, 69)
    elif value > 0:
        return discord.Color.from_rgb(95, 200, 109)
    else:
        return discord.Color.from_rgb(173, 173, 173)

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
        ("It's currently after hours.", "after hours ends"),
        ("The market is currently closed.", "premarket begins")
    ]
    description = f"*{phases[phase][0]}* "
    if phase != 2:
        description += "*Data as of 4pm.*"
    description += f"\n\n{stock.symbol} last traded at **{stock.currentPrice:.2f}**, "
    description += f"and opened at {stock.openingPrice:.2f}.\n"
    description += parseChange(stock.dailyChange, stock.dailyChangePercent, (phase==2)) + "\n"
    color = parseChangeColor(stock.dailyChange)
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
    stock = stock.upper()
    id = str(id)
    if count < 0:
        return "neg"
    if not userPortfolioExists(id):
        return "reg"
    if stock == None:
        return "sym"
    elif count == 0:
        if existsInPortfolio(stock, id):
            users[id]["portfolio"].pop(stock)
            updateUserData()
            return "delS"
        else:
            return "delF"
    else:
        stock = safelyCreateStock(stock)
        users[id]["portfolio"][stock.symbol] = count
        updateUserData()
        if count == 1:
            return "ok"
        return "ok2"

def parseChangeValue(change, annotation="", hasBrackets=True, roundTo=2, prefix=""):
    if hasBrackets:
        if change == 0:
            return f"(±{prefix}0{annotation})"
        elif change > 0:
            return f"(+{prefix}{change:.2f}{annotation})"
        elif change < 0:
            return f"(-{prefix}{abs(change):.2f}{annotation})"
    else:
        if change == 0:
            return f"±{prefix}0{annotation}"
        elif change > 0:
            return f"+{prefix}{change:.2f}{annotation}"
        elif change < 0:
            return f"-{prefix}{abs(change):.2f}{annotation}"

async def getUserPortfolioEmbed(message):
    user = message.author
    id = str(user.id) 
    total = 0
    exch = fx().get_rate("USD", "CAD")
    dailyChange = 0
    name = user.nick
    if name == None:
        name = user.name
    if not userPortfolioExists(id):
        return "reg"
    data = users[id]["portfolio"]
    if data == {}:
        return "empty"

    title = "Fetching data..."
    description = ""
    pfEmbed = discord.Embed(description=description, title=title)
    sobMessage = await message.channel.send(embed=pfEmbed)

    for sym, shares in data.items():
        stock = Stock(sym)
        description += f"**{stock.symbol}** - **{shares}** shares (currently *{stock.currentPrice:.2f}* {stock.currency}, "
        description += f"{parseChangeValue(stock.dailyChange, ' today', False)})\n"
        total += (shares * stock.currentPrice) * exch
        dailyChange += (shares * stock.dailyChange) * exch

        pfEmbed.description = description
        await sobMessage.edit(embed=pfEmbed)
        del stock

    pfEmbed.title = f"Current Value: **${total:,.2f}**\t"
    dailyChangePercent = (dailyChange*100)/total
    pfEmbed.title += f"({parseChangeValue(dailyChange, ' today', False, prefix='$')}, {parseChangeValue(dailyChangePercent, '%', False)})"
    pfEmbed.set_footer(text=f"{name}'s portfolio, title values in CAD.\nData may be incorrect, API upgrade coming soon.", icon_url=user.avatar_url) # hardcoded to CAD for now
    pfEmbed.color = parseChangeColor(dailyChange)
    await sobMessage.edit(embed=pfEmbed)
    return True