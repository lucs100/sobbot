from dotenv import load_dotenv
import requests, os, json

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"

champs = {}

with open('bot/func/data/champs.json') as f:
    data = json.loads(f.read())
    champs = data

def getChampNameById(id):
    return champs[str(id)]

def getChampIdByName(id):
    for k in champs:
        n = data[k].lower()
        if n == id.lower():
            return k
        elif n.replace('\'', " ") == id.lower():
            return k
        elif n.replace('.', " ") == id.lower():
            return k
        elif n.replace('\'', "") == id.lower():
            return k
        elif n.replace('.', "") == id.lower():
            return k
        elif id.lower() in n.lower():
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

def getTopMasteries(s):
    response = requests.get(
        (url + f"/lol/champion-mastery/v4/champion-masteries/by-summoner/{getESID(parseSpaces(s))}"),
        headers = headers
    )
    h = response.json()
    print(json.dumps(h, indent=2))