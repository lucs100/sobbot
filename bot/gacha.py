
import json, random

gachaDict = dict()

class GachaItem:
    def __init__(self, data):
        self.name = data["name"]
        self.rarity = data["rarity"]
        self.baseValue = data["value"]

with open('bot/resources/data/gachaList.json') as f:
    data = list(json.loads(f.read())) # unpacking data
    for item in data:
        item = GachaItem(item)
        gachaDict[item.name] = item
    print(gachaDict)
    f.close()

# with open('bot/resources/data/gachaStats.json') as f:
#     data = json.loads(f.read()) # unpacking data
#     gachaStats = data
#     f.close()
