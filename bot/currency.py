import json

startingCoins = 1000

users = {}

with open('bot/resources/data/userdata.json') as f:
    data = json.loads(f.read())
    users = data
    
def updateUserData():
    with open('bot/resources/data/userdata.json', 'w') as fp:
        json.dump(users, fp,  indent=4)
    return True

def getUserCoins(id):
    id = str(id)
    if id in users:
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
    updateUserData()
    return True