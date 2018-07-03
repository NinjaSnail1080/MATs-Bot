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

from mat import __version__, mat_color
from discord.ext import commands
import discord


class Info:
    "Information"

    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command("help")

    @commands.command()
    async def help(self, ctx):
        await ctx.send("**Work in progress**. My only commands right now are `info`, `lenny`, "
        "`coinflip`, `xkcd`, `kick`, and `randomkick`. My prefixes are `!mat `, `mat.`, `mat/`, "
        "or you could mention me. I also have numerous trigger words/phrases, which serve to "
        "amuse/infuriate the people of this server.\n\nNote: I can't be on all the time. Since "
        "Ninja has no way of hosting me 24/7 as of now, I can only be on when he manually runs "
        "the script.")

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(title="MAT's Bot", description="A open-source, general purpose "
                              "Discord bot written in Python.", color=mat_color)
        embed.add_field(name="Version", value=__version__)
        embed.add_field(name="Author", value="NinjaSnail1080#8581")
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(name="Language", value="Python 3.6.4")
        embed.add_field(name="Library", value="discord.py (rewrite)")
        embed.add_field(name="License", value="GPL v3.0")
        embed.add_field(name="Github Repo", value="https://github.com/NinjaSnail1080/MATs-Bot")
        embed.set_footer(text="Dedicated to WooMAT1417#1142")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
