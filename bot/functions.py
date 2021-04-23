import random, discord, os

def flipCoin():
    coin = random.randint(0, 1)
    if coin == 0:
        return "heads"
    return "tails"

def die(n):
    return random.randint(1, n)

def sobbleImage():
    return (discord.File(fp=("bot/pics/" + (random.choice(os.listdir("bot/pics")))), filename="sobble.png"))