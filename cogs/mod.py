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

from mat import mat_color
from discord.ext import commands
import discord


class Moderation:
    "Moderation tools"

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, members, reason=None):
        if ctx.author.permissions_in(ctx.channel).kick_members:
            cant_kick = []
            if reason is None:
                reason = "No reason given"
            for m in ctx.message.mentions:
                if m != self.bot.user:
                    try:
                        await m.kick(reason=reason + " | Action performed by " + ctx.author.name)
                        await ctx.send(embed=discord.Embed(
                            color=mat_color, title=m.name + " kicked by " + 
                            ctx.author.name, description="Reason: " + reason))
                    except discord.Forbidden:
                        cant_kick.append(m.name)
            for i in cant_kick:
                await ctx.send(
                    "I don't have permissions to kick that person. What's the point of having "
                    "all these moderation commmands if I can't use them?\n\nEither I don't have "
                    "perms to kick, period, or my role is too low. Can one of you guys in charge "
                    "fix that please?")
        else:
            await ctx.send(
                "You don't have permissions to kick members. You better take this issue to "
                "whoever's in charge of your server")


def setup(bot):
    bot.add_cog(Moderation(bot))
