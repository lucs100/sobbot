import riotapi as r
from time import sleep
import random 

def clear(message):
    print("\n" * 100)
    print(message)

def script(additionals):
    mList = additionals + r.summonerList
    random.shuffle(mList)
    while True:
        beforeCycle = len(r.pulledMatches)
        for summoner in mList:
            clear("SCRIPT RUNNING! Do not kill this script, you could corrupt the match table.")
            print(f"Current user: {summoner}")
            sleep(10)
            r.bulkPullMatchData(r.getMatchHistory(summoner))
            sleep(3)
            clear("Script on cooldown. It is safe to kill the script.")
            print(f"Current matches: {len(r.pulledMatches)}")
            sleep(120)
        if len(r.pulledMatches) == beforeCycle: # max pulled
            exit()

script()