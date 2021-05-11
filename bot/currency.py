import json, time

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
    if sender not in users:
        return 3 #sender error
    elif "coins" not in users[str(sender)]:
        return 3 #sender error
    elif recipient not in users:
        return 1 #recipient error
    elif "coins" not in users[str(recipient)]:
        return 1 #recipient error

    if users[sender]["coins"] < value or value <= 0:
        return 2 #insufficient soblecoins

    users[sender]["coins"] -= value
    users[recipient]["coins"] += value
    updateUserData(f"{sender} sent {value} coins to {recipient}")
    return 0

