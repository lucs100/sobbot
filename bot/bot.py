import os
import discord
import functions as sob
from dotenv import load_dotenv

load_dotenv()
DISCORDTOKEN = os.getenv('DISCORDTOKEN')

client = discord.Client()

@client.event
async def on_ready():
	print(f"{client.user} initialized.")

	guildCount = 0

	for guild in client.guilds:
		print(f"Connected to {guild.name} ({guild.id}).")
		guildCount = guildCount + 1

	print(f"{guildCount} total connected servers.")
	print(f"{client.user} is ready!")
	channel = client.get_channel(835267335169245255)
	await channel.send("im conected")
	

@client.event
async def on_message(message):
	if message.author.id != 835251884104482907:
		c = (message.content).lower()
		
		#special interaction messages, do not require prefix
		if c == "hello sobbot":
			await message.channel.send("hi :pleading_face:")

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
				await(message.channel.send(sob.parseMath(c[4:].strip())))
			
			if c.startswith("pkmn"):
				data = c[4:].strip()      #data is query
				try:
					data = int(data)      #rehashes as int if possible
				except ValueError:
					pass
				finally:
					
					await(message.channel.send(embed=sob.pkmnLookup(data)))      #is str by default, triggering reverse search mode, but when query is int, uses normal mode

client.run(DISCORDTOKEN)