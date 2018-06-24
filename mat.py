"""
    MAT's Bot: An open-source, general purpose Discord bot written in Python
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
__version__ = 0.1

from discord.ext import commands
import discord
import asyncio

import inspect
import random
import os

import config

if __name__ == "__main__":
    from cogs import *

    initial_extensions = []
    for f in os.listdir("cogs"):
        if f != "__init__.py":
            if f.endswith(".py"):
                f = f.replace(".py", "")
                initial_extensions.append("cogs." + f)

    _commands = info._commands

    games = ["\"!mat help\" for help", "\"!mat help\" for help", "\"!mat help\" for help",
            "\"!mat help\" for help", "\"!mat help\" for help", "with the server owner's dick", 
            "with the server owner's pussy", "with you", "dead","with myself", 
            "some epic game that you don't have", "with fire", "hard-to-get", "Project X", 
            "getting friendzoned by Sigma", "getting friendzoned by Monika"]


def get_prefix(bot, message):

    prefixes = ["!mat ", "mat/", "mat."]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class MAT(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         description="MAT's Bot",
                         pm_help=None,
                         shard_id=0,
                         status=discord.Status.dnd,
                         activity=discord.Game("Initializing..."),
                         fetch_offline_members=False)

        for cmd in _commands:
            self.remove_command(cmd)

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

    async def on_message(self, message):
        if message.author == bot.user:
            return

        await bot.process_commands(message)

    async def switch_games(self):
        await self.wait_until_ready()
        while True:
            await self.change_presence(activity=discord.Game(random.choice(games)))
            await asyncio.sleep(5)

    def run(self):
        self.loop.create_task(self.switch_games())
        super().run(config.TOKEN)


if __name__ == "__main__":
    bot = MAT()
    bot.run()
