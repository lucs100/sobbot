import random, discord, os, decimal, json, time, io
from datetime import datetime
from PIL import Image

# Classes

class RGBSet:
    def __init__(self, r0, g0, b0):
        self.r = r0
        self.g = g0
        self.b = b0
    # helper class for Colour constructor

class Color:
    def __init__(self, data):
        if isinstance(data, str):
            rgbString = data 
            if rgbString.startswith("rgb(") and rgbString[-1] == ")":
                rgbString = rgbString[4:-1]
            self.r, self.g, self.b = (rgbString.split(',')).strip()

        elif isinstance(data, RGBSet):
            self.r = data.r
            self.g = data.g
            self.b = data.b
    
    def getRgbString(self):
        return f"rgb({self.r}, {self.g}, {self.b})"
    
    def getHexString(self):
        return str(hex(self.r)[2:] + hex(self.g)[2:] + hex(self.b)[2:])

    def generateColourEmbed(self):
        color = self.getRgbString()
        colorhex = self.getHexString()
        img = Image.new(mode="RGB", size=(250, 250), color=color)
        arr = io.BytesIO() # save image as datastream to avoid local saving
        img.save(arr, format='PNG')
        arr.seek(0)

        file = discord.File(arr, filename="bluw.png") # pass stream to discord.File
        title = (f"{color}, #{colorhex}")
        embed = discord.Embed(title=title, color=discord.Colour.from_rgb(self.r, self.g, self.b))
        embed.set_image(url="attachment://bluw.png") 
        # discord requires embeds with nonurl files to be sent separately
        return embed, file


# Functions


def flipCoin():
    coin = random.randint(0, 1)
    if coin == 0:
        return "heads"
    return "tails"

def die(n):
    return random.randint(1, n)

def sobbleImage():
    return (discord.File(fp=("bot/resources/pics/sobble/" + (random.choice(os.listdir("bot/resources/pics/sobble")))), filename="sobble.png"))

def parseMath(exp):
    try:
        add = exp.find('+')
        sub = exp.find('-')
        mult = max(exp.find('x'), exp.find('*'))
        div = exp.find('/')
        expo = exp.find('^')
        #counts each operator to determine if only one is found

        s = [add, sub, mult, div, expo]
        ops = s.count(-1)
        if ops < len(s)-1:
            pass
            # too many operators
        elif ops == len(s):
            pass
            # not enough operators
        else:
            try:
                i = max(s) # element with highest value (1 found)
                a = decimal.Decimal(exp[:i])
                b = decimal.Decimal(exp[i+1:]) # two numbers to perform operation on

                if add != -1:
                    return str(a + b)
                elif sub != -1:
                    return str(a - b)
                elif mult != -1:
                    return str(a * b)
                elif div != -1:
                    if b == 0:
                        return "Even Sobbot can't divide by zero!"
                    return str(a / b)
                elif expo != -1:
                    if a * b > 1000:
                        return "Those numbers overwhelmed poor Sobbot - they're a little too big."
                    return str(a ** b)
                else:
                    return "Major error - Get this checked out. (Error 3)"
            except:
                return "Sobbot lost count - your numbers were a little too big."
    except:
        pass
        # unknown error

def findDex(q):
    q = q.lower()
    pkmn = open('bot/resources/data/pkmn.json')
    data = json.load(pkmn)
    for k in data:
        for k in data:
            n = data[k]["name"].lower()
            if n == q.lower(): # search for dex number by name
                return k
            elif q.lower() in n.lower(): # search if any entry name matches part of search, decent algorithm
                return k
    return -1

def pkmnLookup(n):
    final = None
    try:
        n = int(n) # if n is an int, directly search entries
    except:
        res = int(findDex(str(n))) # otherwise, check if findDex returns a result
        if res != -1:
            n = res # n is now found number
        else:
            return final 
    finally:
        if isinstance(n, int) and n >= 1 and n <= 898:
            # should be done as a dictionary i think? but it ruins my fstrings so whatever
            pkmn = open('bot/resources/data/pkmn.json')
            data = json.load(pkmn)
            name = data[str(n)]["name"]
            art = data[str(n)]["art"]
            # compile data

            if data[str(n)]["typeCount"] == 1:
                type1 = data[str(n)]["type1"]
                final = discord.Embed(
                    title=str(f"**{(name)}**, number {n}"),
                    description=(type1),
                    colour=discord.Colour.random()
                    )
            # form an embed, depending on number of types
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
    # find number of each unit sobbot has been running
    d, h, m, s = int(d), int(h), int(m), int(s)
    q = ""
    x = {
        "d": d,
        "h": h,
        "m": m,
        "s": s
    }
    for key, value in x.items():
        if value != 0:
            q += f"{value}{key}" # if a unit is not 0, append it to the string
    if q == "":
        q = "under a second"
    return (f"Sobbot has been online for {q}!")

def randomBlue():
    r = random.randint(40, 60)
    g = random.randint(80, 180)
    b = random.randint(156, 255)
    # generate a random colour within specified bounds
    blueGenerated = Color(RGBSet(r, g, b))
    return blueGenerated.generateColourEmbed()

def randomColour():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    # generate a random colour
    colGenerated = Color(RGBSet(r, g, b))
    return colGenerated.generateColourEmbed()

def printfile(fp):
    textfile = open(fp, 'r')
    lines = textfile.readlines()
    for line in lines:
        print("{}".format(line.strip())) # helper function to print a txt line by line

async def typingIndicator(channel):
    await channel.trigger_typing()
    return True # trivial function

async def pipeline(channel):
    name = channel.name
    guild = channel.guild
    while True:
        for i in range(10):
            print()
        print(f"Channel: #{name}    Server: {guild}")
        printfile("bot/resources/functions/pipeline/pipelineui.txt")
        print() # print console ui for pipeline mode
        try:
            content = str(input()) # message sent
            if content == "":
                await typingIndicator(channel)
            elif content == "s!end":
                return True # end pipeline
            elif content.startswith("s!reply"):
                print()
                message = await(channel.fetch_message(int(content[7:].strip())))
                messagecontent = message.content
                sender = message.author
                print(f"Replying to \"{messagecontent}\" from {sender}.")
                await(message.reply(input())) # reply to a selected message
                print()
            else:
                await(channel.send(content)) # if no command reached, send message
        except:
            pass

def cubeScramble(count = 25):
    # helper function, generates and returns a single move
    def generateRotation(lastRotCode):
        # inits 
        rotationSet = ["U", "R", "F", "D", "L", "B"]
        modificationSet = ["", "", "'", "2"]
        rotIndex, modIndex = 0, 0

        
        if (lastRotCode == -1):
            # choose move without repeat protection
            rotIndex = random.randint(0, 5)
        else:
            # use lastRotCode to make sure move does not match last
            while True:
                rotIndex = random.randint(0, 5)
                if (rotIndex % 3 != lastRotCode % 3):
                    break
        
        lastRotCode = rotIndex
        modIndex = random.randint(0, 3)
        # return concatenated move and hacky PBRed lastRotCode 
        return (rotationSet[rotIndex]+modificationSet[modIndex], lastRotCode)
    
    # init scramble string and last rotation code
    scramble = ""
    lastRotCode = -1
    # apply bounds
    count = max(count, 1)
    count = min(count, 99)
    # create a string of count moves
    for i in range(count):
        move, lastRotCode = generateRotation(lastRotCode)
        scramble += move + " "
        # every 5th move, add a space for readability 
        if i % 5 == 4:
            scramble += "  "
    return scramble
    

# async def setActivity(client):
#     name = "sobling"
#     large_image = "bot/resources/status/sobblelook.png"
#     large_image_text = "sobling"
#     assets = {"large_image": large_image, "large_image_text":large_image_text}
#     start = datetime.fromtimestamp(time.time())
#     await client.change_presence(activity=discord.Activity(name="sobling", assets=assets, start=start))

# this is broken for now, fix someday