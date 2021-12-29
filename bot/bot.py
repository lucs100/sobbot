import os, discord, time, asyncio, sys

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

bot = commands.Bot(command_prefix = "s!", intents=intents)

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
		c = (message.content).lower() #change to cl? idk this might suck later
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
			
		if c == "ping":
			await message.channel.send("pong! ({0}ms)".format(int(bot.latency*1000)))
			return True
		
		if match("<@!?835251884104482907>", c) is not None: #"@sobbot"
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

		#TODO: retire this.
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
			
			# if c == "ekoroshia" or c == "ikoroshia":
			# 	if userIsBotOwner(message.author):
			# 		await message.channel.send("To turn off Sobbot, type CONFIRM. (10s)")
			# 		def check(msg):
			# 			return msg.author == message.author
			# 		try:
			# 			confirmMessage = await bot.wait_for(event="message", timeout=10, check=check)
			# 			if confirmMessage.content.strip() == "CONFIRM":
			# 				await message.channel.send("Goodbye for now! :pleading_face::blue_heart:")
			# 				sys.exit("Kill command invoked by owner.")
			# 		except asyncio.TimeoutError:
			# 			await message.channel.send("Still running. :grin:")
			# 			return False
			# 		await message.channel.send("Still running. :grin:")
			# 		return False
			# 	else:
			# 		await reportNotOwner(message)
			# 		return False


			# Help Functions

			# if c == "help":
			# 	await message.channel.send(embed=helpDir.getMainHelpDirectory(message))
			# 	return True

			# if c.startswith("help") and (c != "help"):
			# 	topic = c[4:].strip()
			# 	embed = helpDir.getHelpDirectoryEmbed(message, topic)
			# 	await message.channel.send(embed=embed)
			# 	return True
			
			# if c.startswith("info"):
			# 	topic = c[4:].strip()
			# 	await message.channel.send(embed=helpDir.getHelpSingle(message, topic))
			# 	return True
			
			# if c == "about":
			# 	await message.channel.send("https://github.com/lucs100/sobbot")
			# 	return True

			
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


			# Miscellaneous Functions


			# if c == "flipcoin":
			# 	await message.channel.send(sob.flipCoin())
			# 	return True

			# if c.startswith('d'):
			# 	try:
			# 		n = (int(c[1:]))
			# 		await message.channel.send(sob.die(n))
			# 	except:
			# 		pass
			# 	return True

			# if c == "sobbleimage":
			# 	await message.channel.send(file = sob.sobbleImage())
			# 	return True

			# if c.startswith("math"):
			# 	content = sob.parseMath(c[4:].strip())
			# 	await message.channel.send(content)
			# 	return True
			
			# if c.startswith("pkmn"):
			# 	data = c[4:].strip()      #query
			# 	try:
			# 		data = int(data)      #rehashes as int if possible
			# 	except ValueError:
			# 		pass
			# 	finally:
			# 		embed = sob.pkmnLookup(data)
			# 		if embed != None: 	  #result found
			# 			await message.channel.send(embed=sob.pkmnLookup(data))
			# 	return True

			# if c == "starttime":
			# 	startingTime = datetime.fromtimestamp(startTime).strftime("%B %d at %I:%M %p")
			# 	await message.channel.send(f"Sobbot has been online since {startingTime}!")
			# 	return True
			# 	#TODO: maybe format this a little nicer?
			
			# if c == "randblue" or c == "randbluw":
			# 	embed, file = (sob.randomBlue())
			# 	await message.channel.send(embed=embed, file=file)
			# 	return True
			
			# if c == "randcolour" or c == "randcolor":
			# 	embed, file = (sob.randomColor())
			# 	await message.channel.send(embed=embed, file=file)
			# 	return True
			
			# if c.startswith("viewcolour"):
			# 	c = c[10:].strip()
			# 	embed, file = sob.colorPreview(c)
			# 	await message.channel.send(embed=embed, file=file)
			# elif c.startswith("viewcolor"):
			# 	c = c[9:].strip()
			# 	embed, file = sob.colorPreview(c)
			# 	await message.channel.send(embed=embed, file=file)
			
			# if c.startswith("scramble"):
			# 	count = c[8:].strip() # length if specified
			# 	print(count)
			# 	try:
			# 		count = int(count)
			# 		scramble = sob.cubeScramble(count)
			# 	except:
			# 		scramble = sob.cubeScramble()
			# 	await message.channel.send(scramble)
			# 	return True
			

			

			# LoL Functions
			

			if c.startswith("lollevel"):
				try:
					name = c[8:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or sname
						if name == False:
							await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
							return True
					data = riotapi.getSummonerData(name)
					if data == False:
						await message.channel.send("Key expired.")
						return True
					await message.channel.send(f"Summoner **{data.name}** is level **{data.level}**.")
				except:
					await message.channel.send(f"Summoner **{data.name}** doesn't exist.")
					return True

			if c.startswith("lolmastery"):
				try:
					name = c[10:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or summoner name
						if name == False:
							await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
							return True
					embed = riotapi.embedTopMasteries(name)
					if embed == False:
						await message.channel.send("Key expired.")
						return True
					await message.channel.send(embed=embed)
				except: # bad!!!!
					await message.channel.send(f"Summoner **{name}** doesn't exist, or your key expired. Try again!")
				return True
			
			if c.startswith("lolregister"):
				# name = message.content[13:].strip()
				name = c[11:].strip()
				id = message.author.id
				if name == "":
					await message.channel.send("Enter your summoner name to register it to your account!")
					return True
				if not riotapi.isUserRegistered(id):
					ok = riotapi.addRegistration(id, name)
				else:
					ok = riotapi.editRegistration(id, name)
				if ok != False:
					await message.channel.send(f"Set <@!{id}>'s summoner name to **{ok}**!")
				else:
					await message.channel.send(f"Summoner **{name}** doesn't exist, or your key expired. Try again!")
				return True

			if c.startswith("lolrank"):
				try:
					name = c[7:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or sname
						if name == False:
							await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
							return True
					embed = riotapi.embedRankedData(name)
					if isinstance(embed, int):
						if embed == 1:
							await message.channel.send("Key expired.")
							return True
						elif embed == 2:
							await message.channel.send(f"Summoner **{name}** doesn't exist.")
							return True
					await message.channel.send(embed=embed)
				except:
					pass
				return True

			# if c == "lolapireload":
			# 	if message.author.id == 312012475761688578:
			# 		if await riotapi.updateAPIKey():
			# 			await message.channel.send("Successfully set key!")
			# 		else:
			# 			await message.channel.send("Key update failed.")
			# 	else:
			# 		await message.channel.send("You don't have the permissions to do this.")
			
			if c.startswith("lastmatchr"):
				summoner = c[10:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
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

			if c.startswith("lastmatch"):
				summoner = c[9:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
				response = riotapi.timeSinceLastMatch(summoner)
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
			
			if c.startswith("lolroler"):
				summoner = c[8:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
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
			
			if c.startswith("lolrole"):
				summoner = c[7:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
				response = riotapi.getRolePlayDataEmbed(summoner)
				codes = {
					"key": "Key expired.",
					"sum": f"Summoner {summoner} doesn't exist."
				}
				if isinstance(response, str):
					await message.channel.send(codes[response])
				else:
					await message.channel.send(embed=response)
				return True
			
			if c.startswith("lolwrr"):
				summoner = c[6:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
				response = await riotapi.parseWinLossTrend(summoner, message, ranked=True)
				codes = {
					"sum": f"Summoner {summoner} doesn't exist."
				}
				# if isinstance(response, str):
				if response in codes:
					await message.channel.send(codes[response])
				return True

			if c.startswith("lolwr"):
				summoner = c[5:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
				response = await riotapi.parseWinLossTrend(summoner, message)
				codes = {
					"sum": f"Summoner {summoner} doesn't exist."
				}
				# if isinstance(response, str):
				if response in codes:
					await message.channel.send(codes[response])
				return True

			if c.startswith("lmr"):
				summoner = c[3:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
				response = await riotapi.getLiveMatchEmbed(summoner, message, hasRanked=True)
				return True	
			
			if c.startswith("lm"):
				summoner = c[2:].strip()
				if summoner == "":
					summoner = riotapi.isUserRegistered(message.author.id)
					if summoner == False:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `lolregister` to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
						return True
				response = await riotapi.getLiveMatchEmbed(summoner, message)
				return True

			if c.startswith("lwk"):
				c = c[3:].strip()
				link = (riotapi.getWikiLink(c))
				if link != None:
					await message.channel.send(link)
				return True
			
			if c.startswith("lollobby"):
				c = c[8:].strip()
				embed = riotapi.lobbyRankedReport(c) #make embed later
				if embed != None:
					await message.channel.send(embed=embed)
				return True


			# Currency Functions


			# if c == "coinstart":
			# 	ok = coin.addRegistration(message.author.id)
			# 	if ok:
			# 		await message.channel.send(f"<@!{message.author.id}> added to soblecoin! You have {coin.getUserCoins(message.author.id)} coins.")
			# 		return True
			# 	await message.channel.send(f"<@!{message.author.id}> , you already have soblecoins! You have {coin.startingCoins} coins.")
			# 	return False
			
			# if c.startswith("give"):
			# 	try:
			# 		sender = message.author.id
			# 		recipient, value = c[4:].split()
			# 		recipient = recipient[3:-1]
			# 		value = int(value)
			# 		ok = coin.give(sender, recipient, value)
			# 		messages = {
			# 			#indexed by error code
			# 			0: f"Sent **{value}** soblecoins to <@!{recipient}>!",
			# 			1: f"<@!{recipient}> doesn't have soblecoins enabled, or doesn't exist.",
			# 			2: f"Soblecoins not sent! You don't have enough soblecoins.",
			# 			3: f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.",
			# 			4: f"You can't send coins to yourself!"
			# 		}
			# 		if ok in messages:
			# 			await message.channel.send(messages[ok])
			# 	except:
			# 		await message.channel.send("Use `give` (recipient) (value) to send a friend soblecoins!")
			# 	return True
			
			# if c == "balance":
			# 	value = coin.getUserCoins(message.author.id)
			# 	if isinstance(value, bool):
			# 		if value == False:
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.")
			# 			return True
			# 	await message.channel.send(f"<@!{message.author.id}>, you have **{value}** soblecoins!")
			
			# if c == "claim":
			# 	ok, value = coin.claimHourly(message.author.id)
			# 	if isinstance(ok, str):
			# 		if ok == "reg":
			# 			await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.")
			# 	if ok:
			# 		if value == 1000:
			# 			await message.channel.send(f"<@!{message.author.id}>, your balance was topped up to **{value}** soblecoins!")
			# 		else:
			# 			await message.channel.send(f"<@!{message.author.id}> claimed **{value}** soblecoins!")
			# 	else:
			# 		await message.channel.send(f"<@!{message.author.id}>, your next gift isn't ready yet! Try again {value}.")
			# 	return True

			# if c.startswith("roll"):
			# 	value = c[4:].strip()
			# 	status, change, multi = coin.luckyRoll(message.author.id, value)
			# 	codes = {
			# 		"int": f"<@!{message.author.id}>, you can only wager a whole number of soblecoins!",
			# 		"reg": f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.",
			# 		"insuff": f"<@!{message.author.id}>, you only have {change} soblecoins!"
			# 	}
			# 	if status in codes:
			# 		await message.channel.send(codes[status])
			# 	else:
			# 		if multi > 1:
			# 			await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi} and won {change} soblecoins!")
			# 		if multi == 1:
			# 			await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! You didn't win or lose soblecoins.")
			# 		if multi < 1:
			# 			await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! Sorry, you lost {change} soblecoins :frowning:")
			# 	return True
			
			# if c == "shop":
			# 	await message.channel.send(embed = coin.getShop(message))
			# 	return True
			
			# if c.startswith("buy"):
			# 	c = c[3:].strip()
			# 	code, num = coin.buyFromShop(c, message.author.id)
			# 	messages = {
			# 		"exist": f"<@!{message.author.id}>, no item with the ID {c} exists!",
			# 		"reg": f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.",
			# 		"broke": f"<@!{message.author.id}>, you only have {num} soblecoins!",
			# 		"limit": f"<@!{message.author.id}>, you already own that limited item.",
			# 		"prereq": f"<@!{message.author.id}>, you need a prerequisite item in order to buy that."
			# 	}
			# 	if code in messages:
			# 		await message.channel.send(messages[code])
			# 	else:
			# 		await message.channel.send(f"<@!{message.author.id}>, you purchased a **{code}**! You now own {num}.")
			# 	return True

			# if c == "inventory":
			# 	await message.channel.send(coin.getInventoryEmbed(message.author.id))
			# 	return True
			

			# Finance Functions


			# if c.startswith("ticker"):
			# 	c = c[6:].strip()
			# 	embed = finance.createStockEmbed(c)
			# 	if embed != None:
			# 		await message.channel.send(embed=embed)
			# 	else:
			# 		await message.channel.send(f"Symbol {c.upper()} doesn't seem to exist.")
			# 	return True

			# if c == "pfstart":
			# 	ok = finance.createPortfolio(message.author.id)
			# 	if ok:
			# 		await message.channel.send("Portfolio created successfully!")
			# 	else:
			# 		await message.channel.send("Portfolio already exists! Use `resetportfolio` (coming soon) to reset your portfolio.")
			# 	return True
			
			# if c == "pfshow":
			# 	data = await finance.getUserPortfolioEmbed(message)
			# 	codes = {
			# 		"reg": f"<@!{message.author.id}>, you don't have a portfolio! Use `pfstart` to open one.",
			# 		"empty": f"<@!{message.author.id}>, your portfolio is empty!"
			# 	}
			# 	if data in codes:
			# 		await message.channel.send(codes[data])
			# 	return True

			# if c.startswith("pf"): # must after all portfolio functions!
			# 	#slow
			# 	id = message.author.id
			# 	symbol, count = c[2:].split()
			# 	count = int(count) # locked to int for now
			# 	if not (isinstance(symbol, str) and ((isinstance(count, int) or isinstance(count, float)))):
			# 		return True # type error
			# 	status = finance.updatePortfolio(symbol, id, count)
			# 	codes = {
			# 		"reg": f"<@!{message.author.id}>, you don't have a portfolio! Use `pfstart` to open one.",
			# 		"sym": f"{symbol.upper()} isn't a valid symbol!",
			# 		"neg": "You can't have negative shares!",
			# 		"delS": f"Symbol {symbol.upper()} removed successfully!",
			# 		"delF": f"You didn't have any shares of {symbol.upper()}, so nothing was changed.",
			# 		"ok": f"Your portfolio now has **{count}** share of {symbol.upper()}!",
			# 		"ok2": f"Your portfolio now has **{count}** shares of {symbol.upper()}!"
			# 	}
			# 	await message.channel.send(codes[status])
			# 	return True
			

			# Spotify Functions


			# if c == "spcreate":
			# 	await sp.createGuildPlaylistGuildSide(message)
			# 	return True
			
			# if c.startswith("spadd"):
			# 	c = c[5:].strip()
			# 	await sp.addToGuildPlaylistGuildSide(message, c)
			# 	return True
			
			# if c == "spoverview":
			# 	members = getMemberList(message.guild.id)
			# 	await sp.fetchGuildPlaylistOverviewGuildSide(message, members)
			# 	return True
			
			# if c == "splink":
			# 	link = sp.getGuildPlaylist(message.guild.id).link
			# 	await message.channel.send(link)
			# 	return True

			# if c.startswith("spsettitle"):
			# 	title = message.content[len(admin.getGuildPrefix(message.guild.id))+10:].strip()
			# 	perms = (message.author.guild_permissions.manage_guild)
			# 	response = await sp.setGuildPlaylistTitleGuildSide(message, title, perms)
			# 	if response:
			# 		await message.add_reaction("👍")
			# 		return True
			# 	else:
			# 		await message.add_reaction("👎")
			# 		return False

			# if c.startswith("spsetdesc"):
			# 	desc = message.content[len(admin.getGuildPrefix(message.guild.id))+9:].strip()
			# 	perms = (message.author.guild_permissions.manage_guild)
			# 	response = await sp.setGuildPlaylistDescGuildSide(message, desc, perms)
			# 	if response:
			# 		await message.add_reaction("👍")
			# 		return True
			# 	else:
			# 		await message.add_reaction("👎")
			# 		return False
			
			# if c == "spclear":
			# 	perms = (message.author.guild_permissions.manage_guild)
			# 	if not perms:
			# 		await message.channel.send("You'll need Manage Server perms to do that.")
			# 		return False
			# 	target = sp.getGuildPlaylist(message.guild.id)
			# 	if target == None:
			# 		await sp.reportNoGP(message)
			# 		return False
			# 	else:
			# 		await message.channel.send("Are you sure? Type CONFIRM. (15s)")
			# 		def check(msg):
			# 			return msg.author == message.author
			# 		try:
			# 			confirmMessage = await bot.wait_for(event="message", timeout=15, check=check)
			# 			if confirmMessage.content.strip() == "CONFIRM":
			# 				target.delete(isConfirmed=True)
			# 				await message.channel.send("Deleted. :sob:")
			# 				return True
			# 		except asyncio.TimeoutError:
			# 			await message.channel.send("Not deleted. :grin:")
			# 			return False
			# 		await message.channel.send("Cancelled. :grin:")
			# 		return False
			
			# if c == "spsetimage" or c == "spsetcover" or c == "spsetcoverimage":
			# 	try:
			# 		newImg = message.attachments[0]
			# 	except IndexError:
			# 		await message.channel.send("Send an image with that command.")
			# 		return False
			# 	gph = sp.getGuildPlaylist(message.guild.id)
			# 	if gph != None:
			# 		response = await sp.encodeAndSetCoverImage(newImg, gph)
			# 		if response:
			# 			await message.add_reaction("👍")
			# 			return True
			# 		else:
			# 			await message.add_reaction("👎")
			# 			return False
			# 	else:
			# 		await sp.reportNoGP(message)
			# 		return False
			
			# if c == "spdelnewest" or c == "spdeletenewest":
			# 	perms = (message.author.guild_permissions.manage_guild)
			# 	gph = sp.getGuildPlaylist(message.guild.id)
			# 	if gph != None:
			# 		response = await sp.undoAdditionGuildSide(message, gph, perms)
			# 		if response == True:
			# 			await message.add_reaction("👍")
			# 			return True
			# 		else:
			# 			await message.add_reaction("👎")
			# 			if response == "perm":
			# 				await message.channel.send("You don't have permission to do that.")
			# 			elif response == "empty":
			# 				await message.channel.send("The playlist is empty already.")
			# 			return False
			# 	else:
			# 		await sp.reportNoGP(message)
			# 		return False

			# if c.startswith("spdelete") or c.startswith("spremove"):
			# 	perms = (message.author.guild_permissions.manage_guild)
			# 	c = c[8:].strip()
			# 	gph = sp.getGuildPlaylist(message.guild.id)
			# 	if gph != None:
			# 		response = await sp.deleteSongGuildSide(message, gph, c, perms)
			# 		if response == True:
			# 			await message.add_reaction("👍")
			# 			return True
			# 		else:
			# 			await message.add_reaction("👎")
			# 			if response == "perm":
			# 				await message.channel.send("You don't have permission to do that.")
			# 			if response == "notin":
			# 				await message.channel.send(
			# 					"That song doesn't seem to " +
			# 					"be in your server's playlist.")
			# 			return False
			# 	else:
			# 		await sp.reportNoGP(message)
			# 		return False

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

#TODO: replace with builtin is_owner method 
def userIsBotOwner(user):
	return str(user.id) == str(botCreatorID)

async def reportNotOwner(message):
	await message.channel.send("Only the bot owner can do that!")


# *Commands*
# Testing is required across every single command to ensure no functionality is lost.
# Once a command is fully tested and checked, make sure to delete the commented "message catch"
# in on_message. A command can still be in a WIP state to delete the main command.

# Also, make sure the rewrite branch clearly breaks off the main branch. If it fails catastrophically,
# a good backup is required, with the consequences being a huge rollback or rewrite.

# The end goal of this expansion is to merge into main. Keep your code clean.


# Owner Commands


@bot.command()
async def link(message, channelID):
	if userIsBotOwner(message.author):
		try:
			channel = bot.get_channel(channelID)
		except:
			return False
		print("Link successful.")
		await sob.pipeline(channel)
		print("Link ended.")
		return True
	else:
		await reportNotOwner(message)
		return False

@bot.command(name="ekoroshia", aliases=["ikoroshia"])
async def endProcess(message):
	if userIsBotOwner(message.author):
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
	else:
		await reportNotOwner(message)
		return False


# Help Commands


@bot.command()
async def help(message):
	await message.channel.send(embed=helpDir.getMainHelpDirectory(message))
	return True

#TODO: this is kind of an overload? might need to change the command name, or merge with previous command
@bot.command()
async def helpPage(message, topic):
	embed = helpDir.getHelpDirectoryEmbed(message, topic)
	await message.channel.send(embed=embed)
	return True

@bot.command()
async def info(message, topic):
	await message.channel.send(embed=helpDir.getHelpSingle(message, topic))
	return True

@bot.command()
async def about(message):
	await message.channel.send("https://github.com/lucs100/sobbot")
	return True


# Admin Commands


#TODO: use the check feature
@bot.command()
async def prefix(message, newPrefix):
	if not (message.author.guild_permissions.manage_guild):
		await message.channel.send("You don't have permission to do that.")
		return False
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
async def uptime(message):
	await message.send(sob.timeRunning(startTime))
	return True

@bot.command()
async def flipcoin(message):
	await message.channel.send(sob.flipCoin())
	return True

#TODO: name = "d", space optional? requires testing
@bot.command(name="d")
async def die(message, n):
	try:
		await message.channel.send(sob.die(n))
	except: #TODO: what exception type is this?
		pass
	return True

@bot.command()
async def sobbleimage(message):
	await message.channel.send(file = sob.sobbleImage())
	return True

@bot.command()
async def math(message, query):
	#TODO: test if this should have a nonetype check (see automath)
	await message.channel.send(sob.parseMath(query))
	return True

@bot.command()
async def pkmn(message, query):
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

#TODO: can maybe reorganize col command names since we're on command system.
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
	except:
		scramble = sob.cubeScramble()
	await message.channel.send(scramble)
	return True


# LoL Commands
#TODO: absolutely need to look into how implicit params work before porting.

def dummy():
	pass


# Currency Commands
#TODO: these commands suck 
#TODO: rewrite all currency commands to use user objects rather than ids
#TODO: refactor no wallet message into function? 
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
			1: f"<@!{recipient}> doesn't have soblecoins enabled, or doesn't exist.",
			2: f"Soblecoins not sent! You don't have enough soblecoins.",
			3: f"<@!{message.author.nick}>, you aren't registered! Use `coinstart` to start using soblecoins.",
			4: f"You can't send coins to yourself!"
		}
		if ok in responses:
			await message.channel.send(responses[ok])
	except:
		await message.channel.send("Use `give` (recipient) (value) to send a friend soblecoins!")
	return True

@bot.command()
async def balance(message):
	value = coin.getUserCoins(message.author.id)
	if isinstance(value, bool):
		if value == False:
			await message.channel.send(f"<@!{message.author.nick}>, you aren't registered! Use `coinstart` to start using soblecoins.")
			return True
	await message.channel.send(f"<@!{message.author.nick}>, you have **{value}** soblecoins!")

#TODO: maybe give better name/alias?
@bot.command()
async def claim(message):
	ok, value = coin.claimHourly(message.author.id)
	if isinstance(ok, str):
		if ok == "reg":
			await message.channel.send(f"<@!{message.author.nick}>, you aren't registered! Use `coinstart` to start using soblecoins.")
			return False
	if ok:
		if value == 1000:
			await message.channel.send(f"<@!{message.author.nick}>, your balance was topped up to **{value}** soblecoins!")
		else:
			await message.channel.send(f"<@!{message.author.nick}> claimed **{value}** soblecoins!")
	else:
		await message.channel.send(f"<@!{message.author.nick}>, your next gift isn't ready yet! Try again {value}.")
	return True

@bot.command()
async def roll(message, value):
	status, change, multi = coin.luckyRoll(message.author.id, value)
	codes = {
		"int": f"<@!{message.author.id}>, you can only wager a whole number of soblecoins!",
		"reg": f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.",
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
		"reg": f"<@!{message.author.id}>, you aren't registered! Use `coinstart` to start using soblecoins.",
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
@bot.command(name="portfolioadd", aliases=["pfadd"])
async def pf(message, symbol, count):
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
async def spadd(message, song):
	await sp.addToGuildPlaylistGuildSide(message, song)
	return True

@bot.command(aliases=["playlistoverview"])
async def spoverview(message):
	members = getMemberList(message.guild.id)
	await sp.fetchGuildPlaylistOverviewGuildSide(message, members)
	return True

@bot.command(aliases=["playlistlink"])
async def splink(message):
	link = sp.getGuildPlaylist(message.guild.id).link
	await message.channel.send(link)
	return True

#TODO: rewrite to use the perm check feature
#TODO: do params need quotes? testing req'd
@bot.command(aliases=["playlistsettitle", "setplaylisttitle"])
async def spsettitle(message, title):
	perms = (message.author.guild_permissions.manage_guild)
	response = await sp.setGuildPlaylistTitleGuildSide(message, title, perms)
	if response:
		await message.add_reaction("👍")
		return True
	else:
		await message.add_reaction("👎")
		return False

@bot.command(aliases=["playlistsetdesc", "setplaylistdesc"])
async def spsetdesc(message, desc):
	perms = (message.author.guild_permissions.manage_guild)
	response = await sp.setGuildPlaylistDescGuildSide(message, desc, perms)
	if response:
		await message.add_reaction("👍")
		return True
	else:
		await message.add_reaction("👎")
		return False

#TODO: can multimessage handling be done better? :(
@bot.command(aliases=["playlistclear"])
async def spclear(message):
	perms = (message.author.guild_permissions.manage_guild)			
	if not perms:
		await message.channel.send("You'll need Manage Server perms to do that.")
		return False
	target = sp.getGuildPlaylist(message.guild.id)
	if target == None:
		await sp.reportNoGP(message)
		return False
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

#TODO: aliases spsetimage, spsetcover, spsetcoverimage
@bot.command(aliases=["playlistsetimage", "playlistsetcover", "spsetcover"])
async def spsetimage(message):
	try:
		newImg = message.attachments[0]
	except IndexError:
		await message.channel.send("Send an image with that command.")
		return False
	gph = sp.getGuildPlaylist(message.guild.id)
	if gph != None:
		response = await sp.encodeAndSetCoverImage(newImg, gph)
		if response:
			await message.add_reaction("👍")
			return True
		else:
			await message.add_reaction("👎")
			return False
	else:
		await sp.reportNoGP(message)
		return False

#TODO: alias spdelnewest, spdeletenewest
@bot.command(aliases=["spdeletenewest", "playlistdeletenewest"])
async def spdelnewest(message):
	perms = (message.author.guild_permissions.manage_guild)
	gph = sp.getGuildPlaylist(message.guild.id)
	if gph != None:
		response = await sp.undoAdditionGuildSide(message, gph, perms)
		if response == True:
			await message.add_reaction("👍")
			return True
		else:
			await message.add_reaction("👎")
			if response == "perm":
				await message.channel.send("You don't have permission to do that.")
			elif response == "empty":
				await message.channel.send("The playlist is empty already.")
			return False
	else:
		await sp.reportNoGP(message)
		return False

#TODO: alias spdelete, spremove
@bot.command(aliases=["playlistdelete", "playlistremove", "spremove"])
async def spdelete(message, song):
	perms = (message.author.guild_permissions.manage_guild)
	gph = sp.getGuildPlaylist(message.guild.id)
	if gph != None:
		response = await sp.deleteSongGuildSide(message, gph, song, perms)
		if response == True:
			await message.add_reaction("👍")
			return True
		else:
			await message.add_reaction("👎")
			if response == "perm":
				await message.channel.send("You don't have permission to do that.")
			if response == "notin":
				await message.channel.send(
					"That song doesn't seem to " +
					"be in your server's playlist.")
			return False
	else:
		await sp.reportNoGP(message)
		return False


bot.run(DISCORDTOKEN)