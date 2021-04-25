import random, discord, os, decimal, json, time
# import xfunc.data.pkmn as pkmn

def flipCoin():
    coin = random.randint(0, 1)
    if coin == 0:
        return "heads"
    return "tails"

def die(n):
    return random.randint(1, n)

def sobbleImage():
    return (discord.File(fp=("bot/pics/" + (random.choice(os.listdir("bot/pics")))), filename="sobble.png"))

def parseMath(exp):
    try:
        add = exp.find('+')
        sub = exp.find('-')
        mult = max(exp.find('x'), exp.find('*'))
        div = exp.find('/')
        expo = exp.find('^')

        s = [add, sub, mult, div, expo]
        ops = s.count(-1)
        if ops < len(s)-1:
            pass
            # return "Parse failed - too complex or malformed equation. (Error 1)"
        elif ops == len(s):
            pass
            # return "Parse failed - no simple operator found. (Error 2)"
        else:
            try:
                i = max(s)
                a = decimal.Decimal(exp[:i])
                b = decimal.Decimal(exp[i+1:])
                if add != -1:
                    return str(a + b)
                elif sub != -1:
                    return str(a - b)
                elif mult != -1:
                    return str(a * b)
                elif div != -1:
                    if b == 0:
                        return "Even Sobble can't divide by zero!"
                    return str(a / b)
                elif expo != -1:
                    if a * b > 1000:
                        return "Those numbers overwhelmed poor Sobble - they're a little too big."
                    return str(a ** b)
                else:
                    return "Major error - Get this checked out. (Error 3)"
            except Overflow:
                return "Sobble lost count - your numbers were a little too big."
    except:
        pass
        # return "Parse failed - Exception caught. (Error 4)"

def findDex(n):
    # passes dex number to pkmnLookup if reverse search is successful
    n = n.lower()
    pkmn = open('bot/xfunc/data/pkmn.json')
    data = json.load(pkmn)
    for k in data:
        if data[k]["name"] == n:
            return int(k)
    return -1

def pkmnLookup(n):
    final = None
    try:
        n = int(n)
    except:
        res = findDex(str(n))
        if res != -1:
            n = res
        else:
            return final 
    finally:
        if isinstance(n, int) and n >= 1 and n <= 898:
            # should be done as a dictionary i think? but it ruins my fstrings so whatever
            pkmn = open('bot/xfunc/data/pkmn.json')
            data = json.load(pkmn)
            localdata = {}
            name = data[str(n)]["name"]
            art = data[str(n)]["art"]

            if data[str(n)]["typeCount"] == 1:
                type1 = data[str(n)]["type1"]
                final = discord.Embed(
                    title=str(f"**{(name)}**, number {n}"),
                    description=(type1),
                    colour=discord.Colour.random()
                    )

            else:
                type1 = data[str(n)]["type1"]
                type2 = data[str(n)]["type2"]
                final = discord.Embed(
                    title=str(f"**{(name)}**, number {n}"),
                    description=f"{(type1)}, {(type2)}",
                    colour=discord.Colour.random()
                    )

            final.set_image(url=(art))
            pkmn.close()
        return final

def timeRunning(c):
    s = time.time() - c
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    d, h, m, s = int(d), int(h), int(m), int(s)
    if d == h == m == s == 0:
        q = f"under a second!"
    if d == h == m == 0:
        q = f":{s}!"
    elif d == h == 0:
        q = f"{m}:{s}!"
    elif d == 0:
        q = f"{h}:{m}:{s}!"
    else:
        q = f"{d}d {h}:{m}:{s}!"
    return ("Sobbot has been online for " + q)
