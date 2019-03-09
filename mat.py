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

from discord.ext import commands
from utils import get_data, dump_data, CommandDisabled
import discord

import collections
import datetime
import logging
import asyncio
import random
import os
import re

import config
#* This module contains a variable called "TOKEN", which is assigned to a string that contains
#* the bot's token. It's needed in order to run the bot.
#*
#* It also contains a few more variables required to perform certain commands on the bot.
#* See "config_info.txt" for information on all the variables stored in this module.

games = ["\"!mat help\" for help", "\"!mat help\" for help", "\"!mat help\" for help",
         "\"!mat help\" for help", "\"!mat help\" for help", "some epic game you don't have",
         "with you", "dead", "with myself", "a prank on you", "with fire", "hard-to-get",
         "Project X", "you like a god damn fiddle", "getting friendzoned by Sigma"]

if __name__ == "__main__":
    #* Load cogs
    initial_extensions = []
    for f in os.listdir("cogs"):
        if f.endswith(".py"):
            f = f[:-3]
            initial_extensions.append("cogs." + f)
    # initial_extensions.remove("cogs.error_handlers")  #* For debugging purposes

    #* Set up logger
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="mat.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)


async def get_prefix(bot, message):
    prefixes = ["!mat "]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class MAT(commands.Bot):
    """MAT's Bot"""

    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         description="MAT's Bot",
                         case_insensitive=True,
                         pm_help=None,
                         shard_count=1,
                         shard_id=0,
                         status=discord.Status.dnd,
                         activity=discord.Game("Initializing..."),
                         fetch_offline_members=False)

        get_data()

        for extension in initial_extensions:
            self.load_extension(extension)

        self.commands_used = collections.Counter(get_data("bot")["commands_used"])
        self.messages_read = collections.Counter(get_data("bot")["messages_read"])

        def check_disabled(ctx):
            if ctx.channel.guild is not None:
                if "disabled" in get_data("server")[str(ctx.guild.id)]:
                    if ctx.command.name in get_data("server")[str(ctx.guild.id)]["disabled"]:
                        raise CommandDisabled
            return True

        self.add_check(check_disabled)

    async def on_connect(self):
        print("\nConnected to Discord")

    async def on_ready(self):
        serverdata = get_data("server")
        for g in self.guilds:
            if str(g.id) not in serverdata:
                serverdata[str(g.id)] = {"name": g.name}
        dump_data(serverdata, "server")

        self.loop.create_task(self.switch_games())

        print("\nLogged in as:")
        print(bot.user)
        print(bot.user.id)
        print("-----------------")
        print(datetime.datetime.now().strftime("%m/%d/%Y %X"))
        print("-----------------")
        print("Shards: " + str(self.shard_count))
        print("Servers: " + str(len(self.guilds)))
        print("Users: " + str(len(set(self.get_all_members()))))
        print("-----------------\n")
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game(random.choice(games)))

        if os.path.exists("restart"):
            with open("restart", "r") as f:
                _id = int(f.read())
            os.remove("restart")
            channel = self.get_channel(_id)
            await channel.send("And we're back!")
            self.loop.create_task(self.switch_games())

    async def on_guild_join(self, guild):
        app = await self.application_info()
        message = ("Hello everyone, it's good to be here!\n\nI'm MAT, a Discord bot created by "
                   f"**{app.owner}**. I can do a bunch of stuff, but I'm still very much in "
                   "developement, so even more features are coming soon!\n\nIn addition to all "
                   "my commands, I also have a numerous trigger words that server to "
                   "amuse/infuriate the people of this server!\n\nDo `!mat help` to get started")
        try:
            sent = False
            for c in guild.text_channels:
                if re.search("off-topic", c.name) or re.search("chat", c.name) or re.search(
                    "general", c.name) or re.search("bot", c.name):
                    await c.send(
                        embed=discord.Embed(description=message, color=discord.Color.blurple()))
                    sent = True
                    break
            if not sent:
                c = random.choice(guild.text_channels)
                await c.send(
                    content="~~Damn, you guys must have a really strange system for naming your "
                    "channels~~", embed=discord.Embed(description=message,
                    color=discord.Color.blurple()))
        except: pass

        serverdata = get_data("server")
        serverdata[str(guild.id)] = {"name": guild.name}
        dump_data(serverdata, "server")

        joins = self.get_channel(465393762512797696)

        bots = []
        for m in guild.members:
            if m.bot:
                bots.append(m)

        embed = discord.Embed(
            title="Joined " + guild.name, description="**ID**: " + str(guild.id) +
            "\n**Joined**: " + guild.me.joined_at.strftime("%b %-d, %Y at %X UTC"),
            color=joins.guild.me.color)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        embed.add_field(name="Categories", value=len(guild.categories))
        embed.add_field(name="Custom Emojis", value=len(guild.emojis))
        embed.add_field(name="Bots", value=len(bots))
        embed.add_field(name="Region", value=str(guild.region).upper())
        embed.add_field(
            name="Verification Level", value=str(guild.verification_level).capitalize())
        embed.add_field(
            name="Explicit Content Filter", value=str(guild.explicit_content_filter).title())
        if guild.afk_channel is not None:
            embed.add_field(
                name="AFK Channel", value=guild.afk_channel.mention + " after " + str(
                    guild.afk_timeout // 60) + " minutes")
        else:
            embed.add_field(name="AFK Channel", value="No AFK channel")
        embed.add_field(
            name="Server Created", value=guild.created_at.strftime("%b %-d, %Y"))
        if guild.features:
            embed.add_field(
                name="Server Features", value="`" + "`, `".join(guild.features) + "`",
                inline=False)
        embed.add_field(
            name="Server Owner", value=str(guild.owner) + " (User ID: " + str(
                guild.owner_id) + ")", inline=False)

        await joins.send(
            content=f"I am now part of {len(self.guilds)} servers and have "
                f"{len(set(self.get_all_members()))} unique users!", embed=embed)

    async def on_guild_remove(self, guild):
        serverdata = get_data("server")
        serverdata.pop(str(guild.id), None)
        dump_data(serverdata, "server")

    async def on_guild_update(self, before, after):
        serverdata = get_data("server")
        serverdata[str(before.id)]["name"] = after.name
        dump_data(serverdata, "server")

    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.TextChannel):
            serverdata = get_data("server")
            if "triggers_disabled" in serverdata[str(channel.guild.id)]:
                if str(channel.id) in serverdata[str(channel.guild.id)]["triggers_disabled"]:
                    serverdata[str(channel.guild.id)]["triggers_disabled"].remove(str(channel.id))
                    dump_data(serverdata, "server")

    async def on_member_join(self, member):
        serverdata = get_data("server")
        if "welcome" in serverdata[str(member.guild.id)]:
            channel = self.get_channel(int(
                serverdata[str(member.guild.id)]["welcome"]["channel"]))
            await channel.send(
                serverdata[str(member.guild.id)]["welcome"]["message"].format(member.mention))

    async def on_member_remove(self, member):
        serverdata = get_data("server")
        if "goodbye" in serverdata[str(member.guild.id)]:
            channel = self.get_channel(int(
                serverdata[str(member.guild.id)]["goodbye"]["channel"]))
            await channel.send(
                serverdata[str(member.guild.id)]["goodbye"]["message"].format(member.mention))

    async def on_command_completion(self, ctx):
        if not ctx.command.hidden:
            self.commands_used["TOTAL"] += 1
            self.commands_used[ctx.command.name] += 1

            botdata = get_data("bot")
            botdata["commands_used"] = dict(self.commands_used)
            dump_data(botdata, "bot")

    async def on_message(self, message):
        if message.author == bot.user:
            return

        self.messages_read["TOTAL"] += 1
        if message.guild is not None:
            self.messages_read[str(message.guild.id)] += 1

        botdata = get_data("bot")
        botdata["messages_read"] = dict(self.messages_read)
        dump_data(botdata, "bot")

        if not message.author.bot:
            await bot.process_commands(message)

    async def on_message_delete(self, message):
        if not isinstance(message.channel, discord.DMChannel):
            if not message.author.bot:
                content = message.clean_content

                #* The following code is to better format custom emojis that appear in the content
                custom_emoji = re.compile(r"<:(\w+):(\d+)>")
                for m in custom_emoji.finditer(content):
                    content = content.replace(m.group(), m.group()[1:-19])

                last_delete = {"author": message.author.mention,
                               "content": content,
                               "channel": message.channel.mention,
                               "creation": message.created_at.strftime(
                                   "**Sent on:** %A, %B %-d, %Y at %X UTC")}

                serverdata = get_data("server")
                serverdata[str(message.guild.id)]["last_delete"] = last_delete
                dump_data(serverdata, "server")

    async def switch_games(self):
        await self.wait_until_ready()
        while True:
            await self.change_presence(activity=discord.Game(random.choice(games)))
            await asyncio.sleep(random.randint(5, 10))

    def run(self, token):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.start(token))
        except KeyboardInterrupt:
            print("\n\nClosing...\n")
            for task in asyncio.Task.all_tasks(loop):
                task.cancel()
                print("Cancelled task")
            print("\nLogging out...")
            loop.run_until_complete(self.logout())
        finally:
            loop.close()
            print("\nClosed\n")


if __name__ == "__main__":
    bot = MAT()
    bot.run(config.TOKEN)
