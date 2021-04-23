import os
import discord
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

@client.event
async def on_message(message):
	if message.content == "hello sobbot":
		await message.channel.send("hi :pleading_face:")

client.run(TOKEN)