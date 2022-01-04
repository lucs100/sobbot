import json, time, random, discord, admin
from datetime import datetime
from discord.ext import commands

INITIAL_COINS = 1000

# Classes

class CoinNotRegisteredError(commands.CommandError):
	pass

class CoinRecipientNotRegisteredError(commands.CommandError):
	pass

class SelfSendCoinsError(commands.CommandError):
    pass

class InsufficientCoinsError(commands.CommandError):
    pass

class SentLessThanZeroError(commands.CommandError):
    pass

class ClaimNotReadyError(commands.CommandError):
    def __init__(self, user0, time0):
        self.user = user0
        self.time = time0
    pass

class NonIntegerWagerError(commands.CommandError):
    def __init__(self, user0):
        self.user = user0

class PrereqItemRequiredError(commands.CommandError):
    def __init__(self, user0):
        self.user = user0

class LimitedItemAlreadyOwnedError(commands.CommandError):
    pass

class ItemDoesNotExistError(commands.CommandError):
    pass

class WagerTooLowError(commands.CommandError):
    pass
    
users = {}

# TODO: the shop kinda sucks?
# maybe certain things like luck mod should just be ranks
# like how mudae does it with eg. bronze is ONLY luck mod
shop = {}

with open('bot/resources/data/shop.json') as f:
    data = json.loads(f.read())
    shop = data

with open('bot/resources/data/private/userdata.json') as f:
    data = json.loads(f.read())
    users = data
    
def updateUserData(info):
    with open('bot/resources/data/private/userdata.json', 'w') as fp:
        json.dump(users, fp,  indent=4)
    with open('bot/resources/data/private/soblecoinTransactions.txt', 'a') as fp:
        fp.write(f"{info}  -  {str(time.ctime(time.time()))}\n") # logs transaction
    return True

def isUserRegistered(id):
    id = str(id)
    if id in users:
        if "coins" in users[id]:
            return users[id]["coins"]  # if name in user data
    return False

def getUserCoins(id):
    id = str(id)
    if id in users:
        if "coins" in users[id]:
            return users[id]["coins"]
    else:
        return False

def addRegistration(id):
    id = str(id)
    if id not in users:
        users[id] = {} # add id to userlist
    if "coins" in users[str(id)]:
        return False # already created
    users[id]["coins"] = 0
    users[id]["coins"] = INITIAL_COINS
    updateUserData(f"{id} - created soblecoin wallet with {INITIAL_COINS}")
    return True

def give(message, sender, recipient, value):
    sender, recipient = str(sender), str(recipient)
    if sender == recipient:
        raise SelfSendCoinsError
    if not isUserRegistered(sender):
        raise CoinNotRegisteredError
    elif not isUserRegistered(recipient):
        raise CoinRecipientNotRegisteredError
    if users[sender]["coins"] < value:
        raise InsufficientCoinsError
    if value <= 0:
        raise SentLessThanZeroError

    users[sender]["coins"] -= value
    users[recipient]["coins"] += value
    updateUserData(f"{sender} sent {value} coins to {recipient}")

    message.channel.send(f"Sent **{value}** soblecoins to <@!{recipient}>!")

def getUserLuck(id):
    id = str(id)
    try:
        return users[id]["properties"]["luck"]
    except: #key error
        return 0

async def claimHourly(message, userID):
    CLAIM_COOLDOWN = float(2 * 60 * 60)  # 2 hours
    value = 0
    userID = str(userID)
    if not isUserRegistered(userID):
        raise CoinNotRegisteredError # recipient error
    if "coinsLastClaimed" not in users[userID]:
        users[userID]["coinsLastClaimed"] = float(0) # create field
    last = users[userID]["coinsLastClaimed"]
    
    currentTime = time.time()
    timeElapsed = currentTime - last
    luck = getUserLuck(userID)
    value = (random.randint(50, 100) + (random.randint(3+luck, 10) + random.randint(3+luck, 10)) ** 2) 

    if timeElapsed >= CLAIM_COOLDOWN:
        if (getUserCoins(userID) + value) <= INITIAL_COINS:
            users[userID]["coins"] = INITIAL_COINS
            users[userID]["coinsLastClaimed"] = currentTime
            updateUserData(f"{userID} reset to {INITIAL_COINS} coins")
            await message.channel.send(f"<@!{userID}>, your balance was topped up to **{INITIAL_COINS}** soblecoins!")
        else:
            users[userID]["coins"] += value
            users[userID]["coinsLastClaimed"] = currentTime
            updateUserData(f"{userID} claimed {value} coins")
            await message.channel.send(f"<@!{userID}> claimed **{value}** soblecoins!")
    else:
        availableTime = datetime.fromtimestamp(last + CLAIM_COOLDOWN) # date magic to show the user when next claim ready
        currentTime = datetime.fromtimestamp(currentTime)
        nextTimeString = availableTime.strftime("%I:%M %p").lstrip("0")
        nextTimeString = "at " + nextTimeString
        if availableTime.day != currentTime.day:
            nextTimeString = "tomorrow " + nextTimeString
        raise ClaimNotReadyError(userID, nextTimeString) # time not passed

def messageBonus(id):
    id = str(id)
    x = 3 #numerator
    y = 10 #denominator
    coinsOnMessage = 1
    if not isUserRegistered(id):
        return False # no exception required, just quietly error out
    if isinstance(getUserCoins(id), int):
        luck = getUserLuck(id)
        if random.randint(x+luck, y) == x+luck:
            users[id]["coins"] += coinsOnMessage
            updateUserData(f"{id} earned {coinsOnMessage}")
    return True

async def luckyRoll(message, userID, value):
    try:
        value = int(value)
    except:
        raise NonIntegerWagerError
    if value <= 0:
        raise WagerTooLowError
    prizeDict = [0, 0, 0, 0.1, 0.1, 0.1, 0.2, 0.2, 0.25, 
    0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.9, 0.9,
    0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.9, 0.9,
    0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.9, 0.9,
    1, 1.05, 1.1, 1.1, 1.25, 1.5, 2, 2.5, 3, 5, 10] # random set of prize multipliers
    userID = str(userID)
    balance = getUserCoins(userID)
    if not isUserRegistered(userID):
        raise CoinNotRegisteredError
    if balance < value:
        raise InsufficientCoinsError
    luck = getUserLuck(userID)
    chances = 1 + luck
    pulled = []
    for i in range(chances):
        pulled.append(random.choice(prizeDict)) #multiple draws for each level of luck
    bonusRoll = random.randint(1, 6-luck) #luck has a CHANCE to give best draw
    if bonusRoll == 1:
        multi = max(pulled) #if bonus rolled, multi is max drawed
    else:
        if len(pulled) > 2: #otherwise, drop the lowest multi if 3 or more and pick random
            pulled.remove(min(pulled))
        multi = random.choice(pulled)
    change = int(value * multi) - value
    if isinstance(getUserCoins(userID), int):
        users[userID]["coins"] += change
        updateUserData(f"{userID} wagered {value} for a change of {change}")
    if multi > 1:
        await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi} and won {change} soblecoins!")
    elif multi == 1:
        await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! You didn't win or lose soblecoins.")
    elif multi < 1:
        await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! Sorry, you lost {change} soblecoins :frowning:")
    return True

def setupUserInventory(id):
    id = str(id)
    if "inventory" not in users[id]:
        users[id]["inventory"] = {}
    return True

def itemInInventory(itemID, userID):
    itemID, userID = str(itemID), str(userID)
    setupUserInventory(userID)
    if itemID in users[userID]["inventory"]:
        return users[userID]["inventory"][itemID]["count"]
    return 0

def getInventoryEmbed(userID):
    userID = str(userID)
    #primitive, implement this as an embed in the future
    message = f"**<@!{userID}>'s Inventory:**\n"
    if "inventory" in users[userID]:
        inventory = users[userID]["inventory"]
        for i in inventory:
            message += f"{getItemName(i)} - *{str(inventory[i]['count'])} owned*\n"
    else:
        message += "No items owned yet!"
    return message

def getItemName(itemID):
    itemID = str(itemID)
    if itemID in shop:
        return shop[itemID]["name"]
    return "Null item"

def addCustomProperty(name, value, userID):
    if "properties" not in users[userID]:
        users[userID]["properties"] = {}
    users[userID]["properties"][name] = value
    return True
    
def setCustomItemProperties(itemID, userID):
    if "properties" in shop[itemID]:
        for key, value in shop[itemID]["properties"].items():
            addCustomProperty(key, value, userID)
    return True

def checkPrereqs(itemID, userID):
    if "prereq" in shop[itemID]:
        if itemInInventory(shop[itemID]["prereq"], userID):
            return True
        else:
            return False
    return True

def checkLimited(itemID, userID):
    if "limited" in shop[itemID]:
        if itemInInventory(itemID, userID) != 0:
            return False #owned already
        else:
            return True
    return True

def getShop(message):
    #CAREFUL, this is gonna get hard to maintain if there are too many items
    #pagination?
    embed = discord.Embed(title="Sobble Shop", color=0xf42069)
    shopDescription = ""
    for i in range(1, len(shop)+1):
        n = str(i)
        px = admin.getGuildPrefix(message)
        shopDescription += f"**{shop[n]['name']}** ({px}buy {shop[n]['id']})   "
        if "limited" in shop[n]:
            shopDescription += f"`Limited item.`"
        shopDescription += "\n"
        shopDescription += f"Price - {shop[n]['price']} soblecoins\n"
        shopDescription += f"*{shop[n]['description']}*\n"
        if "prereq" in shop[n]:
            shopDescription += f"`Requires {shop[shop[n]['prereq']]['name']}.`\n"
        shopDescription += "\n"
    embed.description = shopDescription
    return embed

async def buyFromShop(message, itemID, userID):
    #may need to add custom item properties someday
    itemID, userID = str(itemID), str(userID)
    if itemID not in shop:
        raise ItemDoesNotExistError #id doesnt exist error
    if not isUserRegistered(userID):
        raise CoinNotRegisteredError #user not registered error
    setupUserInventory(userID)
    price = shop[itemID]["price"]
    if price > getUserCoins(userID):
        raise InsufficientCoinsError #insufficient funds error
    if not checkPrereqs(itemID, userID):
        raise PrereqItemRequiredError #prerequisite item required
    if not checkLimited(itemID, userID):
        raise LimitedItemAlreadyOwnedError #limited item already owned
    else:
        users[userID]["coins"] -= price  #subtract price from balance
    countOwned = itemInInventory(itemID, userID)
    if countOwned == 0:
        users[userID]["inventory"][itemID] = {"count": 1} #new entry for the item
        setCustomItemProperties(itemID, userID)
    else:
        users[userID]["inventory"][itemID]["count"] += 1 #item count increased by 1
        setCustomItemProperties(itemID, userID)
    updateUserData(f"{userID} purchased {shop[itemID]['name']} for {price}")
    await message.channel.send(f"<@!{message.author.id}>, you purchased a **{shop[itemID]['name']}**! You now own {countOwned + 1}.")
    return True