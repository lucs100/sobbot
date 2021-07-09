import riotapi as r
from time import sleep

def clear(message):
    print("\n" * 100)
    print(message)

def script(additionals):
    mList = additionals + r.summonerList
    while True:
        for summoner in mList:
            clear("SCRIPT RUNNING! Do not kill this script, you could corrupt the match table.")
            r.bulkPullMatchData(r.getMatchHistory(summoner))
            sleep(3)
            clear("Script on cooldown. It is safe to kill the script.")
            sleep(180)