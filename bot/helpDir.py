import json, discord
import admin

helpData = {}
helpSingles = {}
helpfulGreen = 0x22bb45

#TODO: helpfile may be out of date due to command update. look into help command?

with open('bot/resources/data/help.json') as f:
    data = json.loads(f.read()) # unpacking data
    helpData = data["subdirectories"]
    helpSingles = data["singles"]

def getMainHelpDirectory(message):
    title = "Sobbot - Command Directory"
    px = admin.getGuildPrefix(message.guild.id)
    description = "*Enter one of the following commands to view a help subdirectory.*\n\n"
    for catName, cat in helpData.items():
        description += f"•`{px}help {catName}` - {cat['desc']} :{cat['emoji']}:\n"
    return discord.Embed(title=title, description=description, color=helpfulGreen)

def getHelpDirectory(topic):
    if topic in helpData:
        return helpData[topic]
    return None

def getHelpDirectoryEmbed(message, topic):
    data = getHelpDirectory(topic)
    if data == None:
        return None
    title = f"Sobbot - {data['title']} Command Directory"
    description = ""
    px = admin.getGuildPrefix(message.guild.id)
    if "header" in data:
        if data["header"] != "": # needs to be a successive check
            description += f"*{data['header']}*\n\n"
    for command in data["commands"]:
        description += f"• {px}{command['usage']} - {command['description']}\n"
    return discord.Embed(title=title, description=description, color=helpfulGreen)

def getSingleList(message):
    pf = admin.getGuildPrefix(message.guild.id)
    helpEmbed = discord.Embed()
    helpEmbed.title = "Available Info Blurbs"
    text = f"Use one of the commands below to learn more!\n\n"
    for topic in helpSingles:
        text += f"`{pf}info {topic}`\n"
    text += f"`{pf}about`\n"
    helpEmbed.description = text
    helpEmbed.color = helpfulGreen
    return helpEmbed

def getHelpSingle(message, topic):
    if topic == "":
        return getSingleList(message)
    if topic in helpSingles:
        helpEmbed = discord.Embed()
        helpEmbed.title = helpSingles[topic]["title"]
        helpEmbed.description = helpSingles[topic]["text"]
        helpEmbed.color = helpfulGreen
        return helpEmbed