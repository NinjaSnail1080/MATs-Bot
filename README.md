# MAT's Bot
***A multi-purpose Discord Bot created by NinjaSnail1080#8581***

__Default prefixes__: `!mat`, `mat.`, or `mat/`

Note: The prefix `!mat` must have a space between it and the command. The other two don't require this space.

The prefix can be changed for your server with the `prefix` command.

## Self-Hosting
I would prefer if you didn't self-host my bot. Instead, you can just invite it to your own server [here](https://discordapp.com/oauth2/authorize?client_id=459559711210078209&scope=bot&permissions=2146958591). However, if you really want to self-host it, the installation steps are as follows:

1. **Get Python 3.5.3 or higher**

This is required to actually run the bot

2. **Clone this repository**

3. **Set up a virtual environment**

Do `python3 -m venv <path to repository>`

4. **Once in the venv, install dependencies**

Run `python3 -m pip install -U -r REQUIREMENTS.txt`

5. **Create a database in PostGreSQL**

You will need version 9.5 or higher

6. **Setup configuration**

Create a file in the root directory called `config.py` and add the variables required to run the bot. There's a list of them in `config_info.txt`.

## Features
MAT's Bot has over 180 commands, including but not limited to:

- Moderation
	- Kick, ban, softban, mute (channel-specific or server-wide)
	- Purge messages
	- Self-assignable roles
	- Create giveaways
	- Starboard system
	- Disable and enable commands
	- Custom welcome and goodbye messages
- MEMES!
- Information
	- Info on the server, a member, channel, role, etc.
	- Bot stats
- Image Manipulation
	- Convert images into ascii art (one of my favorites)
	- Read text from an image
	- Create memes
	- Deepfry, magikify, and blurpify pictures
- MORE MEMES!
- Tag system; tag text for later retrieval
- Utility
	- Get current weather around the world
	- Convert between currencies
	- Dictionary and thesaurus commands
	- Search Google images
	- Set reminders
- Get C&H and xkcd comics
- Create wordclouds for text channels
- Start an Akinator game
- ...and more!

Invite MAT's Bot to your server and type `!mat help` for more info and a full list of commands. Report any problems you may run into at my [support server](https://discord.gg/P4Fp3jA).

### Coming Soon
 - Music commands
 - Economy
 - Auto moderation
 - Leveling
