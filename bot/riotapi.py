# Sobbot - Riot Games API Library
#Lucas Di Pietro 2021


###############################


# Library Imports and Other Formalities


from logging import exception
from discord.ext.commands.errors import CommandError
import requests, os, json, discord, concurrent, warnings
from dotenv import load_dotenv
from datetime import datetime
from admin import getGuildPrefix
from discord.ext import commands

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"
v5url = "https://americas.api.riotgames.com" #MATCH-V5 / TFT-MATCH-V1


# Error Classes


class KeyExpiredError(commands.CommandError):
	pass

class SummonerNotRegisteredError(commands.CommandError):
    pass

class SummonerNotFoundError(commands.CommandError):
    def __init__(self, name0="That summoner"):
        if name0 == None:
            self.name = "That summoner"
        else:
            self.name = name0

class NoRecentMatchesError(commands.CommandError):
    def __init__(self, name0="That summoner"):
        if name0 == None:
            self.name = "That summoner"
        else:
            self.name = name0

class MatchHistoryOutdatedWarning(commands.CommandError):
    pass

class MatchHistoryDataWarning(commands.CommandError):
    pass

class RateLimitError(commands.CommandError):
    pass

class SummonerNotInMatchError(commands.CommandError):
    pass


# Constants and Constant Data


champs = {} #TODO: get from ddrag
users = {}
pulledMatches = {}
queues = {}
runes = {}
summSpells = {}
summonerList = []

CurrentPatch = "12.4.1" #TODO - get from ddrag

MATCH_LIMIT = 25
ADJ_WINRATE_DECAY_CONSTANT = 0.925

MASTERY_TIER_4_BREAKPOINT = 1000
MASTERY_TIER_3_BREAKPOINT = 500
MASTERY_TIER_2_BREAKPOINT = 250
MASTERY_TIER_1_BREAKPOINT = 100

CARRY_FACTOR_UNLOCK = 25

SEASON_12_START_TIME = datetime.fromtimestamp(1641556801)


# Class Declarations


class SummSpell():
    def __init__(self, data):
        self.name = data["name"]
        self.cooldown = data["cooldown"][0]
        self.id = int(data["key"])

class Rank:
    def __init__(self, data, name):
        if "TFT" in data["queueType"]:
            self = None
            return None
        self.queue = data["queueType"]
        self.tier = data["tier"]
        self.division = data["rank"]
        self.lp = data["leaguePoints"]
        self.wins = int(data["wins"])
        self.losses = int(data["losses"])
        self.gp = int(self.wins) + int(self.losses)
        self.name = name

class ChampionMastery:
    def __init__(self, data):
        try:
            self.champ = getChampNameById(data["championId"])
            self.level = data["championLevel"]
            self.points = data["championPoints"]
        except KeyError:
            self.champ = None
            self.level = 0
            self.points = 0

class MatchKey:
    def __init__(self, matchCode):
        self.server, self.numericKey = matchCode.split("_")
        self.key = matchCode

#TODO: split into Match and PlayerInMatch (for Match with PUUID)?
class Match:
    def __init__(self, matchData, summonerPUUID=None):
        if isinstance(matchData, MatchKey):
            matchData = getMatchInfo(matchData)
        try:
            self.gameEndTimestamp = int(matchData["info"]["gameEndTimestamp"])
        except KeyError:
            self.gameEndTimestamp = int(matchData["info"]["gameStartTimestamp"]) #MATCH-V4?
        modeData = getModeFromQueueID(matchData["info"]["queueId"])
        self.map = modeData["map"]
        self.modeDescription = modeData["description"] #this sucks
        if self.map == "Summoner's Rift":
            self.position = getRoleFromMatch(matchData, summonerPUUID) #this is horrible, this entire class needs better structure
        else:
            self.position = "Unknown"
        #TODO: adding class members as neccesary.

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
        # self.rank = getRank(self.summonerName) #TODO - adding as neccesary, v5 screwed up classes

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
        if "gameQueueConfigId" in data:
            self.gameMode = getModeFromQueueID(data["gameQueueConfigId"])["description"]
        else:
            self.gameMode = "Custom Match"
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
        if datetime.timestamp(self.startTime) < 0:
            self.elapsedTime = -1
        else:
            self.elapsedTime = (datetime.now() - self.startTime).seconds
        self.spectatorKey = data["observers"]["encryptionKey"]

class NullSumm: # TODO - add use cases instead of returning Nonetype in summ
    def __init__(self, name):
        self.name = name

class Summoner():
    def __init__(self, data):
        if isinstance(data, str): # i dont rly like this
            self = getSummonerData(data)
        self.eaid = data["accountId"]
        self.esid = data["id"]
        self.puuid = data["puuid"]
        self.name = data["name"]
        self.icon = data["profileIconId"]
        self.timestamp = data["revisionDate"]
        self.level = data["summonerLevel"]
    
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
        return ChampionMastery(response.json())

    def getRank(self):
        return getRankedData(self) # bad!!!!!!!!!!!!!!!!!!!!


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
        if n == q.lower(): # there HAS to be a way to refactor all these conditions 
            return id      # rn this is the best solution to solve the "sh" -> "ashe" error
    for id, n in champs.items():
        n = n.lower()
        if n.replace('\'', " ") == q.lower():
            return id
    for id, n in champs.items():
        n = n.lower()
        if n.replace('.', " ") == q.lower():
            return id
    for id, n in champs.items():
        n = n.lower()
        if n.replace('\'', "") == q.lower():
            return id
    for id, n in champs.items():
        n = n.lower()
        if n.replace('.', "") == q.lower():
            return id
    for id, n in champs.items():
        n = n.lower()
        if n.replace(' ', "") == q.lower():
            return id
    for id, n in champs.items():
        n = n.lower()
        if n[0:len(q)] == q[0:len(q)].lower(): #bound to size of query
            return id
    for id, n in champs.items():
        n = n.lower()
        if q.lower() in n.lower():
            return id
    return -1 # returns -1 if no match

def getCorrectChampName(q):
    cID = getChampIdByName(q)
    return getChampNameById(cID)

def getRole(role, lane): #delete? see getPosition
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

def getRoleFromMatch(matchData, summonerPUUID):
    for player in matchData["info"]["participants"]:
        if summonerPUUID == player["puuid"]:
            return (getTeamPosition(player["teamPosition"]))
    return "Unknown"

def getTeamPosition(positionStr):
    # MATCH-V5 includes teamPosition, an automatically calculated
    # position which is much easier to use than LANE and ROLE
    posDict = {
        "MIDDLE": "Middle",
        "TOP": "Top",
        "JUNGLE": "Jungle",
        "BOTTOM": "Bottom",
        "UTILITY": "Support",
    }
    if positionStr in posDict:
        return posDict[positionStr]
    else:
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

def updateMatchBase(force=False, clean=True):
    def push():
        if clean:
            cleanMatchBase()
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
            #TODO: update this to match-v5 gameId format (in [metadata][id], but needs confirmation)
            #commented out for now
            pass
            # print(f"Dead match found: {entry}")
            # deleteList.append(entry)
    for entry in deleteList:
        pulledMatches.pop(entry)
    updateMatchBase(force=True, clean=False)

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
    code = response.status_code
    if code != 200:
        if code == 429:
            raise RateLimitError
        if code == 404: #TODO: raise error here, not a level down
            return None
        print(f"Error {code} in getSummonerData wasn't explicitly handled. Returning Nonetype.")
        return None #this is horrible lol
    else: return Summoner(summonerData)

def getRankedString(s, hasLP=False, hasWR=False, deco=False, hasGP=False, queue="RANKED_SOLO_5x5"): #only works with default rank right now
    def parseRank(div, tier):
        divList = {
            #"V": "5",
            "IV": "4",
            "III": "3",
            "II": "2",
            "I": "1",
        }
        tierList = {
            "IRON": "I",
            "BRONZE": "B",
            "SILVER": "S",
            "GOLD": "G",
            "PLATINUM": "P",
            "DIAMOND": "D",
            "MASTER": "Master",
            "GRANDMASTER": "GM",
            "CHALLENGER": "Challenger"
        }
        apex = ["MASTER", "GRANDMASTER", "CHALLENGER"]
        if tier in apex:
            return tier.capitalize()
        return f"{tierList[tier]}{divList[div]}"

    try:
        data = getRankedData(s)
    except: #TODO: what error?
        raise RateLimitError
    wr, g = 0, 0 #init to cover case when no ranked data
    found = False
    if isinstance(data, list):
        for q in data:
            try:
                if q.queue == queue:
                    found = True
                    rank = parseRank(q.division, q.tier)
                    lp = q.lp
                    if hasWR:
                        g = (q.wins+q.losses)
                        if g == 0:
                            hasWR = False #no games, will break wr calc
                            break
                        wr = (100*q.wins)/g
            except TypeError:
                if q == "status": #what
                    print(f"TypeError caught in getRankedString() - {vars(q)}")
                    return None
    else: return ""

    wrStr = ""
    lpStr = ""
    gpStr = ""
    if hasWR:
        if hasGP:
            gpStr = f", {g}g"
        deco = ''
        if wr < 44.5 and g >= 50: # 5.5% edge considered significant (5/9 theory)
            deco = '*'            # 50 games arbitrarily considered significant
        elif wr > 55.5 and g >= 50:
            deco = '**'
        wrStr = f"({deco}{wr:.1f}%{deco}{gpStr})"
    if hasLP:
        lpStr = f", {lp} LP "

    if found:
        return (f"{rank}{lpStr} {wrStr}")
    else: return ""

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
    if response.status_code == 429:
        raise RateLimitError
    datajson = response.json()
    data = []
    for i in range(len(datajson)):
        try:
            name = datajson[i]["summonerName"]
        except:
            name = summoner.name
        rankData = Rank(datajson[i], name)
        try:
            test = rankData.tier
            data.append(Rank(datajson[i], name))
        except AttributeError:
            pass
    if len(data) > 0:
        return data # list of Rank objects
    else: return summoner

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
    tierDict = {
        "IRON": 0.3,
        "BRONZE": 0.5,
        "SILVER": 0.8,
        "GOLD": 1,
        "PLATINUM": 2,
        "DIAMOND": 4,
        "MASTER": 10,
        "GRANDMASTER": 20,
        "CHALLENGER": 50
    }
    divDict = {
        "IV": 0.9,
        "III": 1,
        "II": 1.1,
        "I": 1.2,
    }
    return round((tierDict[tier] * divDict[div])**2, 2)

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

def embedRankedData(summoner):
    data = getRankedData(summoner) # either False or data
    if checkKeyInvalid():   
        raise KeyExpiredError
    if data == False:
        raise SummonerNotFoundError
    try:
        summonerName = data[0].name
    except:
        summonerName = data.name
        data = []
    title=f"{summonerName}  -  Ranked Status"
    description, rankDict = "", []
    color = 0x64686e
    for i in range(0, len(data)):
        rank = parseRank(data[i].tier, data[i].division)
        queueName = parseQueue(data[i].queue)
        lp, wins, losses, gamesPlayed, winRate = data[i].lp, data[i].wins, data[i].losses, data[i].gp, ((data[i].wins * 100) / (data[i].gp))
        awr = (wins+10)*100 / (gamesPlayed+20) # 3b1b's method of review checking, applied to winrate
        rankMultiplier = calculateRankMultiplier(data[i].tier, data[i].division)
        # currently testing Carry Factor        
        carryFactor = ((winRate/100)-(4/9))*9
        # methodology in helpfile
        # end testing
        rankedScore = int((wins**2.5 * winRate)*rankMultiplier / gamesPlayed)
        description += (f"**{queueName}** - **{rank}** - {lp} LP")
        description += "\n"
        description += (f"({wins} wins, {losses} losses - {round(winRate, 2)}% winrate)")
        description += "\n"
        #description += (f"*{round(awr, 2)}% adjusted winrate*") #using carry factor for now
        if (queueName == "Solo/Duo"):
            if (gamesPlayed >= CARRY_FACTOR_UNLOCK):
                description += (f"*Carry Factor: {round(carryFactor, 3)}*")
            elif gamesPlayed == CARRY_FACTOR_UNLOCK-1:
                description += ("*Carry Factor unlocks in 1 more game.*")
            else:
                description += (f"*Carry Factor unlocks in {CARRY_FACTOR_UNLOCK-gamesPlayed} more games.*")
            description += "\n"
        description += (f"*Queue Ranked Score: {rankedScore:,}*")
        description += "\n"
        description += "\n"
        rankDict.append(data[i].tier)
    if len(rankDict) > 0:
        color = getTierColor(getMaxRank(rankDict))
        footer = "try s!info carryfactor"
    else:
        color = 0x64686e
    if description == "": #no data returned
        lastMatch = getLastMatch(summoner, True)
        if lastMatch == None:
            description = "This summoner isn't ranked in any queues yet!"
        else:
            lastMatch = Match(lastMatch)
            lastMatchEnd = datetime.fromtimestamp(int(lastMatch.gameEndTimestamp)/1000)
            if lastMatchEnd > SEASON_12_START_TIME:
                description = "This summoner is in the middle of their placement matches, so ranked data isn't available."
            else:
                description = "This summoner isn't ranked in any queues yet!"
    return discord.Embed(title=title, description=description, color=color, footer=footer)

def anonGetSingleMastery(summoner, champ):
    if isinstance(summoner, str):
        summoner = getSummonerData(summoner)
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
        return "no"
    elif response.status_code == 429:
        raise RateLimitError
    return ChampionMastery(response.json())
    
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
    masteryList = []
    for i in range(0, 3): #top three masteries, can be altered
        try:
            masteryList.append(ChampionMastery(response.json()[i]))
        except:
            break # if none left, ie. two or less champs
    return masteryList

def embedTopMasteries(s):
    if checkKeyInvalid():
        return False
    data = getTopMasteries(s)
    title=f"{s}  -  Top Masteries"
    description = ""
    for item in data:
        l = item.level
        n = item.champ
        p = item.points
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

#TODO: make this class -> pickle it

def addRegistration(id, name):
    summoner = getSummonerData(name)
    if summoner == None:
        return False  # summoner does not exist
    try:
        users[str(id)]["lol"] = str(summoner.name)
    except KeyError:
        users[str(id)] = {}     # initialize userdata
        users[str(id)]["lol"] = str(summoner.name)
    updateUserData()
    return (summoner.name) # confirms with properly capitalized name

def getMatchHistory(name, ranked=False, matchCount=MATCH_LIMIT):
    summoner = getSummonerData(name)
    if checkKeyInvalid():
        raise KeyExpiredError
    rankedParam = ""
    if ranked:
        rankedParam = "queue=420&"
    data = requests.get(
            (v5url + f"/lol/match/v5/matches/by-puuid/{summoner.puuid}/ids?{rankedParam}count={matchCount}"),
            headers = headers
        )
    if data.status_code == 400:
        return "sum"
    matchList = []
    try:
        for match in list(data.json()):
            matchList.append(MatchKey(match))
    except KeyError:
        pass
    return matchList

def getLastMatch(name, ranked=False):
    data = getMatchHistory(name, ranked, matchCount=1)
    if data == []:
        return None
    return data[0]

def getMatchInfo(match, autosave=True):
    if isinstance(match, int):
        gameID = match
    if isinstance(match, MatchKey):
        gameID = match.key
    else:
        gameID = match.gameID
    if str(gameID) in pulledMatches:
        return pulledMatches[str(gameID)]
    data = requests.get(
            (v5url + f"/lol/match/v5/matches/{gameID}"),
            headers = headers
        )
    if data.status_code == 400:
        return "sum"
    elif data.status_code == 429:
        raise RateLimitError
    else:
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
    #TODO - this is unfinished

def didPlayerWin(summonerId, matchData):
    try:
        for player in matchData["info"]["participants"]:
            if summonerId == player["summonerId"]:
                return (player["win"])
    except KeyError:
        print(matchData)
        print("RATE LIMIT EXCEEDED!")
        raise RateLimitError

def bulkPullMatchData(matchList, max=MATCH_LIMIT):
    pullList = [] #stupid pass by sharing !!!
    for match in matchList:
        if str(match.key) not in pulledMatches:
            pullList.append(match)
    if len(pullList) > max:
        pullList = pullList[0:max]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        res = [executor.submit(getMatchInfo, game.key, autosave=False) for game in pullList]
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

def getWinLossTrend(summonerName, maxMatches=MATCH_LIMIT, ranked=False, turboMode=True):
    data = getSummonerData(summonerName)
    if data == None:
        raise RateLimitError
    summonerName = data.name
    sID = data.esid
    matchList = getMatchHistory(data, ranked)[0:maxMatches]
    if turboMode:
        bulkPullMatchData(matchList)
    wins = 0
    losses = 0
    awr = 0 #adjusted winrate
    maximum = 0
    value = 1 #TODO: this needs tuning my 3r dropped after winning several games
    for i in range(len(matchList)):
        win = didPlayerWin(sID, getMatchInfo(matchList[i]))
        if win:
            wins += 1
            awr += value
        else:
            losses += 1
        maximum += value
        value *= ADJ_WINRATE_DECAY_CONSTANT
    awr = (awr/maximum)
    g = wins + losses
    return {"record":(wins, losses, g), "awr":awr, "name": summonerName} #TODO: make class

async def parseWinLossTrend(summoner, message, maxMatches=MATCH_LIMIT, ranked=False):
    #make embed later #slow
    title = "Retrieving data..."
    text = "This may take a while if this summoner's match history hasn't recently been pulled."
    embed = discord.Embed(title=title, description=text)
    sentMessage = await message.channel.send(embed=embed)

    try:
        data = getWinLossTrend(summoner, maxMatches, ranked)
    except (RateLimitError, SummonerNotFoundError) as error:
        await sentMessage.delete()
        raise error

    w = data["record"][0]
    l = data["record"][1]
    gp = data["record"][2]
    awr = data["awr"]*100 #adjusted winrate
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
        text += f"Recent-weighted Rating: **+{deltawr:.2f}** points\n"
    else:
        color = 0xd33737
        title = f"{name} - Winrate Analysis ({deltawr:.2f})"
        text += f"Recent-weighted Rating: **{deltawr:.2f}** points\n"
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

#TODO: slow command, overcalls?
def timeSinceLastMatch(name, ranked=False):
    if checkKeyInvalid():
        raise KeyExpiredError
    try:
        name = getSummonerData(name).name
    except AttributeError:
        raise SummonerNotFoundError
    lastMatch = getLastMatch(name, ranked)
    if lastMatch == None:
        raise NoRecentMatchesError(name)
    
    now = datetime.now()
    lastMatch = Match(lastMatch)
    lastMatchEnd = datetime.fromtimestamp(int(lastMatch.gameEndTimestamp)/1000)
    totalSeconds = int((now-lastMatchEnd).total_seconds())
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
    return {"name":name, "time":f"{p(days, 'day')}, {p(hours, 'hour')}, {p(minutes, 'minute')}, {p(seconds, 'second')}"}

def getRoleHistory(name, ranked=False, weightedMode=False):
    try:
        summoner = getSummonerData(name)
        name = summoner.name
    except KeyError:
        raise SummonerNotFoundError
    matchList = getMatchHistory(name, ranked) # all games
    matchHistory = list() # only SR games
    for match in matchList:
        match = Match(match, summoner.puuid)
        if match.position != None:
            matchHistory.append(match)
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
    value = 1
    for i in range(len(matchHistory)):
        match = matchHistory[i]
        if match.map != "Summoner's Rift": #and (match.position == "Unknown")
            gp -= 1
            continue #don't count non-SR games
        if weightedMode:
            roleDict[match.position] += value
            totalWeight += value
            value *= ADJ_WINRATE_DECAY_CONSTANT
        else:
            roleDict[match.position] += 1
    if weightedMode:
        for role in roleDict:
            roleDict[role] = 100*roleDict[role]/totalWeight
    return {"name": name, "roles": roleDict, "games": gp}

def getTopRoles(data):
    primary, secondary = None, None
    temp = dict(data) # pass by sharing workaround
    temp.pop("Unknown")
    primary = max(temp, key=temp.get)
    temp.pop(primary)
    secondary = max(temp, key=temp.get)
    return primary, secondary

async def getRolePlayDataEmbed(message, name, ranked=False):
    try:
        title = "Retrieving data..."
        text = "This may take a while if this summoner's match history hasn't recently been pulled."
        embed = discord.Embed(title=title, description=text)
        sentEmbed = await message.channel.send(embed=embed)
        try:
            name = getSummonerData(name).name
        except AttributeError:
            raise SummonerNotFoundError
        rh = getRoleHistory(name, ranked=ranked, weightedMode=True)
        if rh == "key":
            raise KeyExpiredError
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
            if not (role == "Unknown" and freq == 0): #don't show unknown if 0%
                description += f"{format}{freq:.2f}% {role}{format}\n"
        title = f"{name} likely queues for **{primary}**/*{secondary}*."
        rt = ""
        if ranked:
            rt = "ranked "
        footertext = f"{gp} {rt}SR games analyzed."
        embed.title=title
        embed.description=description
        embed.color=discord.Color.random()
        embed.set_footer(text=footertext)
        await sentEmbed.edit(embed=embed)
    except (KeyExpiredError, SummonerNotFoundError, ZeroDivisionError) as error:
        if isinstance(error, KeyExpiredError):
            await sentEmbed.delete()
            await message.channel.send("Key expired.")
        if isinstance(error, SummonerNotFoundError):
            await sentEmbed.delete()
            await message.channel.send("Summoner not found.")
        if isinstance(error, ZeroDivisionError):
            await sentEmbed.delete()
            if ranked:
                await message.channel.send("That summoner hasn't played any ranked matches!")
            else:
                await message.channel.send("That summoner hasn't played any matches!")

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
    if summoner == "rate":
        return "rate"
    data = requests.get(
            (url + f"/lol/spectator/v4/active-games/by-summoner/{summoner.esid}"),
            headers = headers
        )
    if data.status_code == 429:
        return "rate"
    elif data.status_code == 404:
        return "no"
    else: return LiveMatch(data.json(), summoner)


async def getLiveMatchEmbed(summoner, message, hasRanked=False):

    class PlayerString():
        def __init__(self, data, hasRanked):
            self.summoner = data["summoner"]
            self.champ = data["champ"]
            if hasRanked:
                self.rank = data["rank"]
            self.team = data["team"]

    def parseLiveMatchPlayerString(player):
        masteryStr = ""
        rankStr = ""
        level, points = 0, 0
        targetName = match.targetPlayer.summonerName
        summoner = getSummonerData(player.summonerName)
        if player.summonerName == targetName:
            summonerName = f"*{player.summonerName}*"
        else:
            summonerName = player.summonerName
        if summoner == "rate":
            raise RateLimitError
        champData = (anonGetSingleMastery(player.summonerName, player.champID))
        codes = ["no", "rate"]
        if champData not in codes:
            if hasRanked:
                # rankedData = (summoner.getRank(hasWR=False, deco=True))
                rankedData = getRankedString(summoner, hasWR=False, deco=True)
                if rankedData == "rate":
                    raise RateLimitError
                elif rankedData != "":
                    rankStr = rankedData
                else:
                    rankStr = f"Lv. {summoner.level}"
            level, points = champData.level, (champData.points/1000) # points in 1000s
            msDec = ""
            if level >= 3:
                if points >= MASTERY_TIER_4_BREAKPOINT:
                    msDec = "`"
                    # masteryStr = f"{msDec}(M{level} / {points:.2f}M){msDec}" # too long, maybe use showLevel flag?
                    masteryStr = f"{msDec}({(points/1000):.2f}M){msDec}"
                else:
                    if points >= MASTERY_TIER_3_BREAKPOINT:
                        msDec = "***"
                    elif points >= MASTERY_TIER_2_BREAKPOINT:
                        msDec = "**"
                    elif points >= MASTERY_TIER_1_BREAKPOINT:
                        msDec = "*"
                    # masteryStr = f"{msDec}(M{level} / {points:.1f}K){msDec}" # too long
                    masteryStr = f"{msDec}({points:.1f}K){msDec}"
        elif champData == "rate":
            raise RateLimitError
        data = {
            "summoner": summonerName,
            "champ": f"{player.champName}  {masteryStr}",
            "rank": rankStr,
            "team": player.teamID
        }
        return PlayerString(data=data, hasRanked=hasRanked)
    
    def dumpFile():
        try:
            file = open(f"{str(match.gameID)}.txt", "x")
            file.write(f"Game timer might have failed! Dumping game log: {vars(match)}")
            file.close()
        except:
            pass
    
    try:
        title = "Requesting match data..."
        description = "Hang tight!"
        embed = discord.Embed(title=title, description=description)
        sentEmbed = await message.channel.send(embed=embed)
        if isinstance(summoner, str):
            data = getSummonerData(summoner)
            if data == None:
                raise SummonerNotFoundError
        summoner = data
        match = getLiveMatch(summoner)
        if match == "rate":
            raise RateLimitError
        if isinstance(match, str):
            if match == "rate":
                raise RateLimitError
            elif match == "no":
                raise SummonerNotInMatchError

        text = ""
        if match.targetPlayer.teamID == 100:
            embed.color = 0x3366cc    # blue
        else: embed.color = 0xff5050  # red
        embed.title = "Requesting data..."
        embed.description = text

        ## test code
        # res = []
        # for player in match.participants.values():
        #     print(parseLiveMatchPlayerString(player))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            res = executor.map(parseLiveMatchPlayerString, match.participants.values()) #create executor map of results

        # 5 workers tested to be most optimal for all setups

        blueSumms = ""
        blueChamps = ""
        blueRanks = ""

        redSumms = ""
        redChamps = "" # gotta be a better way to do this?
        redRanks = ""  # maybe lists but i still have to iterate

        for playerString in res:
            if playerString == "rate":
                raise RateLimitError
            else:
                if playerString.team == 100:
                    blueSumms += (playerString.summoner) + "\n"
                    blueChamps += (playerString.champ) + "\n"
                    if hasRanked:
                        blueRanks += (playerString.rank) + "\n"
                elif playerString.team == 200:
                    redSumms += (playerString.summoner) + "\n"
                    redChamps += (playerString.champ) + "\n"
                    if hasRanked:
                        redRanks += (playerString.rank) + "\n"

        embed.add_field(name="Blue Players", value=blueSumms, inline=True)
        embed.add_field(name="Champions", value=blueChamps, inline=True)
        if hasRanked:
            embed.add_field(name="Ranks", value=blueRanks, inline=True)
        else: embed.add_field(name = chr(173), value = chr(173)) # null field

        embed.add_field(name="Red Players", value=redSumms, inline=True)
        embed.add_field(name="Champions", value=redChamps, inline=True)
        if hasRanked:
            embed.add_field(name="Ranks", value=redRanks, inline=True)
        else: embed.add_field(name = chr(173), value = chr(173))

        embed.description = text
        elapsed = match.elapsedTime
        if not (0 <= elapsed <= 90*60):
            title = f"Live Match - Loading In - {match.gameMode}"
            dumpFile()
        else:
            m, s = divmod(elapsed, 60)
            if m >= 60:
                embed.set_footer(text="Time may be inaccurate")
                dumpFile()
                m = m % 60
            title = f"Live Match - {m}:{s:02d} elapsed - {match.gameMode}"
        embed.title = title
        await sentEmbed.edit(embed=embed)
        return True
    except (RateLimitError, SummonerNotInMatchError, SummonerNotFoundError) as error:
        if isinstance(error, RateLimitError):
            embed.title = ":rotating_light: Rate limit reached! "
            embed.description = (":rotating_light:\n Use `info ratelimit` " +
                                "for more information. " +
                                "Wait about a minute before trying again.")
            await sentEmbed.edit(embed=embed)
        if isinstance(error, SummonerNotInMatchError):
            embed.title = "Match not found"
            embed.description = f"Summoner {summoner.name} isn't in a match right now!"
            await sentEmbed.edit(embed=embed)
            return False
        if isinstance(error, SummonerNotFoundError):
            embed.title = "Summoner not found"
            embed.description = f"Summoner {summoner} doesn't seem to exist."
            await sentEmbed.edit(embed=embed)
            return False

def ddGetAbilityName(message): # dd = datadragon
    def parseQuery(q):
        if q == "Renata Glasc":
            return "Renata"
        return q.replace(".", "").replace('\'', "").replace(" ", "")

    ValidCodes = ['q','w', 'e', 'r', 'ult', 'ultimate', 'ulti', 'p', 'passive', 'pass']

    champ, code = None, None # fix this
    try:
        test1, test2 = message.split(" ")
        if test2 in ValidCodes:
            champ, code = test1, test2
    except ValueError:
        for testCode in ValidCodes:
            if len(testCode) >= 2 and message.endswith(testCode):
                code = testCode
                champ = message.replace(testCode, "").strip()

    if (champ, code) == (None, None): # no longer code hit
        champ, code = message[:-1].strip(), message[-1:].strip()
        if code not in ValidCodes:
            return None, None

    champ = getCorrectChampName(champ)
    if champ == "None":
        return None, None
    if code in ['ult', 'ultimate', 'ulti']:
        code = 'r'
    if code in ['passive', 'pass']:
        code = 'p'
    champKey = parseQuery(champ)
    response = requests.get( # TODO - use the ddrag file
                (f"http://ddragon.leagueoflegends.com/cdn/{CurrentPatch}/data/en_US/champion/{parseQuery(champKey)}.json"),
            )
    if response.status_code == 403:
        return "err", "err"
    data = response.json()
    spellDict = {
        'q': data["data"][champKey]["spells"][0]["name"],
        'w': data["data"][champKey]["spells"][1]["name"],
        'e': data["data"][champKey]["spells"][2]["name"],
        'r': data["data"][champKey]["spells"][3]["name"],
        'p': data["data"][champKey]["passive"]["name"],
    }
    return champ, spellDict[code]

def getWikiLink(message):
    #TODO: make this a bit nicer? too bad you cant do custom link text, but just a raw link is ugly
    def scoreSpaces(input):
        if input == None or input == "None": # stupid gCCN returns string
            return None
        return input.replace(" ", "_")
    
    def isNoCode(message):
        if getCorrectChampName(message) == getCorrectChampName(message[:-1]):
            if (message[-1]) in ['q', 'w', 'e', 'r', 'p']:
                if getCorrectChampName(message) != "None": # fn returns string instead of None ugh
                    return True
    
    def getFormat(q):
        return scoreSpaces(getCorrectChampName(q))

    message = message.capitalize().strip()

    # assume passed champ + ability
    champ, spell = ddGetAbilityName(message)
    
    try: #TODO: make these Discord.py errors
        if champ == "err": # out of date?
            return "Something went wrong. Riot's API might be down."
        if isNoCode(message): # assume no ability code + long enough #TODO: why just getFormat(message)? elegant but confusing
            return f"<https://leagueoflegends.fandom.com/wiki/{getFormat(message)}/LoL>"
        elif champ != None and spell != None: # result passed # TODO - "she" erroneously becomes "ashe / e"
            champ, spell = scoreSpaces(champ), scoreSpaces(spell)
            return f"<https://leagueoflegends.fandom.com/wiki/{champ}/LoL#{spell}>"
        elif getFormat(message) != None and len(message) >= 2: # separate case if can be refactored later
            return f"<https://leagueoflegends.fandom.com/wiki/{getFormat(message)}/LoL>"
    except: # something threw exception
        return "Something went wrong. Let <@312012475761688578> know."

def lobbyRankedReport(message):
    def getReport(name):
        description = ""
        if isinstance(name, Summoner):
            description += (f"{name.name} - ")
            description += (f"{getRankedString(name, hasWR=True, hasGP=True, deco=True)}\n") #thread this? idk
        elif isinstance(name, NullSumm):
            description += (f"Couldn't get data for {name.name}\n")
        return description
    
    embed = discord.Embed(color=0x728cf3)

    message = message.replace("joined the lobby", "").split("\n")
    names = []
    for name in message:
        currentName = getSummonerData(name.strip())
        if isinstance(currentName, Summoner): 
            names.append(currentName)
        else:
            names.append(NullSumm(name))
    
    description = ""

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        res = [executor.submit(getReport, name) for name in names]
    
    for playerString in res:
        description += playerString.result()
    
    embed.description = description
    embed.title = "Lobby Overview"
        
    return embed