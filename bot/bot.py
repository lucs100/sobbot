import os
import discord
import time
import functions as sob
import riotapi
import currency as coin
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
		guildCount = guildCount + 1

	global startTime
	startTime = time.time()
	timeFormatted = datetime.fromtimestamp(startTime).strftime("%I:%M %p, %B %d %Y")

	print(f"({guildCount}) total connected servers.")
	print(f"{client.user} is ready!")
	print(f"Time: {timeFormatted}")
	channel = client.get_channel(835267335169245255)
	await channel.send("im conected")
	# await sob.setActivity(client) #not working yet
	await client.change_presence(activity=discord.Game(name="sobling"))

@client.event
async def on_message(message):
	if message.author.id != 835251884104482907: #not from sobbot
		c = (message.content).lower()
		coin.messageBonus(message.author.id) #check droprate for passive coin earning
		
		#special interaction/command messages, do not require prefix
		if c == "hello sobbot":
			await message.channel.send("hi :pleading_face:")
			
		if c == "ping":
			await(message.channel.send("pong! ({0}ms)".format(int(client.latency*1000))))

		#special channels
		if message.channel.id == 835388133959794699:
			content = sob.parseMath(c)
			if content != None:
				await(message.channel.send(content))

		#prefixed messages
		if c.startswith('s!'):
			#remove prefix from search
			c = c[2:]

			if c == "coin":
				await(message.channel.send(sob.flipCoin()))

			if c.startswith('d'):
				try:
					n = (int(c[1:]))
					await(message.channel.send(sob.die(n)))
				except:
					pass

			if c == "sobbleimage":
				await(message.channel.send(file = sob.sobbleImage()))

			if c.startswith("math"):
				content = sob.parseMath(c[4:].strip())
				await(message.channel.send(content))
			
			if c.startswith("pkmn"):
				data = c[4:].strip()      #query
				try:
					data = int(data)      #rehashes as int if possible
				except ValueError:
					pass
				finally:
					embed = sob.pkmnLookup(data)
					if embed != None: 	  #result found
						await(message.channel.send(embed=sob.pkmnLookup(data)))
			
			if c == "uptime":
				await(message.channel.send(sob.timeRunning(startTime)))

			if c == "starttime":
				startingTime = datetime.fromtimestamp(startTime).strftime("%B %d at %I:%M %p")
				await(message.channel.send(f"Sobbot has been online since {startingTime}!"))
				#maybe format this a little nicer?
			
			if c == "randblue" or c == "randbluw":
				fp, content = (sob.randomBlue())
				await(message.channel.send(file=fp, content=content))
			
			if c.startswith("link"):
				try:
					channelid = int(c[4:].strip())
					channel = client.get_channel(channelid)
				except:
					return True
				print("Link successful.")
				await sob.pipeline(channel)
				print("Link ended.")
			
			if c.startswith("lollevel"):
				# try:
					name = c[8:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or sname
						if name == False:
							await(message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!lolregister to add your summoner name. You can also specify a summoner name after this command to use it while unregistered."))
							return True
					data = riotapi.getNameAndLevel(name)
					if data == False:
						await(message.channel.send("Key expired."))
						return True
					name, level = data["name"], data["level"]
					await(message.channel.send(f"Summoner **{name}** is level **{level}**."))
				# except:
				# 	await(message.channel.send(f"Summoner **{name}** doesn't exist."))
				# 	return True

			if c.startswith("lolmastery"):
				try:
					name = c[10:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or sname
						if name == False:
							await(message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!lolregister to add your summoner name. You can also specify a summoner name after this command to use it while unregistered."))
							return True
					embed = riotapi.embedTopMasteries(name)
					if embed == False:
						await(message.channel.send("Key expired."))
						return True
					await(message.channel.send(embed=embed))
				except:
					await(message.channel.send(f"Summoner **{name}** doesn't exist, or your key expired. Try again!"))
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
					await(message.channel.send(f"Set <@!{id}>'s summoner name to **{ok}**!"))
				else:
					await(message.channel.send(f"Summoner **{name}** doesn't exist, or your key expired. Try again!"))
				return True

			if c.startswith("lolrank"):
				try:
					name = c[7:].strip()
					if name.strip() == "":
						name = riotapi.isUserRegistered(message.author.id) #bool or sname
						if name == False:
							await(message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!lolregister to add your summoner name. You can also specify a summoner name after this command to use it while unregistered."))
							return True
					embed = riotapi.embedRankedData(name)
					if embed == False:
						await(message.channel.send("Key expired."))
						return True
					await(message.channel.send(embed=embed))
				except:
					await(message.channel.send(f"Summoner **{name}** doesn't exist, or your key expired. Try again!"))
					return True

			if c == "coinstart":
				ok = coin.addRegistration(message.author.id)
				if ok:
					await(message.channel.send(f"<@!{message.author.id}> added to soblecoin! You have {coin.getUserCoins(message.author.id)} coins."))
					return True
					await(message.channel.send(f"<@!{message.author.id}> , you already have soblecoins! You have {coin.startingCoins} coins."))
				return False
			
			if c.startswith("give"):
				# try:
				sender = message.author.id
				recipient, value = c[4:].split()
				recipient = recipient[3:-1]
				value = int(value)
				ok = coin.give(sender, recipient, value)
				if ok == 0:
					await message.channel.send(f"Sent **{value}** soblecoins to <@!{recipient}>!")
				if ok == 1:
					await message.channel.send(f"<@!{recipient}> doesn't have soblecoins enabled, or doesn't exist.")
				if ok == 2:
					await message.channel.send(f"Soblecoins not sent! You don't have enough soblecoins.")
				if ok == 3:
					await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.")
				if ok == 4:
					await message.channel.send(f"You can't send coins to yourself!")
				# except:
					# await(message.channel.send("Use s!give (recipient) (value) to send a friend soblecoins!"))
				return True
			
			if c == "balance":
				value = coin.getUserCoins(message.author.id)
				if value == None:
					await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.")
				else:
					await message.channel.send(f"<@!{message.author.id}>, you have **{value}** soblecoins!")
				return True
			
			if c == "claim":
				data = coin.claimHourly(message.author.id)
				if data[0] == True:
					await message.channel.send(f"<@!{message.author.id}> claimed **{data[1]}** soblecoins!")
				else:
					if str(data[1]) == str(-1):
						await message.channel.send(f"<@!{message.author.id}>, you aren't registered! Use s!coinstart to start using soblecoins.")
					else:
						await message.channel.send(f"<@!{message.author.id}>, your next gift isn't ready yet! Try again {data[1]}.")

	return True
				
client.run(DISCORDTOKEN)