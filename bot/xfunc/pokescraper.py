import requests, json

pkmn = {}
pokeCount = 898
# DO NOT PULL FROM THE API 898 TIMES UNLESS JSON SAVING WORKS THAT WOULD BE SO STUPID  

for n in range(1, pokeCount+1):
    current = requests.get(f"https://pokeapi.co/api/v2/pokemon/{n}/")
    current = json.loads(current.text)

    nDictionary = {
        "name": current["species"]["name"],
        "art": current["sprites"]["other"]["official-artwork"]["front_default"],
        "sprite": current["sprites"]["versions"]["generation-viii"]["icons"]["front_default"],
        "typeCount": len(current["types"])
    }

    if nDictionary["typeCount"] == 1:
        nDictionary["type1"] = (current["types"][0]["type"]["name"])
    elif nDictionary["typeCount"] == 2:
        nDictionary["type1"] = (current["types"][0]["type"]["name"])
        nDictionary["type2"] = (current["types"][1]["type"]["name"])

    # print(json.dumps(nDictionary, indent=2))

    pkmn[n] = nDictionary

# print(json.dumps(pkmn, indent=2))

with open('bot/xfunc/data/pkmn/pkmn.json', 'w', encoding="utf-8") as f:
    json.dump(pkmn, f, ensure_ascii=False, indent=4)

count = len(pkmn)

if count == pokeCount:
    print(f"Complete - {count}/{pokeCount}.")
else:
    print(f"Failed - {count}/{pokeCount}.")

