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

import datetime


class Info:
    """Information"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command("help")

    @commands.command()
    async def help(self, ctx):
        """Help"""
        await ctx.send("**Work in progress**. My commands right now are `info`, `lenny`, "
                       "`coinflip`, `diceroll`, `serverinfo`, `xkcd`, `ascii`, `kick`, and "
                       "`randomkick`. My prefixes are `!mat `, `mat.`, `mat/`, or you could "
                       "mention me. I also have numerous trigger words/phrases, which serve to "
                       "amuse/infuriate the people of this server.\n\nNote: I can't be on all "
                       "the time. Since Ninja has no way of hosting me 24/7 as of now, I can "
                       "only be on when he manually runs the script.")

    @commands.command()
    async def info(self, ctx):
        """Info about me"""
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

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx, id=None):
        """Info about the server."""
        if id is None:
            s = ctx.channel.guild
        else:
            s = self.bot.get_guild(int(id))

        if s is None:
            await ctx.send("This isn't a valid server id. Try again with a different one.")
        elif s is not None and s.unavailable:
            await ctx.send("This server is unavailable. I can't collect info on it. Try again "
                           "with a different id.")
        else:
            embed = discord.Embed(
                title=s.name, description="Server ID: " + str(s.id), color=mat_color)
            embed.set_thumbnail(url=s.icon_url)
            embed.add_field(name="Members", value=s.member_count)
            embed.add_field(name="Roles", value=len(s.roles))
            embed.add_field(name="Text Channels", value=len(s.text_channels))
            embed.add_field(name="Voice Channels", value=len(s.voice_channels))
            embed.add_field(name="Categories", value=len(s.categories))
            embed.add_field(name="Custom Emojis", value=len(s.emojis))
            embed.add_field(name="Region", value=str(s.region).upper())
            embed.add_field(
                name="Verification Level", value=str(s.verification_level).capitalize())
            if s.afk_channel is not None:
                embed.add_field(
                    name="AFK Channel", value=s.afk_channel.mention + " after " + str(
                        s.afk_timeout // 60) + " minutes")
            else:
                embed.add_field(name="AFK Channel", value="No AFK channel")
            embed.add_field(
                name="Server Creation Date", value=s.created_at.strftime("%b %-d, %Y"))
            if s.features:
                embed.add_field(name="Server Features", value=", ".join(s.features),
                inline=False)
            embed.add_field(
                name="Server Owner", value=str(s.owner) + " (User ID: " + str(s.owner_id) + ")",
                inline=False)

            delta = datetime.datetime.utcnow() - s.created_at

            y = int(delta.total_seconds()) // 31536000 #* Number of seconds in a non-leap year
            mo = int(delta.total_seconds()) // 2592000 % 12 #* Number of seconds in a 30 days
            d = int(delta.total_seconds()) // 86400 % 30 #* Number of seconds in a day
            h = int(delta.total_seconds()) // 3600 % 24 #* Number of seconds in an hour
            mi = int(delta.total_seconds()) // 60 % 60
            se = int(delta.total_seconds()) % 60
            #! Do not change "delta.totalseconds()" to "delta.seconds"
            #! For reasons I don't understand, it doesn't work

            if y == 1:
                year_s = " year"
            else:
                year_s = " years"
            if mo == 1:
                month_s = " month"
            else:
                month_s = " months"
            if d == 1:
                day_s = " day"
            else:
                day_s = " days"
            if h == 1:
                hour_s = " hour"
            else:
                hour_s = " hours"
            if mi == 1:
                minute_s = " minute"
            else:
                minute_s = " minutes"
            if se == 1:
                second_s = " second"
            else:
                second_s = " seconds"

            footer = []
            if y != 0:
                footer.append(str(y) + year_s + ", ")
            if mo != 0:
                footer.append(str(mo) + month_s + ", ")
            if d != 0:
                footer.append(str(d) + day_s + ", ")
            if h != 0:
                footer.append(str(h) + hour_s + ", ")
            if mi != 0:
                footer.append(str(mi) + minute_s + ", ")
            footer.append("and " + str(se) + second_s + ".")

            embed.set_footer(text=s.name + " has been around for roughly " + "".join(footer))

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
