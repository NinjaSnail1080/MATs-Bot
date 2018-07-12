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
import discord


class Misc:
    """Miscellaneous commands. Don't show up in the help command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()  #* This line is temporarily gonna prevent anyone from using this command
    async def invite(self, ctx):
        """Generates an invite link for MAT's Bot"""

        await ctx.send(
            "Here's my invite link so you can invite me to your own server!:\nhttps://discordapp."
            "com/oauth2/authorize?client_id=459559711210078209&permissions=8&scope=bot")


def setup(bot):
    bot.add_cog(Misc(bot))
