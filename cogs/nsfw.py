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

# from mat import find_color
from mat_experimental import find_color

from discord.ext import commands
from bs4 import BeautifulSoup
import discord
import asyncio
import aiohttp

import random

#* MAT's Bot uses the NekoBot API for many of these commands.
#* More info at https://docs.nekobot.xyz/

r_user_agent = {"User-Agent": "mats-bot-reddit:1.0"}


class NSFW:
    """NSFW commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def send_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=6.0)
            await asyncio.sleep(6)
            return await ctx.message.delete()

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url=resp["message"])
        embed.set_footer(text=ctx.author.display_name)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def ass(self, ctx):
        """Posts some ass"""

        with ctx.channel.typing():
            async with self.session.get("https://nekobot.xyz/api/image?type=ass") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(name="4k", aliases=["fourk"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def fourk(self, ctx):
        """Sends some 4k porn (usually softcore)"""

        with ctx.channel.typing():
            async with self.session.get("https://nekobot.xyz/api/image?type=4k") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def girl(self, ctx):
        """Sends a pic of a (usually nude) girl"""

        try:
            with ctx.channel.typing():
                async with self.session.get("https://russiasexygirls.com/?random") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    title = soup.find("span", "entry-title").get_text()

                    pics = []
                    for p in soup.find_all("p"):
                        if "https://russiasexygirls.com/" in str(p):
                            pics.append(p)

                    del pics[0]
                    del pics[0]
                    image = random.choice(pics).a.img["src"]

                embed = discord.Embed(
                    title=title, description="Click above for more images from this album",
                    color=find_color(ctx), url=url)
                embed.set_image(url=image)
                embed.set_footer(text="From: russiasexygirls.com")

                await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a picture. Try again in a little bit.", delete_after=6.0)
            await asyncio.sleep(6)
            return await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def gonewild(self, ctx):
        """Sends a random post from either r/gonewild, r/gonewildcurvy, r/AsiansGoneWild, r/PetiteGoneWild, or r/BigBoobsGW
        Note: Sometimes, the image will be blank because I wasn't able to get a valid image url. In that case, you can just click on the title and go directly to the post"""

        with ctx.channel.typing():
            subs = ["gonewild", "gonewildcurvy", "AsiansGoneWild", "PetiteGoneWild", "BigBoobsGW"]
            try:
                async with self.session.get(
                    f"https://www.reddit.com/r/{random.choice(subs)}/hot.json?sort=hot",
                    headers=r_user_agent) as w:

                    resp = await w.json()
                    data = random.choice(resp["data"]["children"])["data"]

                    embed = discord.Embed(
                        title=data["title"], description=f"By u/{data['author']}",
                        url="https://www.reddit.com" + data["permalink"], color=find_color(ctx))
                    embed.set_image(url=data["url"])
                    embed.set_author(
                        name=data["subreddit_name_prefixed"],
                        url="https://www.reddit.com/" + data["subreddit_name_prefixed"])
                    embed.set_footer(text=f"👍 - {data['score']}")

                    await ctx.send(embed=embed)

            except:
                await ctx.send("Huh, something went wrong and I wasn't able to get an image. "
                               "Try again", delete_after=6.0)
                await asyncio.sleep(6)
                await ctx.message.delete()

    @commands.command(aliases=["nekos"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def neko(self, ctx):
        """Posts some lewd nekos"""

        with ctx.channel.typing():
            async with self.session.get("https://nekobot.xyz/api/image?type="
                                        f"{random.choice(['lewdneko', 'lewdkitsune'])}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def pussy(self, ctx):
        """Posts some pussy"""

        with ctx.channel.typing():
            async with self.session.get("https://nekobot.xyz/api/image?type=pussy") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)


def setup(bot):
    bot.add_cog(NSFW(bot))
