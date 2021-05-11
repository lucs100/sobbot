import json, time, random

startingCoins = 1000

users = {}

with open('bot/resources/data/userdata.json') as f:
    data = json.loads(f.read())
    users = data
    
def updateUserData(info):
    with open('bot/resources/data/userdata.json', 'w') as fp:
        json.dump(users, fp,  indent=4)
    with open('bot/resources/data/soblecoinTransactions.txt', 'a') as fp:
        fp.write(f"{info}  -  {str(time.ctime(time.time()))}\n")
    return True

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
        users[id] = {}
    if "coins" in users[str(id)]:
        return False
    users[id]["coins"] = 0
    users[id]["coins"] = startingCoins
    updateUserData(f"{id} - created soblecoin wallet with {startingCoins}")
    return True

def give(sender, recipient, value):
    sender, recipient = str(sender), str(recipient)
    if sender == recipient:
        return 4 #sender = reciever

    if sender not in users or "coins" not in users[sender]:
        return 3 #sender error
    elif recipient not in users or "coins" not in users[recipient]:
        return 1 #recipient error

    if users[sender]["coins"] < value or value <= 0:
        return 2 #insufficient soblecoins

    users[sender]["coins"] -= value
    users[recipient]["coins"] += value
    updateUserData(f"{sender} sent {value} coins to {recipient}")
    return 0

def claimHourly(id):
    claimCooldown = float(2 * 60 * 60)  # 2 hours
    value = 0
    id = str(id)
    if id not in users or "coins" not in users[id]:
        return False, -1 #recipient error
    if "coinsLastClaimed" not in users[id]:
        users[id]["coinsLastClaimed"] = float(0)
    last = users[id]["coinsLastClaimed"]
    
    currentTime = time.time()
    timeElapsed = currentTime - last
    if timeElapsed >= claimCooldown:
        value = (random.randint(50, 100) + (((random.randint(3, 10)) + (random.randint(3, 10))) ** 2))
        users[id]["coins"] += value
        users[id]["coinsLastClaimed"] = currentTime
        updateUserData(f"{id} claimed {value} coins")
        return True, value
    else:
        return False, time.ctime(last + claimCooldown) #time not passed

def messageBonus(id):
    id = str(id)
    x = 3 # 1/x chance to drop a coin each message
    coinsOnMessage = 1
    if isinstance(getUserCoins(id), int):
        if random.randint(1, x) == 1:
            users[id]["coins"] += coinsOnMessage
            updateUserData(f"{id} earned {coinsOnMessage}")
    return True
    