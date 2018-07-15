"""
    MAT's Bot: An open-source, general purpose Discord bot written in Python.
    Copyright (C) 2018  NinjaSnail1080  (Discord User: @NinjaSnail1080#8581)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__version__ = 0.4

from discord.ext import commands
import discord
import asyncio

import logging
import random
import os
import re

import config
#* This module contains a single variable called "TOKEN", which is assigned to a string that
#* contains the bot's token. It's needed in order to run the bot.

games = ["\"!mat help\" for help", "\"!mat help\" for help", "\"!mat help\" for help",
         "\"!mat help\" for help", "\"!mat help\" for help", "with the server owner's dick",
         "with the server owner's pussy", "with you", "dead", "with myself",
         "some epic game that you don't have", "with fire", "hard-to-get", "Project X",
         "you like a god damn fiddle", "getting friendzoned by Sigma"]

last_delete = {"author": None, "content": None, "channel": None, "creation": None}

if __name__ == "__main__":
    from cogs import *
    import urllib3

    urllib3.disable_warnings()

    #* Load cogs
    initial_extensions = []
    for f in os.listdir("cogs"):
        if f != "__init__.py":
            if f.endswith(".py"):
                f = f[:-3]
                initial_extensions.append("cogs." + f)

    #* Set up logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="mat.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)


def find_color(guild=None):
    if guild is not None:
        if guild.me.top_role.color == discord.Color.default():
            color = discord.Color.blurple()
        else:
            color = guild.me.top_role.color
        return color
    else:
        color = discord.Color.blurple()
        return color


async def get_prefix(bot, message):
    prefixes = ["!mat ", "mat/", "mat."]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class MAT(commands.Bot):
    """MAT's Bot"""

    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         description="MAT's Bot",
                         pm_help=None,
                         shard_count=1,
                         shard_id=0,
                         status=discord.Status.dnd,
                         activity=discord.Game("Initializing..."),
                         fetch_offline_members=False)

        for extention in initial_extensions:
            self.load_extension(extention)

    async def on_ready(self):
        print("\nLogged in as")
        print(bot.user)
        print(bot.user.id)
        print("-----------------")
        print("Shards: " + str(self.shard_count))
        print("Servers: " + str(len(self.guilds)))
        print("Users: " + str(len(set(self.get_all_members()))))
        print("-----------------")
        await self.change_presence(status=discord.Status.online)

    async def on_guild_join(self, guild):
        message = ("Hello everyone, it's good to be here!\n\nHey, as a favor, could one of you "
                   "change my role's color to **#003cff**? It's kinda my signature color, but "
                   "due to an issue with how Discord's permission system works, I can't "
                   "automatically change my role's color to that. So it'd be great if one of you "
                   "guys in charge could do it for me.\n\nAnyway, I can do many things! Type "
                   "!mat help to get started")
        sent = False
        for c in guild.text_channels:
            if re.search("off-topic", c.name) or re.search("chat", c.name) or re.search(
                "general", c.name):
                await c.send(message)
                sent = True
                break
        if not sent:
            c = random.choice(guild.text_channels)
            await c.send("~~Damn, you guys must have a really strange system for naming your "
                         "channels~~\n\n" + message)

        support_server = self.get_guild(463959531807047700)
        joins = support_server.get_channel(465393762512797696)

        embed = discord.Embed(
            title="Joined " + guild.name, description="**ID**: " + str(guild.id) +
            "\n**Joined**: " + guild.me.joined_at.strftime("%b %-d, %Y at %X UTC"),
            color=discord.Color.from_rgb(0, 60, 255))
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        embed.add_field(name="Categories", value=len(guild.categories))
        embed.add_field(name="Custom Emojis", value=len(guild.emojis))
        embed.add_field(
            name="Verification Level", value=str(guild.verification_level).capitalize())
        embed.add_field(name="Region", value=str(guild.region).upper())
        if guild.afk_channel is not None:
            embed.add_field(
                name="AFK Channel", value=guild.afk_channel.mention + " after " + str(
                    guild.afk_timeout // 60) + " minutes")
        else:
            embed.add_field(name="AFK Channel", value="No AFK channel")
        embed.add_field(
            name="Server Created", value=guild.created_at.strftime("%b %-d, %Y"))
        if guild.features:
            embed.add_field(name="Server Features", value=", ".join(guild.features),
                            inline=False)
        embed.add_field(
            name="Server Owner", value=str(guild.owner) + " (User ID: " + str(
                guild.owner_id) + ")", inline=False)

        await joins.send(
            content="I am now part of " + str(len(self.guilds)) + " servers and have " + str(
                len(set(self.get_all_members()))) + " unique users!", embed=embed)

    async def on_message(self, message):
        if message.author == bot.user:
            return

        await bot.process_commands(message)

    async def on_message_delete(self, message):
        if message.author != bot.user:
            global last_delete
            last_delete = {"author": message.author.display_name,
                           "content": message.clean_content,
                           "channel": message.channel,
                           "creation": message.created_at}

    async def switch_games(self):
        await self.wait_until_ready()
        while True:
            await self.change_presence(activity=discord.Game(random.choice(games)))
            await asyncio.sleep(random.randint(4, 8))

    def run(self, token):
        self.loop.create_task(self.switch_games())
        super().run(token)


if __name__ == "__main__":
    bot = MAT()
    bot.run(config.TOKEN)
