from random import Random
from sys import prefix
from dotenv import load_dotenv
import requests, os, json, discord
from datetime import datetime
import concurrent

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"

champs = {}
users = {}
pulledMatches = {}

MatchLimit = 25

with open('bot/resources/data/champs.json') as f:
    data = json.loads(f.read()) # unpacking data
    champs = data

with open('bot/resources/data/private/userdata.json') as f:
    data = json.loads(f.read()) # unpacking data
    users = data

with open('bot/resources/data/private/matchdata.json') as f:
    data = json.loads(f.read()) # unpacking data
    print(f"/riotapi: Loaded {len(data)} matches.")
    pulledMatches = data

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
        json.dump(users, fp, indent=4)
    return True

def updateMatchBase():
    with open('bot/resources/data/private/matchdata.json', 'w') as fp: # updates .json of all user data
        json.dump(pulledMatches, fp, indent=4)
    return True

def addToMatchBase(match, matchId, autosave=True):
    if str(matchId) not in pulledMatches:
        pulledMatches[str(matchId)] = match
        if autosave:
            updateMatchBase()
    return True

def parseSpaces(s):
    return s.replace(" ", "%20") # used in urls

def getSummonerData(s):
    response = requests.get(
        (url + f"/lol/summoner/v4/summoners/by-name/{parseSpaces(s)}"),
        headers = headers
    )
    summonerData = json.loads(response.text)
    if response.status_code == 400:
        return None
    return summonerData # loads basic summoner data

def getESID(s): # encrypted summoner id
    if checkKeyInvalid():
        return False, False  # what
    return getSummonerData(s)["id"]

def getEAID(s): # encrypted summoner id
    if checkKeyInvalid():
        return False, False  # what
    try:
        return getSummonerData(s)["accountId"]
    except KeyError:
        return False

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

def getMatchHistory(name, ranked=False):
    if checkKeyInvalid():
        return "key"
    data = requests.get(
            (url + f"/lol/match/v4/matchlists/by-account/{getEAID(parseSpaces(name))}"),
            headers = headers
        )
    if data.status_code == 400:
        return "sum"
    #datajson = json.dumps(data.json(), indent=4)
    matchList = []
    for matches in data.json()["matches"]:
        if ranked:
            currentMatch = MatchKey(matches)
            if currentMatch.queue == 420: # ranked solo/duo queue id
                matchList.append(MatchKey(matches))
        else:
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
    match = getMatchInfo(int(matchId))
    esid = getESID(summoner)
    matchdata, playerdata = (getPlayerRespectiveInfo(match, esid))
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
        print("ERROR")
        print(matchData)

def bulkPullMatchData(matchList, max=MatchLimit): #not accessible by sobbot atm
    for match in matchList:
        if str(match.gameID) in pulledMatches:
            matchList.remove(match)
    if len(matchList) > max:
        matchList = matchList[0:max]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        res = [executor.submit(getMatchInfo, game.gameID) for game in matchList]
        concurrent.futures.wait(res)
    updateMatchBase()
    return True

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

def getWinLossTrend(summoner, maxMatches=MatchLimit, ranked=False):
    data = getSummonerData(summoner)
    if data == None:
        return "sum"
    summoner = data["name"]
    sID = data["id"]
     #param at some point
    matchList = getMatchHistory(summoner, ranked)[0:maxMatches]
    bulkPullMatchData(matchList)
    w = 0
    l = 0
    awr = 0 #adjusted winrate
    m = 0 #maximum
    for i in range(len(matchList)):
        value = (1 - (i/maxMatches)**3)
        if didPlayerWin(sID, getMatchInfo(matchList[i])):
            w += 1
            awr += value
        else:
            l += 1
        m += value
    awr = (awr/m)
    g = w + l
    return {"record":(w, l, g), "awr":awr, "name": summoner}

async def parseWinLossTrend(summoner, message, maxMatches=MatchLimit, ranked=False):
    #make embed later #slow
    sentMessage = await message.channel.send("Retrieving data... \n" +
    "This may take a while if this summoner's match history hasn't recently been pulled.")
    data = getWinLossTrend(summoner, maxMatches, ranked)
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
    #text += f"Recent-curved winrate: **{awr:.2f}**%\n"
    if deltawr > 0:
        text += f"Recency-Relative Rating: **+{deltawr:.2f}** points\n"
    else:
        text += f"Recency-Relative Rating: **{deltawr:.2f}** points\n"
    tags = getWinLossPerformanceTag(awr, stdwr, deltawr)
    tag2 = tags["tag2"]
    tag3 = tags["tag3"]
    text += f"Short term tag: *{tag2}*\n"
    text += f"Long term tag: *{tag3}*\n"
    await sentMessage.edit(content=text)
    return True

def timeSinceLastMatch(name, ranked=False):
    if checkKeyInvalid():
        return "key"
    try:
        name = getNameAndLevel(name)["name"]
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
        name = getNameAndLevel(name)["name"]
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
        name = getNameAndLevel(name)["name"]
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