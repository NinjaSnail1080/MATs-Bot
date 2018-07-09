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
                           "commands)\n`image` (Image Manipulation commands)\n`info` (Information"
                           " commands)\n`mod` (Moderation commands)\n`music` (Music commands)\n"
                           "`nsfw` (NSFW commands)")

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
            "number of sides can be specified.\nFormat like this: `<prefix> diceroll (OPTIONAL)<# "
            "of sides>`", inline=False)
        embed.add_field(
            name="lenny", value="A list of Lenny faces for all your copypasting needs", inline=False)
        embed.add_field(name="xkcd", value="Posts a random xkcd comic", inline=False)

        await ctx.send(embed=embed)

    async def image(self, ctx):
        await ctx.send("No commands yet ¯\_(ツ)_/¯")

    async def info(self, ctx):
        embed = discord.Embed(
            title="Help | Information Commands", description=list_prefixes, color=mat_color)

        embed.add_field(name="info", value="Info about me!", inline=False)
        embed.add_field(name="serverinfo", value="Info about the server", inline=False)
        embed.add_field(
            name="userinfo", value="Info about a user. By default it'll show your user info, but "
            "you can specify a different member of your server.\nFormat like this: `<prefix> "
            "userinfo (OPTIONAL)<@mention user or user's id>`", inline=False)

        await ctx.send(embed=embed)

    async def mod(self, ctx):
        embed = discord.Embed(
            title="Help | Moderation Commands", description=list_prefixes, color=mat_color)

        embed.add_field(
            name="kick (Must have the \"kick members\" permission)", value="Kicks a member from "
            "the server.\nFormat like this: `<prefix> kick <@mention member(s)> <reason for "
            "kicking>` Put the reason in \"quotation marks\" if it's more than one word. If you "
            "want to kick multiple members, @mention all of them and surround their names with "
            "\"quotation marks\"", inline=False)
        embed.add_field(
            name="randomkick (Must have the \"kick members\" permission)", value="Kicks a random "
            "member, feeling lucky?\nFormat like this: `<prefix> randomkick (OPTIONAL)<list of "
            "@mentions you want me to randomly pick from>`. If you don't mention anyone, I'll "
            "randomly select someone from the server.", inline=False)

        await ctx.send(embed=embed)

    async def music(self, ctx):
        await ctx.send("No commands yet ¯\_(ツ)_/¯")

    async def nsfw(self, ctx):
        embed = discord.Embed(
            title="Help | NSFW Commands ( ͡° ͜ʖ ͡°)", description=list_prefixes, color=mat_color)

        embed.add_field(name="gonewild", value="Posts a random image from r/gonewild (Not "
                        "actually working yet. Heavy WIP)")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))

