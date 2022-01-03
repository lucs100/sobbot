from logging import disable
import os, discord, time, asyncio, sys

from discord.ext.commands.errors import CheckAnyFailure

import functions as sob
import currency as coin
import spotify as sp
import riotapi, finance, admin, helpDir

from re import match
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')
botCreatorID = os.getenv('CREATORID')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
	command_prefix = "s!",
	intents=intents,
	owner_id = int(botCreatorID),
	help_command=None)

#TODO: edit @bot.command() decorator to record successful function uses?

#TODO: create a real helpcommand using discord-pretty-help


# Classes


# Event Procedures


@bot.event
async def on_ready():
	print(f"{bot.user} initialized.")

	guildCount = 0

	for guild in bot.guilds:
		print(f"Connected to {guild.name} ({guild.id}).")
		guildCount += 1 # print all connected guilds 

	global startTime
	startTime = time.time() # show time connected in console
	timeFormatted = datetime.fromtimestamp(startTime).strftime("%I:%M %p, %B %d %Y")

	print(f"({guildCount}) total connected servers.")
	print(f"{bot.user} is ready!")
	print(f"Time: {timeFormatted}")
	channel = bot.get_channel(835267335169245255) # sobblelink channel
	await channel.send("im conected")
	# await sob.setActivity(bot) #not working yet
	await bot.change_presence(activity=discord.Game(name="sobling")) # placeholder until i set up activity

@bot.event
async def on_guild_join(guild):
	# this doesnt work i dont think
	print("NEW GUILD JOINED!")
	dataString = (
		f"{guild.name} ({guild.id}), " +
		f"owned by {guild.owner}#{guild.owner.discriminator}.")
	print(dataString)
	for channel in guild.text_channels:
		if channel.permissions_for(guild.me).send_messages:
			await channel.send(
				"hi, i'm sobbot! my default prefix in this server is `s!`\n" +
				"use `s!help` to see a list of commands! happy sobbing!\n" +
				"contact lucs#9492 if you have any questions!")
		break
	alertChannel = bot.get_channel(865471884786925568)
	await alertChannel.send("<@312012475761688578> NEW SERVER CONNECTED.")
	await alertChannel.send(dataString)
	await alertChannel.send("IF YOU AREN'T OKAY WITH THIS, TURN OFF SOBBOT IMMEDIATELY.")

@bot.event
async def on_message(message):
	if message.author.id != 835251884104482907: #not from sobbot
		c = (message.content).lower()
		coin.messageBonus(message.author.id) #check droprate for passive coin earning
		
		#special interaction/command messages, do not require prefix
		if message.content == "Jenna": # force caps
			# jenna easter egg hi jenna
			with open("bot/resources/images/misc/jenna.jpeg", "rb") as f:
				picture = discord.File(f)
			await message.channel.send("Jenna", file=picture)

		if c == "hello sobbot":
			await message.channel.send("hi :pleading_face:")
			return True
		
		if match("<@!?835251884104482907>", c) is not None: #matches "@sobbot" exactly
			px = admin.getGuildPrefix(message.guild.id)
			await message.channel.send(f"My current prefix in this server is `{px}`.\n" +
			f"Use `{px}help` for a directory of valid commands!  :blue_heart:")
			return True

		#special channels
		if message.channel.id == 835388133959794699:
			content = sob.parseMath(c)
			if content != None:
				await message.channel.send(content)
				return True

		#TODO: retire this when done command rewrite!
		#prefixed messages
		if c.startswith(admin.getGuildPrefix(message.guild.id)):
			#remove prefix from search
			c = c[len(admin.getGuildPrefix(message.guild.id)):]

			
			# Owner Commands - can only be used by the bot creator.
			

			# if c.startswith("link"):
			# 	if userIsBotOwner(message.author):
			# 		try:
			# 			channelid = int(c[4:].strip())
			# 			channel = bot.get_channel(channelid)
			# 		except:
			# 			return False
			# 		print("Link successful.")
			# 		await sob.pipeline(channel)
			# 		print("Link ended.")
			# 		return True
			# 	else:
			# 		await reportNotOwner(message)
			# 		return False

			
			# Admin Functions
				# check perms before letting these functions proceed!!


			# if c.startswith("prefix"):
			# 	if not (message.author.guild_permissions.manage_guild):
			# 		await message.channel.send("You don't have permission to do that.")
			# 		return False
			# 	id = message.guild.id
			# 	c = c[6:].strip()
			# 	if c == "" or c == None:
			# 		ok = admin.resetGuildPrefix(id)
			# 		if ok == "ok":
			# 			await message.channel.send(f"Prefix reset to `{admin.getGuildPrefix(id)}`!")
			# 		elif ok == "nop":
			# 			await message.channel.send(f"This server is already using the default prefix (`{admin.getGuildPrefix(id)}`)!")
			# 		elif ok == "error":
			# 			await message.channel.send("Something went wrong.")
			# 		return True
			# 	ok = admin.updateGuildPrefix(id, c)
			# 	if ok:
			# 		if c == admin.getGuildPrefix(id):
			# 			await message.channel.send(f"Server prefix is now `{c}`!")
			# 			return True
			# 	await message.channel.send(f"Something went wrong. Server prefix unchanged.")
			# 	return True


			# LoL Functions


			# if c == "lolapireload":
			# 	if message.author.id == 312012475761688578:
			# 		if await riotapi.updateAPIKey():
			# 			await message.channel.send("Successfully set key!")
			# 		else:
			# 			await message.channel.send("Key update failed.")
			# 	else:
			# 		await message.channel.send("You don't have the permissions to do this.")
			
			# if c.startswith("lastmatchr"):
			# 	summoner = c[10:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = riotapi.timeSinceLastMatch(summoner, True)
			# 	codes = {
			# 		"key": "Key expired.",
			# 		"sum": f"Summoner {summoner} doesn't exist.",
			# 		"none": f"Summoner {summoner} hasn't played a ranked match in a while!"
			# 	}
			# 	if isinstance(response, str):
			# 		await message.channel.send(codes[response])
			# 	else:
			# 		await message.channel.send(f"{response['name']}'s last ranked match was {response['time']} ago.")
			# 	return True

			# if c.startswith("lastmatch"):
			# 	summoner = c[9:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = riotapi.timeSinceLastMatch(summoner)
			# 	codes = {
			# 		"key": "Key expired.",
			# 		"sum": f"Summoner {summoner} doesn't exist.",
			# 		"none": f"Summoner {summoner} hasn't played a match in a while!"
			# 	}
			# 	if isinstance(response, str):
			# 		await message.channel.send(codes[response])
			# 	else:
			# 		await message.channel.send(f"{response['name']}'s last match was {response['time']} ago.")
			# 	return True
			
			# if c.startswith("lolroler"):
			# 	summoner = c[8:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = riotapi.getRolePlayDataEmbed(summoner, ranked=True)
			# 	codes = {
			# 		"key": "Key expired.",
			# 		"sum": f"Summoner {summoner} doesn't exist."
			# 	}
			# 	if isinstance(response, str):
			# 		await message.channel.send(codes[response])
			# 	else:
			# 		await message.channel.send(embed=response)
			# 	return True
			
			# if c.startswith("lolrole"):
			# 	summoner = c[7:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = riotapi.getRolePlayDataEmbed(summoner)
			# 	codes = {
			# 		"key": "Key expired.",
			# 		"sum": f"Summoner {summoner} doesn't exist."
			# 	}
			# 	if isinstance(response, str):
			# 		await message.channel.send(codes[response])
			# 	else:
			# 		await message.channel.send(embed=response)
			# 	return True
			
			# if c.startswith("lolwrr"):
			# 	summoner = c[6:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = await riotapi.parseWinLossTrend(summoner, message, ranked=True)
			# 	codes = {
			# 		"sum": f"Summoner {summoner} doesn't exist."
			# 	}
			# 	# if isinstance(response, str):
			# 	if response in codes:
			# 		await message.channel.send(codes[response])
			# 	return True

			# if c.startswith("lolwr"):
			# 	summoner = c[5:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = await riotapi.parseWinLossTrend(summoner, message)
			# 	codes = {
			# 		"sum": f"Summoner {summoner} doesn't exist."
			# 	}
			# 	# if isinstance(response, str):
			# 	if response in codes:
			# 		await message.channel.send(codes[response])
			# 	return True

			# if c.startswith("lmr"):
			# 	summoner = c[3:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = await riotapi.getLiveMatchEmbed(summoner, message, hasRanked=True)
			# 	return True	
			
			# if c.startswith("lm"):
			# 	summoner = c[2:].strip()
			# 	if summoner == "":
			# 		summoner = riotapi.isUserRegistered(message.author.id)
			# 		if summoner == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
			# 			return True
			# 	response = await riotapi.getLiveMatchEmbed(summoner, message)
			# 	return True



	#LEAVE THIS AT THE END
	await bot.process_commands(message)
	return True

# Helper Functions

def getMemberList(guildID):
	targetGuild = bot.get_guild(guildID)
	memberList = []
	for member in targetGuild.members:
		memberList.append(member)
	return memberList

# *Commands*
# Testing is required across every single command to ensure no functionality is lost.
# Once a command is fully tested and checked, make sure to delete the commented "message catch"
# in on_message. A command can still be in a WIP state to delete the main command.

# Also, make sure the rewrite branch clearly breaks off the main branch. If it fails catastrophically,
# a good backup is required, with the consequences being a huge rollback or rewrite.

# The end goal of this expansion is to merge into main. Keep your code clean.


# Owner Commands

#TODO: bot.get_channel returns None?
#disabled for now
@bot.command(disabled=True)
@commands.is_owner()
async def link(message, channelID):
	try:
		channel = bot.get_channel(channelID)
	except:
		return False
	print("Link successful.")
	await sob.pipeline(channel)
	print("Link ended.")
	return True

@bot.command(name="ekoroshia", aliases=["ikoroshia"])
@commands.is_owner()
async def endProcess(message):
	await message.channel.send("To turn off Sobbot, type CONFIRM. (10s)")
	def check(msg):
		return msg.author == message.author
	try:
		confirmMessage = await bot.wait_for(event="message", timeout=10, check=check)
		if confirmMessage.content.strip() == "CONFIRM":
			await message.channel.send("Goodbye for now! :pleading_face::blue_heart:")
			sys.exit("Kill command invoked by owner.")
	except asyncio.TimeoutError:
		await message.channel.send("Still running. :grin:")
		return False
	await message.channel.send("Still running. :grin:")
	return False


# Help Commands


#TODO: use discord-pretty-help to make a real HelpCommand

@bot.command()
async def help(message, topic=None):
	if topic == None:
		await message.channel.send(embed=helpDir.getMainHelpDirectory(message))
	else: 
		embed = helpDir.getHelpDirectoryEmbed(message, topic)
		await message.channel.send(embed=embed)
	return True

@bot.command()
async def info(message, topic=None):
	if topic == None:
		await message.channel.send(embed=helpDir.getSingleList(message))
	else:
		await message.channel.send(embed=helpDir.getHelpSingle(message, topic))
	return True

@bot.command()
async def about(message):
	await message.channel.send("https://github.com/lucs100/sobbot")
	return True


# Admin Commands


#TODO: this is broken? command protocol makes prefixes messy
# disabled for now
#TODO: use the check feature
@bot.command(disable=True)
@commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild = True))
async def prefix(message, newPrefix):
	id = message.guild.id
	if newPrefix == "" or newPrefix == None:
		ok = admin.resetGuildPrefix(id)
		if ok == "ok":
			await message.channel.send(f"Prefix reset to `{admin.getGuildPrefix(id)}`!")
		elif ok == "nop":
			await message.channel.send(f"This server is already using the default prefix (`{admin.getGuildPrefix(id)}`)!")
		elif ok == "error":
			await message.channel.send("Something went wrong.")
		return True
	ok = admin.updateGuildPrefix(id, newPrefix)
	if ok:
		if newPrefix == admin.getGuildPrefix(id):
			await message.channel.send(f"Server prefix is now `{newPrefix}`!")
			return True
	await message.channel.send(f"Something went wrong. Server prefix unchanged.")
	return True


# Miscellaneous Commands

@bot.command()
async def ping(message):
	await message.channel.send("pong! ({0}ms)".format(int(bot.latency*1000)))
	return True

@bot.command()
async def uptime(message):
	await message.send(sob.timeRunning(startTime))
	return True

@bot.command()
async def flipcoin(message):
	await message.channel.send(sob.flipCoin())
	return True

#TODO: name = "d", space optional? requires testing
#TODO: no output?
@bot.command(name="d")
async def die(message, n):
	try:
		await message.channel.send(sob.die(n))
	except: #TODO: what exception type is this?
		pass
	return True

#TODO: no image files, test at home
@bot.command()
async def sobbleimage(message):
	await message.channel.send(file = sob.sobbleImage())
	return True

@bot.command()
async def math(message, *, query):
	result = sob.parseMath(query)
	if result != None:
		await message.channel.send(result)
	return True

@bot.command()
async def pkmn(message, *, query):
	try:
		query = int(query)
	except ValueError:
		pass
	finally:
		embed = sob.pkmnLookup(query)
		if embed != None:
			#TODO: does this need to relookup?
			await message.channel.send(embed = sob.pkmnLookup(query))
	return True

@bot.command()
async def starttime(message):
	startingTime = datetime.fromtimestamp(startTime).strftime("%B %d at %I:%M %p")
	await message.channel.send(f"Sobbot has been online since {startingTime}!")
	return True
	#TODO: maybe format this a little nicer?

#TODO: can maybe reorganize col command names since we're on command system? still need to learn
#TODO: maybe make the colour embed, file a class? idk
@bot.command(aliases=["randbluw", "randomblue", "randombluw"])
async def randblue(message):
	embed, file = (sob.randomBlue())
	await message.channel.send(embed=embed, file=file)
	return True

@bot.command(aliases=["randcolor", "randomcolour", "randomcolor"])
async def randcolour(message):
	embed, file = (sob.randomColor())
	await message.channel.send(embed=embed, file=file)
	return True

@bot.command(aliases=["viewcolor"])
async def viewcolour(message, colourCode):
	embed, file = sob.colorPreview(colourCode)
	await message.channel.send(embed=embed, file=file)

#TODO: is this the right way to pass a constant? can likely be rewritten if so
@bot.command()
async def scramble(message, length=25):
	try:
		count = int(length)
		scramble = sob.cubeScramble(length)
	except: #TODO: is this except correct? which exception type?
		scramble = sob.cubeScramble()
	await message.channel.send(scramble)
	return True


# LoL Commands
#TODO: raise errors on riotapi side (lots more)
#TODO: move to matchhistory api v5

def handleRegisteredSummoner(message, query):
	if query == None:
		query = riotapi.isUserRegistered(message.author.id) #bool or sname
		if query == False:
			raise riotapi.SummonerNotRegisteredError
	return query

@bot.command()
async def lollevel(message, *, query=None):
	name = handleRegisteredSummoner(message, query)
	data = riotapi.getSummonerData(name)
	if data == False:
		raise riotapi.KeyExpiredError
	elif data == None:
		raise riotapi.SummonerNotFoundError(query)
	else:
		await message.channel.send(f"Summoner **{data.name}** is level **{data.level}**.")
		return True

@bot.command()
async def lolmastery(message, *, query=None):
	try:
		name = handleRegisteredSummoner(message, query)
		embed = riotapi.embedTopMasteries(name)
		if embed == False:
			raise riotapi.KeyExpiredError
		await message.channel.send(embed=embed)
		return True
	except TypeError:
		raise riotapi.SummonerNotFoundError

@bot.command()
async def lolregister(message, *, name=None):
	id = message.author.id
	if name == None:
		await message.channel.send("Enter your summoner name to register it to your account!")
		return True
	if not riotapi.isUserRegistered(id):
		ok = riotapi.addRegistration(id, name)
	else:
		ok = riotapi.editRegistration(id, name)
	if ok != False:
		await message.channel.send(f"Set <@!{id}>'s summoner name to **{ok}**!")
		return True
	else:
		raise riotapi.SummonerNotFoundError

@bot.command()
#TODO: test ur
async def lolrank(message, *, name=None):
	name = handleRegisteredSummoner(message, name)
	embed = riotapi.embedRankedData(name)
	if isinstance(embed, int):
		if embed == 1:
			raise riotapi.KeyExpiredError
		elif embed == 2:
			raise riotapi.SummonerNotFoundError(name)
	else:
		await message.channel.send(embed=embed)
		return True

@bot.command()
#TODO: test ur
#TODO: MATCH HISTORY V4 :(
async def lastmatch(message, *, summoner=None):
	raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = riotapi.timeSinceLastMatch(summoner, False)
	codes = {
		"key": "Key expired.",
		"sum": f"Summoner {summoner} doesn't exist.",
		"none": f"Summoner {summoner} hasn't played a match in a while!"
	}
	if isinstance(response, str):
		await message.channel.send(codes[response])
	else:
		await message.channel.send(f"{response['name']}'s last match was {response['time']} ago.")
	return True

@bot.command(aliases = ["lastmatchr"])
#TODO: test ur
#TODO: MATCH HISTORY V4 :(
async def lastmatchranked(message, *, summoner=None):
	raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = riotapi.timeSinceLastMatch(summoner, True)
	codes = {
		"key": "Key expired.",
		"sum": f"Summoner {summoner} doesn't exist.",
		"none": f"Summoner {summoner} hasn't played a ranked match in a while!"
	}
	if isinstance(response, str):
		await message.channel.send(codes[response])
	else:
		await message.channel.send(f"{response['name']}'s last ranked match was {response['time']} ago.")
	return True

@bot.command(aliases = ["lolr"])
#TODO: test ur
#TODO: MATCH HISTORY V4 :(
async def lolrole(message, *, summoner=None):
	raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = riotapi.getRolePlayDataEmbed(summoner, ranked=False)
	codes = {
		"key": "Key expired.",
		"sum": f"Summoner {summoner} doesn't exist."
	}
	if isinstance(response, str):
		await message.channel.send(codes[response])
	else:
		await message.channel.send(embed=response)
	return True

@bot.command(aliases = ["lolrr", "lolroler"])
#TODO: test ur
#TODO: MATCH HISTORY V4 :(
async def lolroleranked(message, *, summoner=None):
	raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = riotapi.getRolePlayDataEmbed(summoner, ranked=True)
	codes = {
		"key": "Key expired.",
		"sum": f"Summoner {summoner} doesn't exist."
	}
	if isinstance(response, str):
		await message.channel.send(codes[response])
	else:
		await message.channel.send(embed=response)
	return True

@bot.command(aliases = ["lolwr"])
#TODO: test ur
#TODO: MATCH HISTORY V4 :(
async def lolwinrate(message, *, summoner=None):
	raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = await riotapi.parseWinLossTrend(summoner, message, ranked=False)
	codes = {
		"sum": f"Summoner {summoner} doesn't exist."
	}
	if response in codes:
		await message.channel.send(codes[response])
	return True

@bot.command(aliases = ["lolwrr"])
#TODO: test ur
#TODO: MATCH HISTORY V4 :(
async def lolwinrateranked(message, *, summoner=None):
	raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = await riotapi.parseWinLossTrend(summoner, message, ranked=True)
	codes = {
		"sum": f"Summoner {summoner} doesn't exist."
	}
	if response in codes:
		await message.channel.send(codes[response])
	return True

@bot.command(aliases = ["lm"])
#TODO: test ur
#TODO: why Summoner Not Found?
async def livematch(message, *, summoner=None):
	#raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = await riotapi.getLiveMatchEmbed(summoner, message, hasRanked=False)
	return True

@bot.command(aliases = ["lmr"])
#TODO: test ur
async def livematchranked(message, *, summoner=None):
	#raise riotapi.MatchHistoryOutdatedWarning
	summoner = handleRegisteredSummoner(message, summoner)
	response = await riotapi.getLiveMatchEmbed(summoner, message, hasRanked=True)
	return True

@bot.command(aliases = ["lwk"])
async def lolwiki(message, *, query):
	link = (riotapi.getWikiLink(query))
	if link != None:
		await message.channel.send(link)
	return True

@bot.command()
#TODO: make embed
async def lollobby(message, *, chat):
	embed = riotapi.lobbyRankedReport(chat)
	if embed != None:
		await message.channel.send(embed=embed)
	return True


# Currency Commands
#TODO: these commands suck 
#TODO: rewrite all currency commands to use user objects rather than ids
#TODO: these really shouldnt @ that often

@bot.command()
async def coinstart(message):
	ok = coin.addRegistration(message.author.id)
	if ok:
		await message.channel.send(f"<@!{message.author.id}> added to soblecoin! You have {coin.getUserCoins(message.author.id)} coins.")
		return True
	await message.channel.send(f"<@!{message.author.id}> , you already have soblecoins! You have {coin.startingCoins} coins.")
	return False

#TODO: dont @ recipient wtf??? get the user object
@bot.command()
async def give(message, recipient, value):
	try:
		sender = message.author.id
		recipient = recipient[3:-1]
		value = int(value)
		ok = coin.give(sender, recipient, value)
		responses = {
			#indexed by error code
			0: f"Sent **{value}** soblecoins to <@!{recipient}>!",
			2: f"Soblecoins not sent! You don't have enough soblecoins.",
			4: f"You can't send coins to yourself!"
		}
		if ok in responses:
			await message.channel.send(responses[ok])
	except ValueError:
		await message.channel.send("Use `give` (recipient) (value) to send a friend soblecoins!")
	return True

@bot.command()
async def balance(message):
	value = coin.getUserCoins(message.author.id)
	if isinstance(value, int):
		await message.channel.send(f"<@!{message.author.id}>, you have **{value}** soblecoins!")
	else:
		raise coin.CoinNotRegisteredError

#TODO: maybe give better name/alias?
#TODO: no "reg" warning
@bot.command()
async def claim(message):
	ok, value = coin.claimHourly(message.author.id)
	if isinstance(ok, str):
		if ok == "reg":
			raise coin.CoinNotRegisteredError
	if ok:
		if value == 1000:
			await message.channel.send(f"<@!{message.author.id}>, your balance was topped up to **{value}** soblecoins!")
		else:
			await message.channel.send(f"<@!{message.author.id}> claimed **{value}** soblecoins!")
	else:
		await message.channel.send(f"<@!{message.author.id}>, your next gift isn't ready yet! Try again {value}.")
	return True

@bot.command()
async def roll(message, value):
	status, change, multi = coin.luckyRoll(message.author.id, value)
	codes = {
		"int": f"<@!{message.author.id}>, you can only wager a whole number of soblecoins!",
		"insuff": f"<@!{message.author.id}>, you only have {change} soblecoins!"
	}
	if status in codes:
		await message.channel.send(codes[status])
	else:
		if multi > 1:
			await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi} and won {change} soblecoins!")
		if multi == 1:
			await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! You didn't win or lose soblecoins.")
		if multi < 1:
			await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! Sorry, you lost {change} soblecoins :frowning:")
	return True

@bot.command()
async def shop(message):
	await message.channel.send(embed = coin.getShop(message))
	return True

@bot.command()
async def buy(message, selectionID):
	code, num = coin.buyFromShop(selectionID, message.author.id)
	messages = {
		"exist": f"<@!{message.author.id}>, no item with the ID {selectionID} exists!",
		"broke": f"<@!{message.author.id}>, you only have {num} soblecoins!",
		"limit": f"<@!{message.author.id}>, you already own that limited item.",
		"prereq": f"<@!{message.author.id}>, you need a prerequisite item in order to buy that."
	}
	if code in messages:
		await message.channel.send(messages[code])
	else:
		await message.channel.send(f"<@!{message.author.id}>, you purchased a **{code}**! You now own {num}.")
	return True

@bot.command()
async def inventory(message):
	await message.channel.send(coin.getInventoryEmbed(message.author.id))
	return True


# Finance Functions
# TODO: these as a whole are so sluggish

@bot.command()
async def ticker(message, symbol):
	embed = finance.createStockEmbed(symbol)
	if embed != None:
		await message.channel.send(embed=embed)
	else:
		await message.channel.send(f"Symbol {symbol.upper()} doesn't seem to exist.")
	return True

@bot.command(aliases=["portfoliostart"])
async def pfstart(message):
	ok = finance.createPortfolio(message.author.id)
	if ok:
		await message.channel.send("Portfolio created successfully!")
	else:
		await message.channel.send("Portfolio already exists! Use `resetportfolio` (coming soon) to reset your portfolio.")
	return True

@bot.command(aliases=["portfolioshow", "showportfolio", "showpf"])
async def pfshow(message):
	data = await finance.getUserPortfolioEmbed(message)
	codes = {
		"reg": f"<@!{message.author.id}>, you don't have a portfolio! Use `pfstart` to open one.",
		"empty": f"<@!{message.author.id}>, your portfolio is empty!"
	}
	if data in codes:
		await message.channel.send(codes[data])
	return True

#TODO: can commands be in any order since they're strictly typed?
@bot.command(aliases=["portfolioadd"])
async def pfadd(message, symbol, count):
	id = message.author.id
	count = int(count) #locked to int for now
	if not (isinstance(symbol, str) and ((isinstance(count, int) or isinstance(count, float)))):
		return True # type error
	status = finance.updatePortfolio(symbol, id, count)
	codes = {
		"reg": f"<@!{message.author.id}>, you don't have a portfolio! Use `pfstart` to open one.",
		"sym": f"{symbol.upper()} isn't a valid symbol!",
		"neg": "You can't have negative shares!",
		"delS": f"Symbol {symbol.upper()} removed successfully!",
		"delF": f"You didn't have any shares of {symbol.upper()}, so nothing was changed.",
		"ok": f"Your portfolio now has **{count}** share of {symbol.upper()}!",
		"ok2": f"Your portfolio now has **{count}** shares of {symbol.upper()}!"
	}
	await message.channel.send(codes[status])
	return True


# Spotify Functions
# note: if non-server playlists are ever added, need to realias.


@bot.command(aliases=["playlistcreate"])
async def spcreate(message):
	await sp.createGuildPlaylistGuildSide(message)
	return True

@bot.command(aliases=["playlistadd"])
async def spadd(message, *, song):
	await sp.addToGuildPlaylistGuildSide(message, song)
	return True

@bot.command(aliases=["playlistoverview"])
async def spoverview(message):
	members = getMemberList(message.guild.id)
	await sp.fetchGuildPlaylistOverviewGuildSide(message, members)
	return True

@bot.command(aliases=["playlistlink"])
async def splink(message):
	try:
		link = sp.getGuildPlaylist(message.guild.id).link
		await message.channel.send(link)
	except AttributeError:
		raise sp.NoGuildPlaylistError
	return True

@bot.command(aliases=["playlistsettitle", "setplaylisttitle"])
@commands.check(commands.has_permissions(manage_guild = True))
async def spsettitle(context, *, title):
	response = await sp.setGuildPlaylistTitleGuildSide(context, title)
	if response:
		await context.message.add_reaction("👍")
		return True
	else:
		await context.message.add_reaction("👎")
		return False

@bot.command(aliases=["playlistsetdesc", "setplaylistdesc"])
@commands.check(commands.has_permissions(manage_guild = True))
async def spsetdesc(context, *, desc):
	response = await sp.setGuildPlaylistDescGuildSide(context, desc)
	if response:
		await context.message.add_reaction("👍")
		return True
	else:
		await context.message.add_reaction("👎")
		return False

#TODO: can multimessage handling be done better? :(
@bot.command(aliases=["playlistclear"])
@commands.check(commands.has_permissions(manage_guild = True))
async def spclear(message):
	target = sp.getGuildPlaylist(message.guild.id)
	if target == None:
		raise sp.NoGuildPlaylistError
	else:
		await message.channel.send("Are you sure? Type CONFIRM. (15s)")
		def check(msg):
			return msg.author == message.author
		try:
			confirmMessage = await bot.wait_for(event="message", timeout=15, check=check)
			if confirmMessage.content.strip() == "CONFIRM":
				target.delete(isConfirmed=True)
				await message.channel.send("Deleted. :sob:")
				return True
		except asyncio.TimeoutError:
			await message.channel.send("Not deleted. :grin:")
			return False
		await message.channel.send("Cancelled. :grin:")
		return False

@bot.command(aliases=["playlistsetimage", "playlistsetcover", "spsetcover"])
async def spsetimage(context):
	try:
		newImg = context.message.attachments[0]
	except IndexError:
		await context.channel.send("Send an image with that command.")
		return False
	gph = sp.getGuildPlaylist(context.guild.id)
	if gph != None:
		response = await sp.encodeAndSetCoverImage(newImg, gph)
		if response:
			await context.message.add_reaction("👍")
			return True
		else:
			await context.message.add_reaction("👎")
			return False
	else:
		raise sp.NoGuildPlaylistError

@bot.command(aliases=["spdeletenewest", "playlistdeletenewest"])
async def spdelnewest(context):
	gph = sp.getGuildPlaylist(context.guild.id)
	if gph != None:
		response = await sp.undoAdditionGuildSide(context, gph)
		if response == True:
			await context.message.add_reaction("👍")
			return True
		else:
			await context.message.add_reaction("👎")
			if response == "empty":
				await context.channel.send("The playlist is already empty.")
			return False
	else:
		raise sp.NoGuildPlaylistError

@bot.command(aliases=["playlistdelete", "playlistremove", "spremove"])
@commands.check(commands.has_permissions(manage_guild = True))
async def spdelete(context, *, song):
	gph = sp.getGuildPlaylist(context.guild.id)
	if gph != None:
		response = await sp.deleteSongGuildSide(context, gph, song)
		if response == True:
			await context.message.add_reaction("👍")
			return True
		else:
			await context.message.add_reaction("👎")
			if response == "notin":
				await context.channel.send(
					"That song doesn't seem to " +
					"be in your server's playlist.")
			return False
	else:
		raise sp.NoGuildPlaylistError


# Error Handling


@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.NotOwner):
		await ctx.send("Only the bot owner can do that!")
	if isinstance(error, commands.CheckAnyFailure): # vague avoid if possible
		await ctx.send("You don't have permission to do that.")
	if isinstance(error, coin.CoinNotRegisteredError):
		await ctx.send(f"<@!{ctx.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.")
	if isinstance(error, coin.CoinRecipientNotRegisteredError):
		await ctx.send(f"That user doesn't have soblecoins enabled, or doesn't exist.")
	if isinstance(error, sp.NoGuildPlaylistError):
		await ctx.send("This server doesn't have a server playlist yet!\n" + 
            f"Use `{admin.getGuildPrefix(ctx.guild.id)}spcreate` to make one.")
	if isinstance(error, riotapi.SummonerNotRegisteredError):
		await ctx.send(f"<@!{ctx.author.id}>, you aren't registered! Use `lolregister` to add your summoner name.\n"+
						"You can also specify a summoner name after this command to use it while unregistered.")
	if isinstance(error, riotapi.SummonerNotFoundError):
		await ctx.send(f"{error.name} could not be found.")
	if isinstance(error, riotapi.MatchHistoryOutdatedWarning):
		await ctx.send(f"Command is currently disabled. Use `{admin.getGuildPrefix(ctx.guild.id)}info mh` for more info.")

		

	return True


bot.run(DISCORDTOKEN)