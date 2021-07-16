# sobbot - an experimental discord bot

Repository for Sobbot, a personal Discord bot.
Sobbot is mainly a side project intended for me to gain experience using Python as an interface between Discord, Sobbot's logic, and various APIs, with a some smaller random features thrown in as well.

Sobbot started out as a small test project in using discord.py, but has quickly become my principal side project, showcasing what I feel is my best work to date. My aim is for Sobbot to resemble a full-featured Discord bot with proper input validation and error handling (ie. working as if it were a public-use bot). Despite its feature-crept feel, I try for the more trivial features to be remnants of me learning to work with a project of medium scale. Most of the features I add moving forwards are going to be much more complex in nature, meant to be developed like and feel like production-quality features.

Despite this, Sobbot is at its core my personal Discord bot. I don't *intend* for Sobbot to gain steam and become a popular bot - its API keys would quickly hit rate limits and it is very inconsistently online, however, you're more than welcome to use Sobbot's code as a starter for your own bot. Read the [LICENSE](https://github.com/lucs100/sobbot/blob/main/LICENSE) for more info on this.
Instructions for repurposing Sobbot's code as your own bot:

1. Set up a bot on Discord's developer portal, and acquire its token.
2. Create a file named .env in /bot, and paste `DISCORDTOKEN=yourTokenHere`.
	1. You'll need to paste `RIOTTOKEN=yourTokenHere` in order to use Sobbot's Riot API features, however, this is optional.
		- Note that Riot is very strict about how their API keys are used, and you will need to use an ephemeral key unless your get your project approved.
4. Add your bot to a server using a bot link.
5. Run bot/bot.py.

### NOT RECCOMENDED: You may freely add Sobbot to any Discord server in which you have the *Manage Server* permission using [this link](https://discord.com/oauth2/authorize?client_id=835251884104482907&permissions=34816&scope=bot).

Use s!help for a directory Sobbot's commands. Alternatively, use s!about for info on more niche features.

Sobbot's default prefix is s!, which can be changed using s!prefix `yourprefixhere`.

## Disclaimer, due to repository name and content:

This repository is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by Nintendo. Use of any and all trademarked names in this product are purely coincidental and not endorsed by Nintendo.
