import os
import discord
import functions as sob
import sobblepics
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

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
	c = (message.content).lower()
	#special interaction messages, do not require prefix
	if c == "hello sobbot":
		await message.channel.send("hi :pleading_face:")

	#prefixed messages
	if c.startswith('s!'):
		#remove prefix from search
		c = c[2:]

		if c == "flipcoin":
			await(message.channel.send(sob.flipCoin()))

		if c.startswith('d'):
			try:
				n = (int(c[1:]))
				await(message.channel.send(sob.die(n)))
			except typeError:
				pass

		if c == "sobbleimage":
			await(message.channel.send(file = sob.sobbleImage()))

client.run(TOKEN)