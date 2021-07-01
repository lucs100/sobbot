# sobbot - an aimless discord bot

Repository for Sobbot, a personal Discord bot.
Sobbot is mainly a side project intended for me to gain experience using Python as an interface between Discord, Sobbot's logic, and various API's, with a lot of random features thrown in as well. This is intentional - Sobbot isn't really intended to be a general use Discord bot, but rather a compilation of tons of side projects too small for their own repoitories, wrapped into a Discord bot.

However, you're more than welcome to use Sobbot's code as a starter for your own bot, or even verbatim rebranded as your own bot. Read the [LICENSE](https://github.com/lucs100/sobbot/blob/main/LICENSE) for more info on this.
Instructions for repurposing Sobbot's code as your own bot:

1. Set up a bot on Discord's developer portal, and acquire its token.
2. Create a file named .env in /bot, and paste `DISCORDTOKEN=yourTokenHere`.
	1. You will need to paste `RIOTTOKEN=yourTokenHere` in order to use Sobbot's Riot API features, however, this is optional.
4. Add your bot to a server using a bot link.
5. Run bot/bot.py.

### NOT RECCOMENDED: You may freely add Sobbot to any Discord server in which you have the *Manage Server* permission using [this link](https://discord.com/oauth2/authorize?client_id=835251884104482907&permissions=34816&scope=bot).

Use s!help for help with Sobbot's commands. (coming soon)

Sobbot's default prefix is s!, which can be changed using s!prefix `yourprefixhere`.

## Disclaimer, due to repository name and content:

This repository is not endorsed by, directly affiliated with, maintained, authorized, or sponsored by Nintendo. Use of any and all trademarked names in this product are not endorsed by Nintendo.
