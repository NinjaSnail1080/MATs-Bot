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

import logging
import inspect

import config

logger = logging.getLogger("mat")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("mat.log", "w", "utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class MAT(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=["!mat ", "mat/", "mat.", "<@459559711210078209> "],
                         description="MAT's Bot",
                         pm_help=None,
                         activity=discord.Game("!mat help"),
                         fetch_offline_members=False)
        self.remove_command("help")

        members = inspect.getmembers(self)
        for name, member in members:
            if isinstance(member, commands.Command):
                if member.parent is None:
                    self.add_command(member)

    async def on_ready(self):
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')

    @commands.command()
    async def help(self, ctx):
        await ctx.send("Work in progress. My only command right now is `about`. My prefixes are "
                       "`!mat `, `mat.`, `mat/`, or you could mention me.")

    @commands.command()
    async def about(self, ctx):
        embed = discord.Embed(title="MAT's Bot", description="A open-source, general purpose "
                              "Discord bot written in Python.", color=discord.Color.from_rgb(
                                  0, 60, 255))
        embed.add_field(name="Version", value=__version__)
        embed.add_field(name="Author", value="NinjaSnail1080#8581")
        embed.add_field(name="Server Count", value=f"{len(bot.guilds)}")
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(name="License", value="GPL v3.0")
        embed.add_field(name="Github Repo", value="https://github.com/NinjaSnail1080/MATs-Bot")

        await ctx.send(embed=embed)

    def run(self):
        super().run(config.TOKEN)


if __name__ == "__main__":
    bot = MAT()
    bot.run()
