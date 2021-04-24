import random, discord, os, decimal

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