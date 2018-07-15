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


class Owner:
    """Commands that can only be performed by the bot owner, NinjaSnail1080#858"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def quit(self, ctx):
        """Quit the bot's program"""

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("Can't delete message in this server")
        await self.bot.wait_until_ready()
        await self.bot.logout()
        await self.bot.close()


def setup(bot):
    bot.add_cog(Owner(bot))
