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

# list_prefixes = "**Prefixes**: `" + "` | `".join()) + "`"
list_prefixes = "**Prefixes**: `!mat` | `mat.` | `mat/`"


class Help:
    """Help commands"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command("help")

    @commands.command()
    async def help(self, ctx, cat=None):
        """HELP!"""
        if cat is None:
            embed = discord.Embed(
                title="MAT's Bot | Help Command", description=list_prefixes + "\n**Categories**:",
                color=mat_color)

            embed.add_field(
                name="<:confetti:464831811558572035> Fun", value="5 commands\n`<prefix> help "
                "fun` for more info")
            embed.add_field(
                name="<:paint:464836778000515072> Image Manipulation", value="0 commands\n"
                "`<prefix> help image` for more info")
            embed.add_field(
                name="<:info:464831966382915584> Info", value="2 commands\n`<prefix> help info` "
                "for more info")
            embed.add_field(
                name="<:Fist:464833337983500289> Moderation", value="2 commands\n`<prefix> help "
                "mod` for more info")
            embed.add_field(
                name=":notes: Music", value="0 commands\n`<prefix> help music` for more info")
            embed.add_field(
                name=":wink: NSFW", value="1 command\n`<prefix> help nsfw` for more info")

            await ctx.send(
                content="**Note**: I can't be on all the time. Since Ninja has no way of hosting "
                "me 24/7 as of now, I can only be on when he manually runs the script.",
                embed=embed)

        elif cat == "fun":
            await self.fun(ctx)

        elif cat == "info":
            await self.info(ctx)

    async def fun(self, ctx):
        embed = discord.Embed(
            title="Help | Fun Commands", description=list_prefixes, color=mat_color)

        embed.add_field(
            name="ascii", value="Converts an image into ascii art. Will work for most "
            "images\nFormat like this: `<prefix> ascii <image_url>`", inline=False)
        embed.add_field(
            name="coinflip", value="Flips a coin, pretty self-explanatory", inline=False)
        embed.add_field(
            name="diceroll", value="Rolls a dice. By default a 6-sided one though the "
            "number of sides can be specified. Format like this: `<prefix> diceroll (OPTIONAL)<# "
            "of sides>`", inline=False)
        embed.add_field(
            name="lenny", value="A list of Lenny faces for all your copypasting needs", inline=False)
        embed.add_field(name="xkcd", value="Posts a random xkcd comic", inline=False)

    async def info(self, ctx):
        embed = discord.Embed(
            title="Help | Info Commands", description=list_prefixes, color=mat_color)

        embed.add_field(name="info", value="Info about me!", inline=False)
        embed.add_field(name="serverinfo", value="Info about the server", inline=False)
        embed.add_field(
            name="userinfo", value="Info about a user. By default it'll show your user info, but "
            "you can specify a different member of your server. Format like this: `<prefix> "
            "userinfo (OPTIONAL)<@mention user or user's id>`", inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))

