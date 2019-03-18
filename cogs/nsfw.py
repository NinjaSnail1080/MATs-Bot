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

from utils import find_color, delete_message, get_reddit, ChannelNotNSFW

from discord.ext import commands
from bs4 import BeautifulSoup
import discord
import aiohttp

import random

import config


class NSFW(commands.Cog):
    """NSFW commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        elif not ctx.channel.is_nsfw() and ctx.command.name != "neko": #* See "neko" command
            raise ChannelNotNSFW
        return True

    async def send_nekobot_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url=resp["message"])
        embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.command()
    async def anal(self, ctx):
        """Sends gifs of anal sex"""

        await ctx.channel.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekobot.xyz/api/image?type=anal") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command()
    async def artsy(self, ctx):
        """Posts some artsy porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "SexyButNotPorn", "LaBeauteFeminine", "BacklitBeauty", "nsfw_bw")

    @commands.command()
    async def asian(self, ctx):
        """Posts pics of hot asians"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "AsianHotties", "Sexy_Asians", "asianbabes", "bustyasians",
                                "juicyasians", "AsiansGoneWild")

    @commands.command(aliases=["butt", "butts", "booty"])
    async def ass(self, ctx):
        """Posts some ass"""

        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://api.obutts.ru/butts/get/{random.randint(7, 5999)}") as w:
                        resp = await w.json()

                try:
                    resp = resp[0]
                except: pass

                url = "http://media.obutts.ru/" + resp["preview"]
                if resp["model"] is None or resp["model"] == "":
                    model = ""
                else:
                    model = "**Model**: " + resp["model"]

                embed = discord.Embed(color=find_color(ctx), description=model)
                embed.set_image(url=url)
                embed.set_footer(text=f"ass | {ctx.author.display_name}")

                await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    async def bdsm(self, ctx):
        """Posts some bdsm or bondage porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post", "bdsm", "bondage")

    @commands.command(aliases=["tits"])
    async def boobs(self, ctx):
        """Posts some boobs"""

        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://api.oboobs.ru/boobs/get/{random.randint(8, 13013)}") as w:
                        resp = await w.json()
                try:
                    resp = resp[0]
                except: pass

                url = "http://media.oboobs.ru/" + resp["preview"]
                if resp["model"] is None or resp["model"] == "":
                    model = ""
                else:
                    model = "**Model**: " + resp["model"]

                embed = discord.Embed(color=find_color(ctx), description=model)
                embed.set_image(url=url)
                embed.set_footer(text=f"boobs | {ctx.author.display_name}")

                await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    async def cute(self, ctx):
        """Posts some cute nude girls"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "adorableporn", "TooCuteForPorn", "legalteens", "18_19")

    @commands.command()
    async def cosplay(self, ctx):
        """Posts some sexy cosplay"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "cosplaygirls", "cosplayonoff", "FictionalBabes", "NSFWCostumes")

    @commands.command(aliases=["dickpic", "penis", "cock"])
    async def dick(self, ctx):
        """Posts a dick pic"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 200, True, False, "a post",
                                "PenisPics", "penis", "ratemycock", "MassiveCock", "Cock")

    @commands.command()
    async def ecchi(self, ctx):
        """Posts some ecchi (basically softcore hentai)"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post", "ecchi")

    @commands.command(name="4k", aliases=["fourk", "hdporn"])
    async def fourk(self, ctx):
        """Sends some 4k/UHD porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(
            ctx, 1, 100, True, False, "a post", "NSFW_Wallpapers", "HighResNSFW", "UHDnsfw")

    @commands.command()
    async def gonewild(self, ctx):
        """Sends a random post from either r/gonewild, r/gonewildcurvy, r/GoneWildSmiles, r/PetiteGoneWild, or r/RealGirls"""

        await ctx.channel.trigger_typing()
        return await get_reddit(
            ctx, 2, 200, True, True, "a post",
            "gonewild", "gonewildcurvy", "GoneWildSmiles", "PetiteGoneWild", "RealGirls")

    @commands.command()
    async def hentai(self, ctx, arg: str=None):
        """Posts some hentai. Add `-gif` after the command for a hentai gif OR add `-irl` for a hentai_irl post"""

        await ctx.channel.trigger_typing()
        if arg is None:
            return await get_reddit(ctx, 1, 100, True, False, "a post", "hentai")
        elif arg == "-gif":
            await ctx.channel.trigger_typing()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://nekobot.xyz/api/image?type=hentai_anal") as w:
                    resp = await w.json()
            return await self.send_nekobot_image(ctx, resp)
        elif arg == "-irl":
            return await get_reddit(ctx, 1, 75, True, False, "a post", "hentai_irl")
        else:
            await ctx.send("Invalid formatting. You can only add `-gif` after the command for a "
                           "hentai gif OR `-irl` for a hentai_irl post", delete_after=7.0)
            return await delete_message(ctx, 7)

    @commands.command(aliases=["stockings", "panties"])
    async def lingerie(self, ctx):
        """Posts pics of hot girls in lingerie"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "lingerie", "stockings", "pantyfetish", "panties")

    @commands.command(aliases=["nekos"])
    async def neko(self, ctx):
        """Posts some lewd nekos if used in an NSFW channel, or nonlewd nekos if used in a regular channel."""

        await ctx.channel.trigger_typing()
        if ctx.channel.is_nsfw():
            url = "https://nekos.life/api/lewd/neko"
        else:
            url = "https://nekos.life/api/neko"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as w:
                    resp = await w.json()

            embed = discord.Embed(color=find_color(ctx))
            embed.set_image(url=resp["neko"])
            embed.set_footer(text=f"neko | {ctx.author.display_name}")

            await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(aliases=["porngif"])
    async def pgif(self, ctx):
        """Posts a porn gif"""

        await ctx.channel.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekobot.xyz/api/image?type=pgif") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command(aliases=["vagina"])
    async def pussy(self, ctx):
        """Posts some pussy"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "pussy", "rearpussy", "simps", "spreading", "landingstrip")

    @commands.command()
    async def thighs(self, ctx):
        """Sends some thiccccccccc thighs"""

        await ctx.channel.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekobot.xyz/api/image?type=thigh") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)


def setup(bot):
    bot.add_cog(NSFW(bot))
