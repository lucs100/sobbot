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
            sleep(3)
            r.bulkPullMatchData(r.getMatchHistory(summoner))
            sleep(3)
            clear("Script on cooldown. It is safe to kill the script.")
            print(f"Current matches: {len(r.pulledMatches)} ({beforeCycle})")
            sleep(120)
        if len(r.pulledMatches) == beforeCycle: # max pulled
            print("Pulled all matches! Exiting.")
            exit()

additionalNames = []
while True:
    name = input("Enter a name to add it to the list. Press Enter to start.")
    if name == "":
        break
    else:
        additionalNames.append(name)

script(additionalNames)