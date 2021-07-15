# Sobbot - Riot Games API Library
# Written by Lucas Di Pietro 2021


###############################


# Library Imports and Other Formalities


from random import Random
from sys import prefix
from discord import player
from dotenv import load_dotenv
import requests, os, json, discord
from datetime import datetime
import concurrent
from time import sleep

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"


# Constants and Constant Data


champs = {}
users = {}
pulledMatches = {}
queues = {}
runes = {}
summSpells = {}
summonerList = []

MatchLimit = 80


# Class Declarations


class SummSpell():
    def __init__(self, data):
        self.name = data["name"]
        self.cooldown = data["cooldown"][0]
        self.id = int(data["key"])

class MatchKey:
    def __init__(self, matchData):
        self.gameID = matchData["gameId"]
        self.champID = int(matchData["champion"])
        self.champ = getChampNameById(self.champID)
        self.queue = int(matchData["queue"])
        self.time = datetime.fromtimestamp(int(matchData["timestamp"])/1000)
        self.role = getRole(matchData["role"], matchData["lane"])
        self.debugData = (matchData["role"], matchData["lane"])

class Match:
    def __init__(self, matchData):
        pass
        #todo

class LiveMatchParticipant():
    def __init__(self, data):
        self.teamID = data["teamId"]
        self.summ1 = summSpells
        self.summ2 = summSpells
        self.champID = data["championId"]
        self.champName = getChampNameById(self.champID)
        self.icon = data["profileIconId"]
        self.summonerName = data["summonerName"]
        self.customizationObjects = data["gameCustomizationObjects"]
        # self.perks = data["perks"]["perkIds"] #change these to runes later maybe?
        # self.primaryRuneTree = data["perks"]["perkStyle"]
        # self.secondaryRuneTree = data["perks"]["perkSubStyle"]
        # self.rank = getRank(self.summonerName) #todo

class LiveMatchBan():
    def __init__(self, data):
        self.champID = data["championId"]
        self.champName = getChampNameById(self.champID) 
        self.teamID = data["teamId"]
        self.pickTurn = data["pickTurn"]

class LiveMatch():
    def __init__(self, data, targetSummoner):
        if not isinstance(targetSummoner, Summoner):
            targetSummoner = getSummonerData(targetSummoner)
        self.targetSummoner = targetSummoner
        self.gameMode = getModeFromQueueID(data["gameQueueConfigId"])["description"]
        self.participants = {}
        for player in data["participants"]:
            if player["summonerName"] == self.targetSummoner.name:
                self.targetPlayer = LiveMatchParticipant(player)
            self.participants[data["participants"].index(player)] = LiveMatchParticipant(player)
        self.gameID = data["gameId"]
        self.bans = {}
        for ban in data["bannedChampions"]:
            self.bans[data["bannedChampions"].index(ban)] = LiveMatchBan(ban)
        self.startTime = datetime.fromtimestamp(data["gameStartTime"]/1000)
        self.elapsedTime = (datetime.now() - self.startTime).seconds
        self.spectatorKey = data["observers"]["encryptionKey"]

class Summoner():
    def __init__(self, data):
        if isinstance(data, str):
            self = getSummonerData(data)
        self.eaid = data["accountId"]
        self.esid = data["id"]
        self.puuid = data["puuid"]
        self.name = data["name"]
        self.icon = data["profileIconId"]
        self.timestamp = data["revisionDate"]
        self.level = data["summonerLevel"]

    def getRank(self, hasLP=False, queue="RANKED_SOLO_5x5"): #only works with default rank right now
        try:
            response = requests.get(
                (url + f"/lol/league/v4/entries/by-summoner/{self.esid}"),
                headers = headers
            )
        except:
            return "Summoner not found"
        datajson = response.json()
        data = {}
        for q in datajson:
            try:
                if q["queueType"] == queue:
                    data = {
                        "tier": q["tier"],
                        "division": q["rank"],
                        "lp": q["leaguePoints"]
                        }
            except TypeError:
                if q == "status":
                    pass
                # rate limit
        if data != {}:
            if hasLP:
                return (f"{data['tier'].capitalize()} {data['division']}, {data['lp']} LP")
            else:
                return (f"{data['tier'].capitalize()} {data['division']}")
        else: return "Unranked"
    
    def getSingleMastery(self, champ):
        if not isinstance(champ, int):
            try: champ = int(champ)
            except ValueError:
                try: 
                    champ = getChampIdByName(str(champ))
                    if champ == -1:
                        return None
                except: return None
        response = requests.get(
                (url + f"/lol/champion-mastery/v4/champion-masteries/by-summoner/{self.esid}/by-champion/{champ}"),
                headers = headers
            )
        if response.status_code == 404:
            return None
        return {"level": response.json()["championLevel"], "points": response.json()["championPoints"]}


# File Imports / Setup


with open('bot/resources/data/champs.json') as f:
    data = json.loads(f.read()) # unpacking data
    champs = data
    f.close()

with open('bot/resources/data/queues.json') as f:
    data = json.loads(f.read()) # unpacking data
    queues = data
    f.close()

with open('bot/resources/data/private/userdata.json') as f:
    data = json.loads(f.read()) # unpacking data
    users = data
    f.close()

with open('bot/resources/data/runesReforged.json') as f:
    data = json.loads(f.read()) # unpacking data
    runes = data
    f.close()

with open('bot/resources/data/summoner.json') as f:
    data = json.loads(f.read()) # unpacking data
    for summ in data:
        summSpells[int(data[summ]["key"])] = SummSpell(data[summ])
    f.close()

with open('bot/resources/data/private/matchdata.json') as f:
    try:
        data = json.loads(f.read()) # unpacking data
        print(f"/riotapi: Loaded {len(data)} matches.")
        pulledMatches = data
    except:
        print("Failure loading matchdata.json. File may be corrupt.")
    f.close()

for user in users.values():
    try:
        summonerList.append(user["lol"])
    except KeyError:
        pass


# Function Definitions


def getModeFromQueueID(id):
    try:
        for queue in queues:
            if queue["queueId"] == id:
                return {"map": queue["map"], "description": queue["description"]} 
    except KeyError:
        return {"map": "Queues file outdated!", "description": "Queues file outdated!"} 

def getChampNameById(id):
    return champs[str(id)]

def getChampIdByName(q):
    for id, n in champs.items():
        n = n.lower()
        if n == q.lower(): # quick and dirty algorithm to search for champ id by name
            return id
        elif n.replace('\'', " ") == q.lower():
            return id
        elif n.replace('.', " ") == q.lower():
            return id
        elif n.replace('\'', "") == q.lower():
            return id
        elif n.replace('.', "") == q.lower():
            return id
        elif n.replace(' ', "") == q.lower():
            return id
        elif q.lower() in n.lower():
            return id
    return -1 # returns -1 if no match

def getRole(role, lane):
    if lane == "MID":
        return "Middle"
    elif lane == "TOP":
        return "Top"
    elif lane == "JUNGLE":
        return "Jungle"
    elif role == "DUO_CARRY" or (role == "SOLO" and lane == "BOTTOM"):
        return "Bottom"
    elif role == "DUO_SUPPORT":
        return "Support"
    return "Unknown"

def checkKeyInvalid():
    response = requests.get(
        (url + f"/lol/status/v4/platform-data"), # quick response to see if both key ok and api ok
        headers = headers
    )
    return not (response.status_code != 401 and response.status_code != 403) 

# async def updateAPIKey():
#     load_dotenv(override=True) # allows overriding envs from an updated .env file
#     global RIOTTOKEN
#     global headers
#     RIOTTOKEN = os.getenv('RIOTTOKEN')
#     headers = {"X-Riot-Token": RIOTTOKEN} # pushes update to global headers
#     return True

def updateUserData():
    with open('bot/resources/data/private/userdata.json', 'w') as fp: # updates .json of all user data
        json.dump(users, fp, indent=4)
    return True

def updateMatchBase(force=False):
    def push():
        with open('bot/resources/data/private/matchdata.json', 'w') as fp: # updates .json of all user data
            json.dump(pulledMatches, fp, indent=4)
        return True

    if force:
        return push()
    
    with open('bot/resources/data/private/matchdata.json') as f:
            oldLen = len(json.loads(f.read())) # unpacking data
    f.close()
    if len(pulledMatches) >= oldLen:
        push()
    else:
        print("Attempted to save corrupt matchbase! Matchbase not saved.")
        return False

def cleanMatchBase():
    deleteList = []
    for entry in pulledMatches:
        if "gameId" not in pulledMatches[entry]:
            print(f"Dead match found: {entry}")
            deleteList.append(entry)
    for entry in deleteList:
        pulledMatches.pop(entry)
    updateMatchBase(force=True)

cleanMatchBase() # run this on startup to prune malformed matches!

def addToMatchBase(match, matchId, autosave=True):
    if str(matchId) not in pulledMatches:
        pulledMatches[str(matchId)] = match
        if autosave:
            updateMatchBase()
    return True

def parseSpaces(s):
    return s.replace(" ", "%20") # used in urls

def getSummonerData(s):
    if isinstance(s, Summoner):
        return s
    response = requests.get(
        (url + f"/lol/summoner/v4/summoners/by-name/{parseSpaces(s)}"),
        headers = headers
    )
    summonerData = response.json()
    if response.status_code != 200:
        return None
    else: return Summoner(summonerData)

def getRankedData(s):
    if checkKeyInvalid():
        return False
    summoner = getSummonerData(s)
    try:
        response = requests.get(
            (url + f"/lol/league/v4/entries/by-summoner/{summoner.esid}"),
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
        name = summoner.name
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
    
def calculateRankMultiplier(tier, div):
    tierDex = {
        "IRON": 0.1,
        "BRONZE": 0.35,
        "SILVER": 0.8,
        "GOLD": 1.5,
        "PLATINUM": 3,
        "DIAMOND": 10,
        "MASTER": 25,
        "GRANDMASTER": 50,
        "CHALLENGER": 100
    }
    divDex = {
        "IV": 1,
        "III": 1.4,
        "II": 1.6,
        "I": 1.8,
    }
    return round((tierDex[tier] * divDex[div])**2, 2)

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
        rmx = calculateRankMultiplier(data[i]["tier"], data[i]["division"]) # rank multiplier
        rs = int((w**2.5 * wr)*rmx / gp)
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

def anonGetSingleMastery(summoner, champ):
    if isinstance(summoner, str):
        summoner = getSummonerData(summoner)
    if summoner == None:
        return None
    if not isinstance(champ, int):
        try: champ = int(champ)
        except ValueError:
            try: 
                champ = getChampIdByName(str(champ))
                if champ == -1:
                    return None
            except: return None
    response = requests.get(
            (url + f"/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner.esid}/by-champion/{champ}"),
            headers = headers
        )
    if response.status_code == 404:
        return None
    # elif response.status_code == 409:
    #     return None #rate limit
    try:
        return {"level": response.json()["championLevel"], "points": response.json()["championPoints"]}
    except KeyError:
        return {"level": 0, "points": 0}
    
def getTopMasteries(s):
    if checkKeyInvalid():
        return False
    try:
        response = requests.get(
            (url + f"/lol/champion-mastery/v4/champion-masteries/by-summoner/{getSummonerData(s).esid}"),
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
    summoner = getSummonerData(name)
    if summoner == None:
        return False  # summoner does not exist
    users[str(id)] = {"lol": "placeholder"}
    users[str(id)]["lol"] = str(summoner.name)
    updateUserData()
    return (summoner.name) # confirms with properly capitalized name

def editRegistration(id, name):
    summoner = getSummonerData(name)
    if summoner == None:
        return False  # summoner does not exist
    users[str(id)]["lol"] = str(summoner.name)
    updateUserData()
    return (summoner.name) # confirms with properly capitalized name

def getMatchHistory(name, ranked=False):
    summoner = getSummonerData(name)
    if checkKeyInvalid():
        return "key"
    rankedParam = ""
    if ranked:
        rankedParam = "?queue=420"
    data = requests.get(
            (url + f"/lol/match/v4/matchlists/by-account/{summoner.eaid}{rankedParam}"),
            headers = headers
        )
    if data.status_code == 400:
        return "sum"
    matchList = []
    for matches in data.json()["matches"]:
        matchList.append(MatchKey(matches))
    return matchList

def getLastMatch(name, ranked=False):
    data = getMatchHistory(name, ranked)
    if data == []:
        return "none" #for errordict use, ik Nonetype exists
    return data[0]

def getMatchInfo(match, autosave=True):
    if isinstance(match, int):
        gameID = match
    else:
        gameID = match.gameID
    if str(gameID) in pulledMatches:
        return pulledMatches[str(gameID)]
    data = requests.get(
            (url + f"/lol/match/v4/matches/{gameID}"),
            headers = headers
        )
    if data.status_code == 400:
        return None
    addToMatchBase(data.json(), gameID, autosave)
    return data.json()

def getPlayerRespectiveInfo(match, esid):
    for player in match["participantIdentities"]:
        if player["player"]["summonerId"] == esid:
            playerdata = player
            playerNumber = player["participantId"]
    return {"matchdata": match["participants"][playerNumber-1], "playerdata": playerdata}

def analyzePlayerPerformance(matchId, summoner):
    summoner = getSummonerData(summoner)
    match = getMatchInfo(int(matchId))
    matchdata, playerdata = (getPlayerRespectiveInfo(match, summoner.esid))
    print(json.dumps(matchdata, indent=4))
    print(json.dumps(playerdata, indent=4))
    #todo

def didPlayerWin(summonerId, matchData):
    playerIndex = 0
    try:
        for player in matchData["participantIdentities"]:
            if summonerId == player["player"]["summonerId"]:
                playerIndex = player["participantId"]
                if playerIndex < 6:
                    return (matchData["teams"][0]["win"] == "Win")
                return (matchData["teams"][1]["win"] == "Win")
    except KeyError:
        print(matchData)
        print("RATE LIMIT EXCEEDED!")
        return "rate"

def bulkPullMatchData(matchList, max=MatchLimit):
    pullList = [] #stupid pass by sharing !!!
    for match in matchList:
        if str(match.gameID) not in pulledMatches:
            pullList.append(match)
    if len(pullList) > max:
        pullList = pullList[0:max]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        res = [executor.submit(getMatchInfo, game.gameID, autosave=False) for game in pullList]
        concurrent.futures.wait(res)
    updateMatchBase()
    return len(pullList)

def getWinLossPerformanceTag(awr, stdwr, deltawr):
    tag1 = "Placeholder"
    tag2 = "Standard"
    tag3 = "Average" #default tags
    #tag1 = short term, tag2 = longterm

    #not using tag1s for now
    # if awr >= 75:
    #     tag1 = "Unstoppable"
    # if awr >= 65:
    #     tag1 = "Blazing"
    # if awr >= 55:
    #     tag1 = "On Fire"
    # elif awr <= 45:
    #     tag1 = "In a Rough Patch"
    # elif awr <= 35:
    #     tag1 = "Needs a Break"
    # elif awr <= 25:
    #     tag1 = "Should cool off"
    
    if abs(stdwr-50) < 2.5 and abs(deltawr) < 2:
        tag2 = "Consistent"
    elif deltawr >= 5:
        tag2 = "Suddenly Winning"
    elif deltawr >= 3.25:
        tag2 = "Hot Streak"
    elif deltawr >= 1.5:
        tag2 = "Warming Up"
    elif deltawr <= -1.5:
        tag2 = "Rough Patch"
    elif deltawr <= -3.25:
        tag2 = "Cold Streak"
    elif deltawr <= -5:
        tag1 = "Tilted"
    elif deltawr == 0:
        tag2 = "Is this even mathematically possible"

    if stdwr >= 80:
        tag3 = "Absolutely Insane"
    elif stdwr >= 70:
        tag3 = "Cracked"
    elif stdwr >= 60:
        tag3 = "Overachiever"
    elif stdwr <= 40:
        tag3 = "Underperformer"
    elif stdwr <= 30:
        tag3 = "Needs a new champ"
    elif stdwr <= 20:
        tag3 = "Should Uninstall"

    return {
        "tag1":tag1,
        "tag2":tag2,
        "tag3":tag3
        }

def getWinLossTrend(summonerName, maxMatches=MatchLimit, ranked=False, turboMode=True):
    data = getSummonerData(summonerName)
    if data == None:
        return "sum"
    summonerName = data.name
    sID = data.esid
    matchList = getMatchHistory(data, ranked)[0:maxMatches]
    if turboMode:
        bulkPullMatchData(matchList)
    w = 0
    l = 0
    awr = 0 #adjusted winrate
    m = 0 #maximum
    for i in range(len(matchList)):
        value = (1 - (i/maxMatches)**3)
        win = didPlayerWin(sID, getMatchInfo(matchList[i]))
        if isinstance(win, str):
            return win #error code
        elif win:
            w += 1
            awr += value
        else:
            l += 1
        m += value
    awr = (awr/m)
    g = w + l
    return {"record":(w, l, g), "awr":awr, "name": summonerName}

async def parseWinLossTrend(summoner, message, maxMatches=MatchLimit, ranked=False):
    #make embed later #slow
    title = "Retrieving data..."
    text = "This may take a while if this summoner's match history hasn't recently been pulled."
    embed = discord.Embed(title=title, description=text)
    sentMessage = await message.channel.send(embed=embed)
    data = getWinLossTrend(summoner, maxMatches, ranked)
    codes = ["rate", "sum"]
    if data in codes:
        if data == "rate":
            text = "<@!312012475761688578> **RATE LIMIT EXCEEDED!** Sobbot will now exit to avoid API blacklisting."
            await sentMessage.edit(content=text)
            exit()
        elif data == "sum":
            text = f"Summoner {summoner} doesn't exist."
            await sentMessage.edit(content=text)
    w = data["record"][0]
    l = data["record"][1]
    gp = data["record"][2]
    awr = data["awr"]*100
    name = data["name"]
    stdwr = (w/gp)*100
    deltawr = (awr-stdwr)
    text = ""
    if ranked:
        text += f"{name} is {w}W - {l}L in their past {gp} ranked matches.\n"
    else:
        text += f"{name} is {w}W - {l}L in their past {gp} matches.\n"
    text += f"Standard winrate: **{stdwr:.2f}**%\n"
    #text += f"Recent-curved winrate: **{awr:.2f}**%\n" #hidden
    if deltawr > 0:
        color = 0x6ad337
        title = f"{name} - Winrate Analysis (+{deltawr:.2f})"
        text += f"Recency-Relative Rating: **+{deltawr:.2f}** points\n"
    else:
        color = 0xd33737
        title = f"{name} - Winrate Analysis ({deltawr:.2f})"
        text += f"Recency-Relative Rating: **{deltawr:.2f}** points\n"
    tags = getWinLossPerformanceTag(awr, stdwr, deltawr)
    tag2 = tags["tag2"]
    tag3 = tags["tag3"]
    text += f"Short term tag: *{tag2}*\n"
    text += f"Long term tag: *{tag3}*\n"
    embed.title = title
    embed.description = text
    embed.color = color
    await sentMessage.edit(embed=embed)
    return True

def timeSinceLastMatch(name, ranked=False):
    if checkKeyInvalid():
        return "key"
    try:
        name = getSummonerData(name).name
    except KeyError:
        return "sum"
    codes = ["key", "sum", "none"]
    now = datetime.now()
    lastMatch = getLastMatch(name, ranked)
    if lastMatch in codes:
        return lastMatch
    lastMatchTime = lastMatch.time
    totalSeconds = int((now-lastMatchTime).total_seconds())
    # while totalSeconds < 0:
    #     totalSeconds += 24*60*60 #timedeltas become negative sometimes
    days, remainder = divmod(totalSeconds, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)
    def p(value, annotation): #parse
        if value == 1:
            return f"{value} {annotation}"
        return f"{value} {annotation}s"
    if days == 0:
        if hours == 0:
            if minutes == 0:
                return {"name":name, "time":f"{p(seconds, 'second')}"}
            return {"name":name, "time":f"{p(minutes, 'minute')}, {p(seconds, 'second')}"}
        return {"name":name, "time":f"{p(hours, 'hour')}, {p(minutes, 'minute')}, {p(seconds, 'second')}"}
    return {"name":name, "time":f"{p(days, 'day')}, {p(hours, 'hour')}, {p(minutes, 'minute')} {p(seconds, 'second')}"}

def getRoleHistory(name, ranked=False, weightedMode=False):
    try:
        name = getSummonerData(name).name
    except KeyError:
        return "sum"
    matchHistory = getMatchHistory(name, ranked)
    gp = len(matchHistory)
    totalWeight = 0
    roleDict = {
        "Top": 0,
        "Jungle": 0,
        "Middle": 0,
        "Bottom": 0,
        "Support": 0,
        "Unknown": 0,
    }
    for i in range(len(matchHistory)):
        match = matchHistory[i]
        # if match.role == "Unknown":
        #     print(match.debugData)
        if weightedMode:
            value = (1 - ((i/gp)**2))
            roleDict[match.role] += value
            totalWeight += value
        else:
            roleDict[match.role] += 1
    if weightedMode:
        for role in roleDict:
            roleDict[role] = 100*roleDict[role]/totalWeight
    return {"name": name, "roles": roleDict, "games": gp}

def getTopRoles(data):
    primary, secondary = None, None
    temp = dict(data) # pass by sharing workaround
    temp = dict(temp)
    temp.pop("Unknown")
    primary = max(temp, key=temp.get)
    temp.pop(primary)
    secondary = max(temp, key=temp.get)
    return primary, secondary

def getRolePlayDataEmbed(name, ranked=False):
    try:
        name = getSummonerData(name).name
    except KeyError:
        return "sum"
    codes = ["key", "sum"]
    rh = getRoleHistory(name, ranked=ranked, weightedMode=True)
    if rh in codes:
        return rh
    name, data, gp = rh["name"], rh["roles"], rh["games"] 
    primary, secondary = getTopRoles(data)
    description = ""
    for role in data:
        freq = data[role]
        if role == primary:
            format = "**"
        elif role == secondary:
            format = "*"
        else:
            format = ""
        description += f"{format}{freq:.2f}% {role}{format}\n"
    title = f"{name} likely queues for **{primary}**/*{secondary}*."
    rt = ""
    if ranked:
        rt = "ranked "
    footertext = f"{gp} {rt}games analyzed."
    embed = discord.Embed(title=title, description=description, color=discord.Color.random())
    embed.set_footer(text=footertext)
    return embed

def getBanData(matchList):
    if isinstance(matchList, Match):
        matchList = [matchList]
    if isinstance(matchList, MatchKey):
        matchList = [Match(getMatchInfo(matchList))]
    bans = dict()
    for match in matchList:
        data = getMatchInfo(match)
        for playerId in range(0, 10):
            try:
                bannedChamp = str(data["teams"][(playerId - 1) // 5]["bans"][(playerId % 5) - 1]["championId"])
                # ban "order" doesnt match up with player indexing, so getting bans by player
                # is awkward (need to compare one of the account IDs to determing pick order)
                # function only gets bans for match + accounts for dupes
                if champs[bannedChamp] in bans:
                    bans[champs[bannedChamp]] += 1
                else:
                    bans[champs[bannedChamp]] = 1
            except KeyError:
                pass
    return bans

def getLiveMatch(summoner):
    if isinstance(summoner, str):
        summoner = getSummonerData(summoner)
    data = requests.get(
            (url + f"/lol/spectator/v4/active-games/by-summoner/{summoner.esid}"),
            headers = headers
        )
    if data.status_code == 409:
        return "rate"
    elif data.status_code == 404:
        return "no"
    else: return LiveMatch(data.json(), summoner)

async def getLiveMatchEmbed(summoner, message):

    class PlayerString():
        def __init__(self, data, team):
            self.dataString = data
            self.team = team

    def parseLiveMatchPlayerString(player):
        d = ""
        masteryStr = ""
        rankStr = " - "
        level, points = 0, 0
        targetName = match.targetPlayer.summonerName
        champData = (anonGetSingleMastery(player.summonerName, player.champID))
        if champData != None:
            rankStr += (getSummonerData(player.summonerName).getRank())
            level, points = champData["level"], champData["points"]
            msDec = ""
            if level >= 3:
                if points >= 50000:
                    msDec = "*"
                if points >= 200000:
                    msDec = "**"
                if points >= 500000:
                    msDec = "***"
                if points >= 1000000:
                    msDec = "`"
                masteryStr = f"  -  {msDec}(M{level} / {points:,}){msDec}"
        else:
            return None
        if player.summonerName == targetName:
            d = "**"
        return PlayerString(data=f"{d}{player.summonerName}{d}  -  {player.champName}{masteryStr} {rankStr}\n", team=player.teamID)
        
    title = "Requesting match data..."
    description = "Hang tight!"
    embed = discord.Embed(title=title, description=description)
    sentEmbed = await message.channel.send(embed=embed)
    if isinstance(summoner, str):
        data = getSummonerData(summoner)
        if data == None:
            embed.title = "Summoner not found"
            embed.description = f"Summoner {summoner} doesn't seem to exist."
            await sentEmbed.edit(embed=embed)
            return False
    summoner = data
    match = getLiveMatch(summoner)
    if isinstance(match, str):
        if match == "rate":
            embed.title = "Rate limit exceeded!"
            embed.description = "<@!312012475761688578> Sobbot will now exit."
            await sentEmbed.edit(embed=embed)
            return False
        elif match == "no":
            embed.title = "Match not found"
            embed.description = f"Summoner {summoner.name} isn't in a match right now!"
            await sentEmbed.edit(embed=embed)
            return False
    text = ""
    if match.targetPlayer.teamID == 100:
        embed.color = 0x3366cc    # blue
    else: embed.color = 0xff5050  # red
    embed.title = "Populating data..."
    text += "`Blue Team`\n"
    embed.description = text
    for team in range(0, 2):
        res = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            res = executor.map(parseLiveMatchPlayerString, match.participants.values()) #create executor map of results
        for playerString in res:
            if playerString == None:
                embed.title = "Rate limit exceeded!"
                embed.description = "<@!312012475761688578>"
                await sentEmbed.edit(embed=embed)
                return False
            if playerString.team == (team+1)*100: # if result on team:
                text += playerString.dataString   # print player result
        embed.description = text
        await sentEmbed.edit(embed=embed)
        if team == 0:
            text += "\n`Red Team`\n"
    # embed.description = str(match)
    embed.description = text
    title = ""
    elapsed = match.elapsedTime
    m, s = divmod(elapsed, 60)
    title += f"Live Match - {m}:{s:02d} elapsed - {match.gameMode}"
    embed.title = title
    await sentEmbed.edit(embed=embed)