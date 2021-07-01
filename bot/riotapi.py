from dotenv import load_dotenv
import requests, os, json, discord

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"

champs = {}
users = {}

with open('bot/resources/data/champs.json') as f:
    data = json.loads(f.read()) # unpacking data
    champs = data

with open('bot/resources/data/private/userdata.json') as f:
    data = json.loads(f.read()) # unpacking data
    users = data

def checkKeyInvalid():
    response = requests.get(
        (url + f"/lol/status/v4/platform-data"), # quick response to see if both key ok and api ok
        headers = headers
    )
    return not (response.status_code != 401 and response.status_code != 403) 

async def updateAPIKey():
    load_dotenv(override=True) # allows overriding envs from an updated .env file
    global RIOTTOKEN
    global headers
    RIOTTOKEN = os.getenv('RIOTTOKEN')
    headers = {"X-Riot-Token": RIOTTOKEN} # pushes update to global headers
    return True

def updateUserData():
    with open('bot/resources/data/private/userdata.json', 'w') as fp: # updates .json of all user data
        json.dump(users, fp,  indent=4)
    return True

def getChampNameById(id):
    return champs[str(id)]

def getChampIdByName(q):
    for k in champs:
        n = data[k].lower()
        if n == q.lower(): # quick and dirty algorithm to search for champ id by name
            return k
        elif n.replace('\'', " ") == q.lower():
            return k
        elif n.replace('.', " ") == q.lower():
            return k
        elif n.replace('\'', "") == q.lower():
            return k
        elif n.replace('.', "") == q.lower():
            return k
        elif n.replace(' ', "") == q.lower():
            return k
        elif q.lower() in n.lower():
            return k
    return -1 # returns -1 if no match

def parseSpaces(s):
    return s.replace(" ", "%20") # used in urls

def getSummonerData(s):
    response = requests.get(
        (url + f"/lol/summoner/v4/summoners/by-name/{parseSpaces(s)}"),
        headers = headers
    )
    summonerData = json.loads(response.text)
    return summonerData # loads basic summoner data

def getESID(s): # encrypted summoner id
    if checkKeyInvalid():
        return False, False  # what
    return getSummonerData(s)["id"]

def getNameAndLevel(s):
    if checkKeyInvalid():
        return False
    summonerData = getSummonerData(s)
    return {"name": summonerData["name"], "level": int(summonerData["summonerLevel"])}

def getRankedData(s):
    if checkKeyInvalid():
        return False
    try:
        response = requests.get(
            (url + f"/lol/league/v4/entries/by-summoner/{getESID(s)}"),
            headers = headers
        )
    except:
        return False
    datajson = response.json()
    data = {}
    for i in range(len(datajson)):
        data[i] = {
            "queue": datajson[i]["queueType"],
            "tier": datajson[i]["tier"],
            "division": datajson[i]["rank"],
            "lp": datajson[i]["leaguePoints"],
            "wins": datajson[i]["wins"],
            "losses": datajson[i]["losses"],
            "gp": int(datajson[i]["wins"]) + int(datajson[i]["losses"])
        }
    try:
        name = datajson[i]["summonerName"]
    except:
        name = getNameAndLevel(s)["name"]
    return data, name

def getMaxRank(list):
    rankSet = set()
    ranks = {
        "IRON": 0,
        "BRONZE": 1,
        "SILVER": 2,
        "GOLD": 3,
        "PLATINUM": 4,
        "DIAMOND": 5,
        "MASTER": 6,
        "GRANDMASTER": 7,
        "CHALLENGER": 8
    }
    ranksReverse = [
        "IRON",
        "BRONZE",
        "SILVER",
        "GOLD",
        "PLATINUM",
        "DIAMOND",
        "MASTER",
        "GRANDMASTER",
        "CHALLENGER"
    ]
    for i in range(len(list)):
        rankSet.add(ranks[list[i]])
    maxRank = max(rankSet)
    return ranksReverse[maxRank]

def getTierColor(tier):
    tier = tier.capitalize()
    colorTable = {
        "Iron": 0x5E5858,
        "Bronze": 0xA16147,
        "Silver": 0x859FA9,
        "Gold": 0xCC9C3F,
        "Platinum": 0x1699A0,
        "Diamond": 0x806CE7,
        "Master": 0xB40FCB,
        "Grandmaster": 0xFC3D39,
        "Challenger": 0x4FEDFF
    }
    try:
        return colorTable[tier]
    except:
        return 0x64686e

def parseRank(tier, div):
    # divTable = {
    #     "I": 1,
    #     "II": 2,
    #     "III": 3,
    #     "IV": 4,
    #     "V": 5
    # }
    apexTable = ["Master", "Grandmaster", "Challenger"]
    tier = tier.capitalize()
    if tier in apexTable:
        return tier   # apex ranks do not have divs but are coded as (rank) (div1)
    return f"{tier} {div}"

def parseQueue(queue):
    queueTable = {
        "RANKED_SOLO_5x5": "Solo/Duo",
        "RANKED_FLEX_SR": "Flex"
    }
    return queueTable[queue]

def embedRankedData(s):
    data = getRankedData(s) # either False, for error 2, or {data, s}
    if checkKeyInvalid():   
        return 1 # key invalid error
    if data == False:
        return 2 # summoner does not exist
    data, s = data[0], data[1]
    title=f"{s}  -  Ranked Status"
    description, rankDict = "", []
    color = 0x64686e
    for i in range(0, len(data)):
        rank = parseRank(data[i]["tier"], data[i]["division"])
        q = parseQueue(data[i]["queue"])
        lp, w, l, gp, wr = data[i]["lp"], data[i]["wins"], data[i]["losses"], data[i]["gp"], ((data[i]["wins"] * 100) / (data[i]["gp"]))
        awr = (w+10)*100 / (gp+20) # 3b1b's method of review checking, applied to winrate
        rs = int((w**3 * wr) / gp)
        description += (f"**{q}** - **{rank}** - {lp} LP")
        description += "\n"
        description += (f"({w} wins, {l} losses - {round(wr, 2)}% winrate)")
        description += "\n"
        description += (f"*{round(awr, 2)}% adjusted winrate*")
        description += "\n"
        description += (f"*Queue Ranked Score: {rs:,}*")
        description += "\n"
        description += "\n"
        rankDict.append(data[i]["tier"])
    if len(rankDict) > 0:
        color = getTierColor(getMaxRank(rankDict))
    else:
        color = 0x64686e
    if description == "": #no data returned
        description = "This summoner isn't ranked in any queues yet!"
    return discord.Embed(title=title, description=description, color=color)

data = embedRankedData("s8 is so fun")
if isinstance(data, discord.Embed):
    print(data.title)
    print("")
    print(data.description)
    print("")
    print(data.color)
else:
    print(data)

def getTopMasteries(s):
    if checkKeyInvalid():
        return False
    try:
        response = requests.get(
            (url + f"/lol/champion-mastery/v4/champion-masteries/by-summoner/{getESID(parseSpaces(s))}"),
            headers = headers
        )
    except:
        return False
    datajson = response.json()
    data = []
    for i in range(0, 3): #top three masteries, can be altered
        try:
            data.append({
                "name": getChampNameById(datajson[i]["championId"]),
                "level": datajson[i]["championLevel"],
                "points": datajson[i]["championPoints"]
                })
        except:
            break # if none left, ie. two or less champs
    return data

def embedTopMasteries(s):
    if checkKeyInvalid():
        return False
    data = getTopMasteries(s)
    title=f"{s}  -  Top Masteries"
    description = ""
    for i in range(0, len(data)):
        l, n, p = data[i]["level"], data[i]["name"], data[i]["points"]
        description += (f"Mastery {l} with *{n}*  -  **{p:,}** points")
        description += "\n"
    if description == "": #no loops, ie. no data
        description = "This summoner hasn't earned any mastery points yet!"
    embed = discord.Embed(title=title, description=description, color=0x2beafc)
    return embed

def isUserRegistered(id):
    id = str(id)
    if id in users:
        if "lol" in users[id]:
            return users[id]["lol"]  # if lol name in user data
    return False

def addRegistration(id, name):
    data = getNameAndLevel(name)
    if data == False:
        return False  # summoner does not exist
    users[str(id)] = {"lol": "placeholder"}
    users[str(id)]["lol"] = str(data["name"])
    updateUserData()
    return data["name"] # confirms with properly capitalized name

def editRegistration(id, name):
    data = getNameAndLevel(name)
    if data == False:
        return False  # summoner does not exist
    users[str(id)]["lol"] = str(data["name"])
    updateUserData()
    return data["name"] # confirms with properly capitalized name