from dotenv import load_dotenv
import requests, os, json

load_dotenv()
RIOTTOKEN = os.getenv('RIOTTOKEN')
headers = {"X-Riot-Token": RIOTTOKEN}
url = "https://na1.api.riotgames.com"

def parseSpaces(s):
    return s.replace(" ", "%20")
    
def getLevel(s):
    s = parseSpaces(s)
    response = requests.get(
        (url + f"/lol/summoner/v4/summoners/by-name/{s}"),
        headers = headers
    )
    summonerData = json.loads(response.text)
    return summonerData["name"], int(summonerData["summonerLevel"])