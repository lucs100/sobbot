from dotenv import load_dotenv
import requests, os, json, discord

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"

champs = {}
users = {}

with open('bot/resources/data/champs.json') as f:
    data = json.loads(f.read())
    champs = data

with open('bot/resources/data/userdata.json') as f:
    data = json.loads(f.read())
    users = data

def updateUserData():
    with open('bot/resources/data/userdata.json', 'w') as fp:
        json.dump(users, fp,  indent=4)
    return True

def getChampNameById(id):
    return champs[str(id)]

def getChampIdByName(q):
    for k in champs:
        n = data[k].lower()
        if n == q.lower():
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
    return -1

def parseSpaces(s):
    return s.replace(" ", "%20")

def checkKeyInvalid():
    response = requests.get(
        (url + f"/lol/status/v4/platform-data"),
        headers = headers
    )
    return not (response.status_code != 401 and response.status_code != 403)

def getSummonerData(s):
    response = requests.get(
        (url + f"/lol/summoner/v4/summoners/by-name/{parseSpaces(s)}"),
        headers = headers
    )
    summonerData = json.loads(response.text)
    return summonerData

def getESID(s): #encrypted summoner id
    if checkKeyInvalid():
        return False
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
            "losses": datajson[i]["losses"]
        }
    name = datajson[i]["summonerName"]
    return data, name

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
        return tier
    return f"{tier} {div}"

def parseQueue(queue):
    queueTable = {
        "RANKED_SOLO_5x5": "Solo/Duo",
        "RANKED_FLEX_SR": "Flex"
    }
    return queueTable[queue]

def embedRankedData(s):
    data, s = getRankedData(s)
    # if data == False or s == False:
    #     return False
    title=f"{s}  -  Ranked Status"
    description = ""
    for i in range(0, len(data)):
        rank = parseRank(data[i]["tier"], data[i]["division"])
        q = parseQueue(data[i]["queue"])
        lp, w, wr = data[i]["lp"], data[i]["wins"], ((data[i]["wins"] * 100) / (data[i]["wins"] + data[i]["losses"]))
        description += (f"**{q}** - **{rank}** - {lp} LP")
        description += "\n"
        description += (f"*({w} wins - {round(wr, 2)}% winrate)*")
        description += "\n"
        description += "\n"
    if description == "":
        description = "This summoner isn't ranked in any queues yet!"
    return discord.Embed(title=title, description=description, color=0xFFDC00)

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
    for i in range(0, 3):
        try:
            data.append({
                "name": getChampNameById(datajson[i]["championId"]),
                "level": datajson[i]["championLevel"],
                "points": datajson[i]["championPoints"]
                })
        except:
            break
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
    if descripton == "":
        description = "This summoner hasn't earned any mastery points yet!"
    embed = discord.Embed(title=title, description=description, color=0x2beafc)
    return embed

def isUserRegistered(id):
    id = str(id)
    if id in users:
        return users[id]["lol"]
    else:
        return False

def addRegistration(id, name):
    data = getNameAndLevel(name)
    if data == False:
        return False
    users[str(id)] = {"lol": "placeholder"}
    users[str(id)]["lol"] = str(data["name"])
    updateUserData()
    return data["name"]

def editRegistration(id, name):
    data = getNameAndLevel(name)
    if data == False:
        return False
    users[str(id)]["lol"] = str(name)
    updateUserData()
    return data["name"]