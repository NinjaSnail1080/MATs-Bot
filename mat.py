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
__version__ = 0.6

from discord.ext import commands
import discord
import asyncio
import psutil
import rapidjson as json

import collections
import datetime
import logging
import random
import os
import re
import sys

import config
#* This module contains a variable called "TOKEN", which is assigned to a string that contains
#* the bot's token. It's needed in order to run the bot.
#*
#* It also contains a few more variables required to perform certain commands on the bot.
#* See "config_info.txt" for information on all the variables stored in this module.

games = ["\"!mat help\" for help", "\"!mat help\" for help", "\"!mat help\" for help",
         "\"!mat help\" for help", "\"!mat help\" for help", "with the server owner's dick",
         "with the server owner's pussy", "with you", "dead", "with myself",
         "a prank on you", "with fire", "hard-to-get", "Project X", "you like a god damn fiddle",
         "getting friendzoned by Sigma"]

if __name__ == "__main__":
    import urllib3

    urllib3.disable_warnings()

    #* Load cogs
    initial_extensions = []
    for f in os.listdir("cogs"):
        if f.endswith(".py"):
            if f != "__init__.py":
                f = f[:-3]
                initial_extensions.append("cogs." + f)
    # initial_extensions.remove("cogs.error_handlers")  #* For debugging purposes

    #* Set up logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="mat.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)


def get_data(to_return=None):
    """Gets data from all of the .data.json file"""

    if os.path.exists("bot.data.json"):
        with open("bot.data.json", "r") as f:
            botdata = dict(json.load(f))
    else:
        with open("bot.data.json", "w") as f:
            botdata = {"messages_read": {}, "commands_used": {}}
            json.dump(botdata, f)

    if os.path.exists("server.data.json"):
        with open("server.data.json", "r") as f:
            serverdata = dict(json.load(f))
    else:
        with open("server.data.json", "w") as f:
            serverdata = {}
            json.dump(serverdata, f)

    if os.path.exists("user.data.json"):
        with open("user.data.json", "r") as f:
            userdata = dict(json.load(f))
    else:
        with open("user.data.json", "w") as f:
            userdata = {}
            json.dump(userdata, f)

    if to_return is None:
        return
    elif to_return == "bot":
        return botdata
    elif to_return == "server":
        return serverdata
    elif to_return == "user":
        return userdata
    else:
        raise TypeError("\"to_return\" param must be either \"bot\", \"server\", or \"user\"")


def dump_data(to_dump, file):
    """Dumps data to the .data.json files"""

    if file == "bot":
        with open("bot.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)

    elif file == "server":
        with open("server.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)

    elif file == "user":
        with open("user.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)
    else:
        raise TypeError("\"file\" param must be either \"bot\", \"server\", or \"user\"")


def restart_bot():
    """Restarts the current program after cleaning up file objects and descriptors"""

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as exc:
        logging.error(exc)

    python = sys.executable
    os.execl(python, python, *sys.argv)


async def delete_message(ctx, time):
    """Deletes a command's message if the command was formatted incorectly"""

    await asyncio.sleep(time)
    try:
        await ctx.message.delete()
    except:
        pass
    return


def find_color(ctx):
    """Find the color of the bot's top role in the guild. Or if it's a DM,
    return Discord's "blurple" color
    """
    try:
        if ctx.guild.me.top_role.color == discord.Color.default():
            color = discord.Color.blurple()
        else:
            color = ctx.guild.me.top_role.color
        return color
    except AttributeError:  #* If it's a DM channel
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

        get_data()

        for extention in initial_extensions:
            self.load_extension(extention)

        self.commands_used = collections.Counter(get_data("bot")["commands_used"])
        self.messages_read = collections.Counter(get_data("bot")["messages_read"])

        def check_disabled(ctx):
            if "disabled" in get_data("server")[str(ctx.guild.id)]:
                return ctx.command.name not in get_data("server")[str(ctx.guild.id)]["disabled"]
            else:
                return True

        self.add_check(check_disabled)

    async def on_ready(self):
        serverdata = get_data("server")
        for g in self.guilds:
            if str(g.id) not in serverdata:
                serverdata[str(g.id)] = {"name": g.name, "triggers": {}}
                for c in g.text_channels:
                    serverdata[str(g.id)]["triggers"][str(c.id)] = "true"
        dump_data(serverdata, "server")

        print("\nLogged in as")
        print(bot.user)
        print(bot.user.id)
        print("-----------------")
        print(datetime.datetime.now().strftime("%m/%d/%Y %X"))
        print("-----------------")
        print("Shards: " + str(self.shard_count))
        print("Servers: " + str(len(self.guilds)))
        print("Users: " + str(len(set(self.get_all_members()))))
        print("-----------------\n")
        await self.change_presence(status=discord.Status.online)

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
                   f"{app.owner}. I can do a bunch of stuff, but I'm still very much in "
                   "developement, so even more features are coming soon!\n\nIn addition to all "
                   "my commands, I also have a numerous trigger words that server to "
                   "amuse/infuriate the people of this server!\n\nDo `!mat help` to get started")
        try:
            sent = False
            for c in guild.text_channels:
                if re.search("off-topic", c.name) or re.search("chat", c.name) or re.search(
                    "general", c.name):
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
        serverdata[str(guild.id)] = {"name": guild.name, "triggers": {}}
        for c in guild.text_channels:
            serverdata[str(guild.id)]["triggers"][str(c.id)] = "true"
        dump_data(serverdata, "server")

        joins = self.get_channel(465393762512797696)

        bots = []
        for m in guild.members:
            if m.bot:
                bots.append(m)

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
            content="I am now part of " + str(len(self.guilds)) + " servers and have " + str(
                len(set(self.get_all_members()))) + " unique users!", embed=embed)

    async def on_guild_remove(self, guild):
        serverdata = get_data("server")
        serverdata.pop(str(guild.id), None)
        dump_data(serverdata, "server")

    async def on_guild_update(self, before, after):
        serverdata = get_data("server")
        serverdata[str(before.id)]["name"] = after.name
        dump_data(serverdata, "server")

    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.TextChannel):
            serverdata = get_data("server")
            serverdata[str(channel.guild.id)]["triggers"][str(channel.id)] = "true"
            dump_data(serverdata, "server")

    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.TextChannel):
            serverdata = get_data("server")
            serverdata[str(channel.guild.id)]["triggers"].pop(str(channel.id), None)
            if serverdata[str(channel.guild.id)]["logs"] == str(channel.id):
                serverdata[str(channel.guild.id)].pop("logs", None)
            dump_data(serverdata, "server")

    async def on_member_join(self, member):
        serverdata = get_data("server")
        if "welcome" not in serverdata[str(member.guild.id)]:
            return
        else:
            channel = self.get_channel(int(
                serverdata[str(member.guild.id)]["welcome"]["channel"]))
            await channel.send(
                serverdata[str(member.guild.id)]["welcome"]["message"].format(member.mention))

    async def on_member_remove(self, member):
        serverdata = get_data("server")
        if "goodbye" not in serverdata[str(member.guild.id)]:
            return
        else:
            channel = self.get_channel(int(
                serverdata[str(member.guild.id)]["goodbye"]["channel"]))
            await channel.send(
                serverdata[str(member.guild.id)]["goodbye"]["message"].format(member.name))

    async def on_command_completion(self, ctx):
        if not ctx.command.hidden:
            self.commands_used["TOTAL"] += 1
            self.commands_used[ctx.command.name] += 1

            botdata = get_data("bot")
            botdata["commands_used"] = dict(self.commands_used)
            dump_data(botdata, "bot")

    async def on_message(self, message):
        if message.author.bot:
            return

        self.messages_read["TOTAL"] += 1
        if message.guild is not None:
            self.messages_read[str(message.guild.id)] += 1

        botdata = get_data("bot")
        botdata["messages_read"] = dict(self.messages_read)
        dump_data(botdata, "bot")

        await bot.process_commands(message)

    async def on_message_delete(self, message):
        if not isinstance(message.channel, discord.DMChannel):
            if not message.author.bot:
                content = message.clean_content + "\n"
                for a in message.attachments:
                    content = content + "\n" + a.url

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
        self.loop.create_task(self.switch_games())
        super().run(token)


if __name__ == "__main__":
    bot = MAT()
    bot.run(config.TOKEN)
