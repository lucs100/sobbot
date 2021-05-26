import json, time, random, discord
from datetime import datetime

startingCoins = 1000

users = {}

shop = {}

with open('bot/resources/data/shop.json') as f:
    data = json.loads(f.read())
    shop = data

with open('bot/resources/data/userdata.json') as f:
    data = json.loads(f.read())
    users = data
    
def updateUserData(info):
    with open('bot/resources/data/userdata.json', 'w') as fp:
        json.dump(users, fp,  indent=4)
    with open('bot/resources/data/soblecoinTransactions.txt', 'a') as fp:
        fp.write(f"{info}  -  {str(time.ctime(time.time()))}\n") # logs transaction
    return True

def isUserRegistered(id):
    id = str(id)
    if id in users:
        if "coins" in users[id]:
            return users[id]["coins"]  # if lol name in user data
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
    users[id]["coins"] = startingCoins
    updateUserData(f"{id} - created soblecoin wallet with {startingCoins}")
    return True

def give(sender, recipient, value):
    sender, recipient = str(sender), str(recipient)
    if sender == recipient:
        return 4 # sender = reciever

    if not isUserRegistered(sender):
        return 3 # sender error
    elif not isUserRegistered(recipient):
        return 1 # recipient error

    if users[sender]["coins"] < value or value <= 0:
        return 2 # insufficient soblecoins

    users[sender]["coins"] -= value
    users[recipient]["coins"] += value
    updateUserData(f"{sender} sent {value} coins to {recipient}")
    return 0

def getUserLuck(id):
    id = str(id)
    try:
        return users[id]["properties"]["luck"]
    except: #key error
        return 0

def claimHourly(id):
    claimCooldown = float(2 * 60 * 60)  # 2 hours
    value = 0
    id = str(id)
    if not isUserRegistered(id):
        return False, -1 # recipient error
    if "coinsLastClaimed" not in users[id]:
        users[id]["coinsLastClaimed"] = float(0) # create field
    last = users[id]["coinsLastClaimed"]
    
    currentTime = time.time()
    timeElapsed = currentTime - last
    luck = getUserLuck(id)
    value = (random.randint(50, 100) + (random.randint(3+luck, 10) + random.randint(3+luck, 10)) ** 2) 

    if timeElapsed >= claimCooldown:
        if (getUserCoins(id) + value) <= 1000:
            users[id]["coins"] = 1000
            users[id]["coinsLastClaimed"] = currentTime
            updateUserData(f"{id} reset to 1000 coins")
            return True, 1000
        else:
            users[id]["coins"] += value
            users[id]["coinsLastClaimed"] = currentTime
            updateUserData(f"{id} claimed {value} coins")
            return True, value
    else:
        availableTime = datetime.fromtimestamp(last + claimCooldown) # date magic to show the user when next claim ready
        currentTime = datetime.fromtimestamp(currentTime)
        nextTimeString = availableTime.strftime("%I:%M %p").lstrip("0")
        nextTimeString = "at " + nextTimeString
        if availableTime.day != currentTime.day:
            nextTimeString = "tomorrow " + nextTimeString
        return False, nextTimeString # time not passed

def messageBonus(id):
    id = str(id)
    x = 3 #numerator
    y = 10 #denominator
    coinsOnMessage = 1
    if not isUserRegistered(id):
        return False
    if isinstance(getUserCoins(id), int):
        luck = getUserLuck(id)
        if random.randint(x+luck, y) == 1:
            users[id]["coins"] += coinsOnMessage
            updateUserData(f"{id} earned {coinsOnMessage}")
    return True

def luckyRoll(id, value):
    try:
        value = int(value)
    except:
        return "int", 0, 0    # errors return a code and two placeholders
    prizeDict = [0, 0, 0, 0.1, 0.1, 0.1, 0.2, 0.2, 0.25, 
    0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.9, 0.9,
    0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.9, 0.9,
    0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 0.75, 0.9, 0.9,
    1, 1.05, 1.1, 1.1, 1.25, 1.5, 2, 2.5, 3, 5, 10] # random set of prize multipliers
    id = str(id)
    balance = getUserCoins(id)
    if not isUserRegistered(id):
        return "reg", 0, 0
    if balance < value:
        return "insuff", balance, 0
    luck = getUserLuck(id)
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
    if isinstance(getUserCoins(id), int):
        users[id]["coins"] += change
        updateUserData(f"{id} wagered {value} for a change of {change}")
    return "ok", abs(change), multi

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

def getShop():
    #CAREFUL, this is gonna get hard to maintain if there are too many items
    #pagination?
    embed = discord.Embed(title="Sobble Shop", color=0xf42069)
    shopDescription = ""
    for i in range(1, len(shop)+1):
        n = str(i)
        shopDescription += f"**{shop[n]['name']}** (s!buy {shop[n]['id']})   "
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

def buyFromShop(itemID, userID):
    #may need to add custom item properties someday
    itemID, userID = str(itemID), str(userID)
    if itemID not in shop:
        return "exist", 0 #id doesnt exist error
    if not isUserRegistered(userID):
        return "reg", 0 #user not registered error
    setupUserInventory(userID)
    price = shop[itemID]["price"]
    if price > getUserCoins(userID):
        return "broke", getUserCoins(userID) #insufficient funds error
    if not checkPrereqs(itemID, userID):
        return "prereq", 0 #prerequisite item required
    if not checkLimited(itemID, userID):
        return "limit", 0 #limited item already owned
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
    return shop[itemID]["name"], countOwned + 1 