"""
    MAT's Bot: An open-source, general purpose Discord bot written in Python.
    Copyright (C) 2018  NinjaSnail1080  (Discord Username: @NinjaSnail1080#8581)

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

from utils import CommandDisabled

from discord.ext import commands, tasks
import discord
import psutil

import collections
import datetime
import logging
import asyncio
import random
import aiohttp
import os
import re

import config
#* This module contains a variable called "TOKEN", which is assigned to a string that contains
#* the bot's token. It's needed in order to run the bot.
#*
#* It also contains a few more variables required to perform certain commands on the bot.
#* See "config_info.txt" for information on all the variables stored in this module.

#* Load cogs
initial_extensions = []
for f in os.listdir("cogs"):
    if f.endswith(".py"):
        f = f[:-3]
        initial_extensions.append("cogs." + f)
# initial_extensions.remove("cogs.discordbots") #* Uncomment this line to not use the top.gg api
# initial_extensions.remove("cogs.error_handlers")  #* For debugging purposes

#* Set up logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="mat.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


def get_prefix(bot, message):
    if message.guild is not None:
        guild_prefixes = bot.guilddata[message.guild.id]["prefixes"]
    else:
        guild_prefixes = []

    prefixes = bot.default_prefixes + guild_prefixes

    return commands.when_mentioned_or(*prefixes)(bot, message)


class MAT(commands.Bot):
    """MAT's Bot"""

    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         description="MAT's Bot",
                         case_insensitive=True,
                         help_command=None,
                         shard_count=1,
                         shard_id=0,
                         status=discord.Status.dnd,
                         activity=discord.Game("Initializing..."),
                         fetch_offline_members=False)

        self.process = psutil.Process((os.getpid()))

        self.update_version()

        self.ready_for_commands = False

        async def create_session():
            self.session = aiohttp.ClientSession(loop=self.loop)

        self.loop.run_until_complete(create_session())

        self.default_prefixes = ["!mat ", "mat/", "mat."]

        self.games = ["\"!mat help\" for help", "\"!mat help\" for help",
                      "\"!mat help\" for help", "\"!mat help\" for help",
                      "with you", "dead", "with myself", "a prank on you", "with fire",
                      "hard-to-get", "you like a god damn fiddle",
                      "on {} servers!", "with {} users!"]

        self.switch_games.start()

        for extension in initial_extensions:
            self.load_extension(extension)

        def check_disabled(ctx):
            if ctx.guild is not None:
                if ctx.command.name in self.guilddata[ctx.guild.id]["disabled"]:
                    raise CommandDisabled
            return True

        self.add_check(check_disabled)

    def update_version(self):
        self.__version__ = open("VERSION.txt").readline()

    async def on_connect(self):
        self.owner = (await self.application_info()).owner

        self.join_new_guild_message = (
            "Hello everyone, it's good to be here!\n\nI'm MAT, a Discord bot created by "
            f"**{self.owner}**. I can do a bunch of stuff with my "
            f"{len([c for c in self.commands if not c.hidden])} commands, but I'm still "
            "in developement, so even more features are coming soon.\n\nMy prefixes are "
            "`!mat`, `mat.` or `mat/`, though they are customizable per server.\nDo `!mat help` "
            "to get started")

        print("\nConnected to Discord")

    async def on_ready(self):
        print("\nLogged in as:")
        print(self.user)
        print(self.user.id)
        print("-----------------")
        print(datetime.datetime.now().strftime("%m/%d/%Y %X"))
        print("-----------------")
        print("Shards: " + str(self.shard_count))
        print("Servers: " + str(len(self.guilds)))
        print("Users: " + str(len(self.users)))
        print("-----------------\n")
        self.started_at = datetime.datetime.utcnow()

    async def on_command_completion(self, ctx):
        if not ctx.command.hidden:
            self.commands_used["TOTAL"] += 1
            self.commands_used[ctx.command.qualified_name] += 1
            self.botdata["commands_used"] = dict(self.commands_used)

            user_commands_used = collections.Counter(
                self.userdata[ctx.author.id]["commands_used"])
            user_commands_used["TOTAL"] += 1
            user_commands_used[ctx.command.qualified_name] += 1
            self.userdata[ctx.author.id]["commands_used"] = dict(user_commands_used)

            if ctx.guild is not None:
                guild_commands_used = collections.Counter(
                    self.guilddata[ctx.guild.id]["commands_used"])
                guild_commands_used["TOTAL"] += 1
                guild_commands_used[ctx.command.qualified_name] += 1
                self.guilddata[ctx.guild.id]["commands_used"] = dict(guild_commands_used)

    async def on_message(self, message):
        if not self.ready_for_commands:
            return

        self.messages_read["TOTAL"] += 1
        if message.guild is not None:
            self.messages_read[str(message.guild.id)] += 1 #* Keys in json must be strings

        self.botdata["messages_read"] = dict(self.messages_read)

        await self.process_commands(message)

    async def on_message_delete(self, message):
        if message.guild is not None and not message.author.bot:
            content = message.clean_content

            #* The following code is to better format custom emojis that appear in the content
            custom_emoji = re.compile(r"<:(\w+):(\d+)>")
            for m in custom_emoji.finditer(content):
                content = content.replace(m.group(), m.group()[1:-19])

            last_delete = {
                "author": message.author.mention,
                "content": content,
                "channel": message.channel.mention,
                "creation": message.created_at.strftime("**Sent on:** %A, %B %-d, %Y at %X UTC")
            }
            self.guilddata[message.guild.id]["last_delete"] = last_delete

    @tasks.loop()
    async def switch_games(self):
        game = random.choice(self.games)
        if game == self.games[-1]:
            await self.change_presence(activity=discord.Game(game.format(len(self.users))))
        elif game == self.games[-2]:
            await self.change_presence(activity=discord.Game(game.format(len(self.guilds))))
        else:
            await self.change_presence(activity=discord.Game(game))
        await asyncio.sleep(random.randint(12, 20))

    @switch_games.before_loop
    async def before_switch_games(self):
        await self.wait_until_ready()

    def run(self, token):
        try:
            self.loop.run_until_complete(self.start(token))
        except KeyboardInterrupt:
            print("\n\nClosing...\n")
            self.switch_games.cancel()

            for extention in self.extensions.copy():
                self.unload_extension(extention)
                print("Unloaded extension: " + extention)
            print("\n")
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
                print("Cancelled task: " + str(task._coro))

            print("\nLogging out...")
            self.loop.run_until_complete(self.logout())
        finally:
            try:
                self.loop.run_until_complete(self.dbl.close())
            except AttributeError:
                pass
            self.loop.run_until_complete(self.pool.close())
            self.loop.run_until_complete(self.session.close())
            self.loop.close()
            print("\nClosed\n")


if __name__ == "__main__":
    bot = MAT()
    bot.run(config.TOKEN)
