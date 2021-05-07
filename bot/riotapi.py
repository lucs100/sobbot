from dotenv import load_dotenv
import requests, os, json

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"

def parseSpaces(s):
    return s.replace(" ", "%20")

def checkKeyInvalid():
    response = requests.get(
        (url + f"/lol/status/v4/platform-data"),
        headers = headers
    )
    return not (response.status_code != 401 and response.status_code != 403)

def getSummonerData(s):
    s = parseSpaces(s)
    response = requests.get(
        (url + f"/lol/summoner/v4/summoners/by-name/{s}"),
        headers = headers
    )
    summonerData = json.loads(response.text)
    return summonerData

def getNameAndLevel(s):
    if checkKeyInvalid():
        return False
    summonerData = getSummonerData(s)
    return {"name": summonerData["name"], "level": int(summonerData["summonerLevel"])}