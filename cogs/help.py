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

from cogs.fun import Fun
from cogs.info import Info
from cogs.mod import Moderation
from cogs.music import Music
from cogs.nsfw import NSFW

# list_prefixes = "**Prefixes**: `" + "` | `".join()) + "`"
list_prefixes = "**Prefixes**: `!mat` | `mat.` | `mat/`"


class Help:
    """Help commands"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command("help")

    @commands.command()
    async def help(self, ctx, cat=None):
        """MAT's Bot | Help command"""

        if cat is None:
            embed = discord.Embed(
                title="MAT's Bot | Help command", description=list_prefixes + "\n**Categories**:",
                color=find_color(ctx, ctx.channel.guild))

            embed.add_field(
                name="<:confetti:464831811558572035> Fun", value="5 commands\n`<prefix> help "
                "fun` for more info", inline=False)
            embed.add_field(
                name="<:info:464831966382915584> Info", value="2 commands\n`<prefix> help info` "
                "for more info", inline=False)
            embed.add_field(
                name="<:Fist:464833337983500289> Moderation", value="2 commands\n`<prefix> help "
                "mod` for more info", inline=False)
            embed.add_field(
                name=":notes: Music", value="0 commands\n`<prefix> help music` for more info",
                inline=False)
            embed.add_field(
                name=":wink: NSFW", value="1 command\n`<prefix> help nsfw` for more info",
                inline=False)

            await ctx.send(
                content="**Note**: I can't be on all the time. Since Ninja has no way of hosting "
                "me 24/7 as of now, I can only be on when he manually runs the script.",
                embed=embed)

        elif cat == "fun":
            await self.fun(ctx)

        elif cat == "image":
            await self.image(ctx)

        elif cat == "info":
            await self.info(ctx)

        elif cat == "mod":
            await self.mod(ctx)

        elif cat == "music":
            await self.music(ctx)

        elif cat == "nsfw":
            await self.nsfw(ctx)

        else:
            await ctx.send("That's not a category. The ones you can pick are:\n`fun` (Fun "
                           "commands)\n`info` (Information commands)\n`mod` (Moderation commands)"
                           "\n`music` (Music commands)\n`nsfw` (NSFW commands)")

    async def fun(self, ctx):
        """Help | Fun Commands"""

        embed = discord.Embed(
            title=self.fun.__doc__, description=list_prefixes, color=find_color(
                ctx, ctx.channel.guild))

        embed.add_field(
            name="ascii", value=Fun.ascii.help, inline=False)
        embed.add_field(
            name="coinflip", value=Fun.coinflip.help, inline=False)
        embed.add_field(
            name="diceroll", value=Fun.diceroll.help, inline=False)
        embed.add_field(
            name="lenny", value=Fun.lenny.help, inline=False)
        embed.add_field(name="xkcd", value=Fun.xkcd.help, inline=False)

        await ctx.send(embed=embed)

    async def image(self, ctx):

        await ctx.send("No commands yet ¯\_(ツ)_/¯")

    async def info(self, ctx):
        """Help | Information Commands"""

        embed = discord.Embed(
            title=self.info.__doc__, description=list_prefixes, color=find_color(
                ctx, ctx.channel.guild))

        embed.add_field(name="info", value=Info.info.help, inline=False)
        embed.add_field(name="serverinfo", value=Info.serverinfo.help, inline=False)
        embed.add_field(name="userinfo", value=Info.userinfo.help, inline=False)

        await ctx.send(embed=embed)

    async def mod(self, ctx):
        """Help | Moderation Commands"""

        embed = discord.Embed(
            title=self.mod.__doc__, description=list_prefixes, color=find_color(
                ctx, ctx.channel.guild))

        embed.add_field(
            name="kick (Must have the \"kick members\" permission)", value=Moderation.kick.help,
            inline=False)
        embed.add_field(
            name="purge (Must have the \"manage messages\" permission",
            value=Moderation.purge.help, inline=False)
        embed.add_field(
            name="randomkick (Must have the \"kick members\" permission)",
            value=Moderation.randomkick.help, inline=False)

        await ctx.send(embed=embed)

    async def music(self, ctx):
        """Help | Music Commands"""

        await ctx.send("No commands yet ¯\_(ツ)_/¯")

    async def nsfw(self, ctx):
        """Help | NSFW Commands ( ͡° ͜ʖ ͡°)"""

        embed = discord.Embed(
            title=self.nsfw.__doc__, description=list_prefixes, color=find_color(
                ctx, ctx.channel.guild))

        embed.add_field(name="gonewild", value=NSFW.gonewild.help)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))

