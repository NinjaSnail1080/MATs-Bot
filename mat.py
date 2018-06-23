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

import logging
import inspect
import traceback
import random
import sys

import config

logger = logging.getLogger("mat")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("mat.log", "w", "utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

initial_extensions = ["cogs.triggers", "cogs.info"]

_commands = ["help", "info"]

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
                         activity=discord.Game("\"!mat help\" for help"),
                         fetch_offline_members=False)
        for cmd in _commands:
            self.remove_command(cmd)

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        print("Logged in as")
        print(bot.user.name)
        print(bot.user.id)
        print("---------")

    async def on_message(self, message):
        if message.author.bot:
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
