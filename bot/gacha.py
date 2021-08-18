
import json, random, datetime

gachaDict = dict()

class OwnedGachaItem:
    def __init__(self, stockItem, user):
        pass

class StockGachaItem:
    def __init__(self, data):
        self.name = data["name"]
        self.rarity = data["rarity"]
        self.baseValue = data["value"]
    
    def getUserItemInstances(self, userID):
        # return all OGIs of a certain item class
        pass
    
    def createOwnedItem(self, userID):
        # generate random values for value, quality, attack/defense?????? other stats
        # 
        pass


with open('bot/resources/data/gachaList.json') as f:
    data = list(json.loads(f.read())) # unpacking data
    for item in data:
        item = StockGachaItem(item)
        gachaDict[item.name] = item
    f.close()



# with open('bot/resources/data/gachaStats.json') as f:
#     data = json.loads(f.read()) # unpacking data
#     gachaStats = data
#     f.close()
