import os
import discord
import time
import functions as sob
from dotenv import load_dotenv

load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')

client = discord.Client()

startTime = 0

@client.event
async def on_ready():
	print(f"{client.user} initialized.")

	guildCount = 0

	for guild in client.guilds:
		print(f"Connected to {guild.name} ({guild.id}).")
		guildCount = guildCount + 1

	global startTime
	startTime = time.time()

	print(f"{guildCount} total connected servers.")
	print(f"{client.user} is ready!")
	print(f"Time: {time.ctime(startTime)}")
	channel = client.get_channel(835267335169245255)
	await channel.send("im conected")


@client.event
async def on_message(message):
	if message.author.id != 835251884104482907:
		c = (message.content).lower()
		
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
				except typeError:
					pass

			if c == "sobbleimage":
				await(message.channel.send(file = sob.sobbleImage()))

			if c.startswith("math"):
				content = sob.parseMath(c[4:].strip())
				if content != None:
					await(message.channel.send(content))
			
			if c.startswith("pkmn"):
				data = c[4:].strip()      #data is query
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
				await(message.channel.send(time.ctime(startTime)))
				#maybe format this a little nicer?

client.run(DISCORDTOKEN)