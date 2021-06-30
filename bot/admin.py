import json

guilds = dict({})

DefaultPrefix = "s!"

with open('bot/resources/data/private/guilds.json') as f:
    guilds = json.loads(f.read())

def getGuildPrefix(id):
    try:
        return guilds[str(id)]["prefix"]
    except KeyError:
        return DefaultPrefix

def checkUserAdmin(user):
    if user.guild_persmissions.administrator:
        return True
    
def updateGuildData():
    with open('bot/resources/data/private/guilds.json', 'w') as fp:
        json.dump(guilds, fp, indent=4)
    return True

def resetGuildPrefix(id):
    id = str(id)
    try:
        if "prefix" in guilds[id]:
            guilds[id].pop("prefix")
            updateGuildData()
            return "ok"
        else:
            return "nop"
    except:
        return "error"

def updateGuildPrefix(id, prefix):
    id = str(id)
    if prefix == DefaultPrefix:
        resetGuildPrefix(id)
        return True
    if id in guilds:
        guilds[id]["prefix"] = ""
    else:
        guilds[id] = {}
        guilds[id]["prefix"] = ""
    guilds[id]["prefix"] = prefix
    updateGuildData()
    return (guilds[id]["prefix"] == prefix)