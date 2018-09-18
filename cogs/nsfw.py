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

try:
    from mat_experimental import find_color, delete_message
except ImportError:
    from mat import find_color, delete_message

from discord.ext import commands
from bs4 import BeautifulSoup
import discord
import aiohttp

import random

import config

#* MAT's Bot uses the NekoBot API for many of these commands.
#* More info at https://docs.nekobot.xyz/


class NSFW:
    """NSFW commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def send_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url=resp["message"])
        embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def anal(self, ctx):
        """Sends gifs of anal sex"""

        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/image?type=anal") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(aliases=["butts"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def ass(self, ctx):
        """Posts some ass"""

        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/image?type=ass") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(aliases=["tits"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def boobs(self, ctx):
        """Posts some boobs"""

        try:
            with ctx.channel.typing():
                async with self.session.get(
                    f"http://api.oboobs.ru/boobs/get/{random.randint(1, 13013)}") as w:
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

    @commands.command(name="4k", aliases=["fourk"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def fourk(self, ctx):
        """Sends some 4k porn (usually softcore)"""

        await ctx.channel.trigger_typing()
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

                    try:
                        del pics[0]
                        del pics[0]
                    except: pass
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
            return await delete_message(ctx, 6)

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def gonewild(self, ctx):
        """Sends a random post from either r/gonewild, r/gonewildcurvy, r/AsiansGoneWild, r/PetiteGoneWild, or r/BigBoobsGW
        Note: Sometimes, the image will be blank because I wasn't able to get a valid image url. In that case, you can just click on the title and go directly to the post"""

        subs = ["gonewild", "gonewildcurvy", "AsiansGoneWild", "PetiteGoneWild", "BigBoobsGW"]
        try:
            with ctx.channel.typing():
                async with self.session.get(
                    f"https://www.reddit.com/r/{random.choice(subs)}/hot.json?sort=hot",
                    headers=config.R_USER_AGENT) as w:

                    resp = await w.json()
                    data = random.choice(resp["data"]["children"])["data"]

                    if data["stickied"]:
                        raise Exception

                    embed = discord.Embed(
                        title=data["title"], description=f"By [u/{data['author']}](https://www."
                        f"reddit.com/user/{data['author']}/)", url="https://www.reddit.com" +
                        data["permalink"], color=find_color(ctx))
                    embed.set_image(url=data["url"])
                    embed.set_author(
                        name=data["subreddit_name_prefixed"],
                        url="https://www.reddit.com/" + data["subreddit_name_prefixed"])
                    embed.set_footer(text=f"👍 - {data['score']}")

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong and I wasn't able to get an image. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(aliases=["nekos"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def neko(self, ctx):
        """Posts some lewd nekos"""

        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/image?type="
                                    f"{random.choice(['lewdneko', 'lewdkitsune'])}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(aliases=["porngif"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def pgif(self, ctx):
        """Posts a porn gif"""

        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/image?type=pgif") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(hidden=True, brief="Invalid formatting. You need to include some search "
                      "terms after the command")
    @commands.guild_only()
    @commands.is_nsfw()
    async def phsearch(self, ctx, *, terms):
        """Search Pornhub!
        Format like this: `<prefix> phsearch <search terms>`
        """
        try:
            with ctx.channel.typing():
                async with self.session.get("https://www.pornhub.com/video/search?search="
                                            f"{terms.replace(' ', '+')}") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    title = soup.find("a", {"class": "img"})['title']
                    url = "https://www.pornhub.com" + soup.find("a", {"class": "img"})['href']
                    preview = soup.find("a", {"class": "img"}).img["data-image"]
                    duration = soup.find(
                        "div", {"class": "img fade fadeUp videoPreviewBg"}).var.get_text()

                    embed = discord.Embed(title=title, description="**Duration**: " + duration,
                                          color=find_color(ctx), url=url)
                    embed.set_image(url=preview)

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong and I wasn't able to get an image. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def pussy(self, ctx):
        """Posts some pussy"""

        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/image?type=pussy") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(aliases=["thigh"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def thighs(self, ctx):
        """Sends some thiccccccccc thighs"""

        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/image?type=thigh") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)


def setup(bot):
    bot.add_cog(NSFW(bot))
