import json

guilds = dict({})

DefaultPrefix = "s!"

with open('bot/resources/data/guilds.json') as f:
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
    with open('bot/resources/data/guilds.json', 'w') as fp:
        json.dump(guilds, fp, indent=4)
    return True