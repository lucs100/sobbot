import os
import discord
import time
import functions as sob
import riotapi
import currency as coin
import finance
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')

client = discord.Client()

startTime = time.time()

@client.event
async def on_ready():
	print(f"{client.user} initialized.")

	guildCount = 0

	for guild in client.guilds:
		print(f"Connected to {guild.name} ({guild.id}).")
		guildCount = guildCount + 1 # print all connected guilds 

	global startTime
	startTime = time.time() # show time connected in console
	timeFormatted = datetime.fromtimestamp(startTime).strftime("%I:%M %p, %B %d %Y")

	print(f"({guildCount}) total connected servers.")
	print(f"{client.user} is ready!")
	print(f"Time: {timeFormatted}")
	channel = client.get_channel(835267335169245255) # sobblelink channel
	await channel.send("im conected")
	# await sob.setActivity(client) #not working yet
	await client.change_presence(activity=discord.Game(name="sobling")) # placeholder until i set up activity

@client.event
async def on_message(message):
	if message.author.id != 835251884104482907: #not from sobbot
		c = (message.content).lower()
		coin.messageBonus(message.author.id) #check droprate for passive coin earning
		
		#special interaction/command messages, do not require prefix
		if c == "hello sobbot":
			await message.channel.send("hi :pleading_face:")
			
		if c == "ping":
			await message.channel.send("pong! ({0}ms)".format(int(client.latency*1000)))

		#special channels
		if message.channel.id == 835388133959794699:
			content = sob.parseMath(c)
			if content != None:
				await message.channel.send(content)

		#prefixed messages
		if c.startswith('s!'):
			#remove prefix from search
			c = c[2:]


			# Miscellaneous Functions


			if c == "flipcoin":
				await message.channel.send(sob.flipCoin())

			if c.startswith('d'):
				try:
					n = (int(c[1:]))
					await message.channel.send(sob.die(n))
				except:
					pass

			if c == "sobbleimage":
				await message.channel.send(file = sob.sobbleImage())

			if c.startswith("math"):
				content = sob.parseMath(c[4:].strip())
				await message.channel.send(content)
			
			if c.startswith("pkmn"):
				data = c[4:].strip()      #query
				try:
					data = int(data)      #rehashes as int if possible
				except ValueError:
					pass
				finally:
					embed = sob.pkmnLookup(data)
					if embed != None: 	  #result found
						await message.channel.send(embed=sob.pkmnLookup(data))
			
			if c == "uptime":
				await message.channel.send(sob.timeRunning(startTime))

			if c == "starttime":
				startingTime = datetime.fromtimestamp(startTime).strftime("%B %d at %I:%M %p")
				await message.channel.send(f"Sobbot has been online since {startingTime}!")
				#maybe format this a little nicer?
			
			if c == "randblue" or c == "randbluw":
				embed, file = (sob.randomBlue())
				await message.channel.send(embed=embed, file=file)
			
			if c.startswith("link"):
				try:
					channelid = int(c[4:].strip())
					channel = client.get_channel(channelid)
				except:
					return True
				print("Link successful.")
				await sob.pipeline(channel)
				print("Link ended.")
			

			# LoL Functions
			

			if c.startswith("lollevel"):
				try:
					name = c[8:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or sname
						if name == False:
							await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!lolregister to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
							return True
					data = riotapi.getNameAndLevel(name)
					if data == False:
						await message.channel.send("Key expired.")
						return True
					name, level = data["name"], data["level"]
					await message.channel.send(f"Summoner **{name}** is level **{level}**.")
				except:
					await message.channel.send(f"Summoner **{name}** doesn't exist.")
					return True

			if c.startswith("lolmastery"):
				try:
					name = c[10:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or summoner name
						if name == False:
							await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!lolregister to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
							return True
					embed = riotapi.embedTopMasteries(name)
					if embed == False:
						await message.channel.send("Key expired.")
						return True
					await message.channel.send(embed=embed)
				except:
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
							await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!lolregister to add your summoner name. You can also specify a summoner name after this command to use it while unregistered.")
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
					return True
				except:
					return True

			if c == "lolapireload":
				if message.author.id == 312012475761688578:
					if await riotapi.updateAPIKey():
						await message.channel.send("Successfully set key!")
					else:
						await message.channel.send("Key update failed.")
				else:
					await message.channel.send("You don't have the permissions to do this.")


			# Currency Functions


			if c == "coinstart":
				ok = coin.addRegistration(message.author.id)
				if ok:
					await message.channel.send(f"<@!{message.author.id}> added to soblecoin! You have {coin.getUserCoins(message.author.id)} coins.")
					return True
				await message.channel.send(f"<@!{message.author.id}> , you already have soblecoins! You have {coin.startingCoins} coins.")
				return False
			
			if c.startswith("give"):
				try:
					sender = message.author.id
					recipient, value = c[4:].split()
					recipient = recipient[3:-1]
					value = int(value)
					ok = coin.give(sender, recipient, value)
					messages = {
						#indexed by error code
						0: f"Sent **{value}** soblecoins to <@!{recipient}>!",
						1: f"<@!{recipient}> doesn't have soblecoins enabled, or doesn't exist.",
						2: f"Soblecoins not sent! You don't have enough soblecoins.",
						3: f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.",
						4: f"You can't send coins to yourself!"
					}
					if ok in messages:
						await message.channel.send(messages[ok])
				except:
					await message.channel.send("Use s!give (recipient) (value) to send a friend soblecoins!")
				return True
			
			if c == "balance":
				value = coin.getUserCoins(message.author.id)
				if value == None:
					await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.")
				else:
					await message.channel.send(f"<@!{message.author.id}>, you have **{value}** soblecoins!")
				return True
			
			if c == "claim":
				ok, value = coin.claimHourly(message.author.id)
				if ok:
					if value == 1000:
						await message.channel.send(f"<@!{message.author.id}>, your balance was topped up to **{value}** soblecoins!")
					else:
						await message.channel.send(f"<@!{message.author.id}> claimed **{value}** soblecoins!")
				else:
					if value == -1:
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.")
					else:
						await message.channel.send(f"<@!{message.author.id}>, your next gift isn't ready yet! Try again {value}.")

			if c.startswith("roll"):
				value = c[4:].strip()
				status, change, multi = coin.luckyRoll(message.author.id, value)
				if status == "int":
					await message.channel.send(f"<@!{message.author.id}>, you can only wager a whole number of soblecoins!")
				if status == "reg":
					await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.")
				elif status == "insuff":
					await message.channel.send(f"<@!{message.author.id}>, you only have {change} soblecoins!")
				elif status == "ok":
					if multi > 1:
						await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi} and won {change} soblecoins!")
					if multi == 1:
						await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! You didn't win or lose soblecoins.")
					if multi < 1:
						await message.channel.send(f"<@!{message.author.id}>, you rolled x{multi}! Sorry, you lost {change} soblecoins :frowning:")
			
			if c == "shop":
				await message.channel.send(embed = coin.getShop())
			
			if c.startswith("buy"):
				c = c[3:].strip()
				code, num = coin.buyFromShop(c, message.author.id)
				messages = {
					"exist": f"<@!{message.author.id}>, no item with the ID {c} exists!",
					"reg": f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.",
					"broke": f"<@!{message.author.id}>, you only have {num} soblecoins!",
					"limit": f"<@!{message.author.id}>, you already own that limited item.",
					"prereq": f"<@!{message.author.id}>, you need a prerequisite item in order to buy that."
				}
				if code in messages:
					await message.channel.send(messages[code])
				else:
					await message.channel.send(f"<@!{message.author.id}>, you purchased a **{code}**! You now own {num}.")

			if c == "inventory":
				await message.channel.send(coin.getInventoryEmbed(message.author.id))
			

			# Finance Functions


			if c.startswith("ticker"):
				c = c[6:].strip()
				embed = finance.createStockEmbed(c)
				if embed != None:
					await message.channel.send(embed=embed)
				else:
					await message.channel.send(f"Symbol {c.upper()} doesn't seem to exist :(")

				
	return True
				
client.run(DISCORDTOKEN)