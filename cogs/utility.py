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

from mat import find_color
from discord.ext import commands
import discord


class Utility:
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["avatar"])
    async def pfp(self, ctx, user=None):
        """Get a user's pfp. By default it retrieves your own but you can specify a different user
        Format like this: `<prefix> pfp (OPTIONAL)<@mention user or user's id>`
        """
        if user is None:
            m = ctx.author
        else:
            if ctx.message.mentions:
                for member in ctx.message.mentions:
                    m = member
                    break
            else:
                try:
                    m = ctx.channel.guild.get_member(int(user))
                except:
                    m = None
        if m is None:
            await ctx.send("Invalid user id or incorrect formatting. Make sure you format the "
                           "command correctly: `<prefix> pfp (OPTIONAL)<@mention user or user's "
                           "id>`")
        else:
            embed = discord.Embed(
                title=m.display_name + "'s Profile Pic", color=find_color(ctx, ctx.channel.guild),
                url=m.avatar_url)
            embed.set_image(url=m.avatar_url)

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
