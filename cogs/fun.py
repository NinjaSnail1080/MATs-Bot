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
from bs4 import BeautifulSoup
import discord
import asyncio
import aiohttp
import ascii
import validators

import random
import re
import os


class Fun:
    """Fun stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ascii(self, ctx, *, image=None):
        """Converts an image into ascii art. Will work for most images.
        Format like this: `<prefix> ascii <image URL>`
        """
        if image is not None and validators.url(image):
            try:
                with ctx.channel.typing():
                    art = ascii.loadFromUrl(image, 60, False)
                    if len(art) > 1994:
                        art = "".join(art.split())
                        split_art = re.findall(".{1,1920}", art)
                        for a in split_art:
                            art = re.sub("(.{60})", "\\1\n", a, 0, re.DOTALL)
                            await ctx.send(f"```{art}```")
                    else:
                        await ctx.send(f"```{art}```")
            except OSError:
                await ctx.send("Huh, something went wrong. I wasn't able to convert this into "
                               "ascii art. Try again with a different image.", delete_after=7.0)
                await asyncio.sleep(7)
                await ctx.message.delete()
            except TypeError:
                await ctx.send("Huh, something went wrong. I wasn't able to convert this into "
                               "ascii art. Try again with a different image.", delete_after=7.0)
                await asyncio.sleep(7)
                await ctx.message.delete()
        elif image is None:
            await ctx.send("You need to include a link to the image you want to convert.\n\n"
                           "Format like this: `<prefix> ascii <image URL>`", delete_after=10.0)
            await asyncio.sleep(10)
            await ctx.message.delete()
        elif not validators.url(image):
            await ctx.send("Invalid url. The link to your image needs to look something like this"
                           ":\n\n`http://www.example.com/something/image.png`", delete_after=10.0)
            await asyncio.sleep(10)
            await ctx.message.delete()

    @commands.command()
    async def coinflip(self, ctx):
        """Flips a coin, pretty self-explanatory"""

        coin = random.choice(["Heads!", "Tails!"])
        temp = await ctx.send("Flipping...")
        with ctx.channel.typing():
            await asyncio.sleep(1)
            await temp.delete()
            await ctx.send(coin)

    @commands.command()
    async def commitstrip(self, ctx):
        """Posts a random CommitStrip comic (Only for programmers)"""

        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession().get(
                    "http://www.commitstrip.com/?random=1") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    title = soup.find("h1", "entry-title").get_text()
                    date = soup.find("time", "entry-date").get_text()
                    comic = soup.find("div", "entry-content")
                    image = comic.p.img["src"]

            embed = discord.Embed(title=title, color=find_color(ctx), url=url)

            embed.set_author(name="CommitStrip", url="http://www.commitstrip.com/en/?")
            embed.set_image(url=image)
            embed.set_footer(text="Published: " + date)

            await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=6.0)
            await asyncio.sleep(6)
            await ctx.message.delete()

    @commands.command()
    async def copypasta(self, ctx):
        """Posts a copypasta
        (Randomly selects from a list of 30)
        """
        await ctx.channel.trigger_typing()
        with open(os.path.join(
            os.path.dirname(__file__), "data" + os.sep + "copypastas.txt"), "r") as f:

            copypastas = f.read()
            copypastas = copypastas.split("\n\n\n\n")
            copypastas = list(filter(None, copypastas))

        await ctx.send(random.choice(copypastas))

    @commands.command(aliases=["ch", "cyha", "cyahap", "c&h"])
    async def cyhap(self, ctx):
        """Posts a random Cyanide & Happiness comic"""

        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession().get("http://explosm.net/comics/random") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    number = url.replace("http://explosm.net/comics/", "")[:-1]
                    image = "http:" + soup.find("img", id="main-comic")["src"]
                    info = soup.find("div", id="comic-author").get_text()

                    embed = discord.Embed(
                        title=f"Cyanide and Happiness #{number}", url=url, color=find_color(ctx))
                    embed.set_author(name="Explosm", url="http://explosm.net/")
                    embed.set_image(url=image)
                    embed.set_footer(text=info)

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=6.0)
            await asyncio.sleep(6)
            await ctx.message.delete()

    @commands.command(brief="The number of sides must be an **integer above 2**. Try again.")
    async def diceroll(self, ctx, sides: int=6):
        """Rolls a dice. By default a 6-sided one though the number of sides can be specified.
        Format like this: `<prefix> diceroll (OPTIONAL)<# of sides>`
        """
        if sides <= 2:
            await ctx.send("The number of sides must be an **integer above 2**. Try again.",
                           delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        dice = str(random.randint(1, sides))
        temp = await ctx.send(f"Rolling a {sides}-sided dice...")
        with ctx.channel.typing():
            await asyncio.sleep(1.5)
            await temp.delete()
            await ctx.send(dice + "!")

    @commands.command()
    async def f(self, ctx):
        """Pay your respects"""

        msg = await ctx.send(
            "%s has paid their respects. Press F to pay yours." % ctx.author.mention)
        await msg.add_reaction("\U0001f1eb")

    @commands.command()
    async def lenny(self, ctx):
        """A list of Lenny faces for all your copypasting needs"""

        embed = discord.Embed(
            title="A list of Lenny faces for all your copypasting needs",
            color=find_color(ctx), url="https://www.lennyfaces.net/")

        embed.add_field(name="Classic", value="( ͡° ͜ʖ ͡°)")
        embed.add_field(name="Pissed Off", value="( ͠° ͟ʖ ͡°)")
        embed.add_field(name="Winky", value="( ͡~ ͜ʖ ͡°)")
        embed.add_field(name="Wide-Eyed", value="( ͡◉ ͜ʖ ͡◉)")
        embed.add_field(name="Wide-Eyed 2", value="( ͡☉ ͜ʖ ͡☉)")
        embed.add_field(name="Happy", value="( ͡ᵔ ͜ʖ ͡ᵔ )")
        embed.add_field(name="Sad", value="( ͡° ʖ̯ ͡°)")
        embed.add_field(name="With Ears", value="ʕ ͡° ͜ʖ ͡°ʔ")
        embed.add_field(name="Communist", value="(☭ ͜ʖ ☭)")
        embed.set_footer(text="From: https://www.lennyfaces.net/")

        await ctx.send(embed=embed)

    @commands.command(aliases=["weirdspeak"])
    async def mock(self, ctx, *, stuff: str=None):
        """Say something and I'll mock you"""

        if stuff is None:
            await ctx.send("Dude, you need to say something for me to mock", delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url="https://media.discordapp.net/attachments/452928801093976064/"
                        "473376642069299201/mock.jpg")
        stuff = list(stuff.lower())
        mock = []
        for i in stuff:
            if i.lower() == "c":
                if random.randint(1, 2) == 1:
                    i = "k"
            if i.lower() == "k":
                if random.randint(1, 2) == 1:
                    i = "c"
            elif i.lower() == "x":
                if random.randint(1, 2) == 1:
                    i = "ks"
            if random.randint(1, 2) == 1:
                i = i.upper()
            mock.append(i)

        await ctx.channel.trigger_typing()
        await ctx.send(content="".join(mock), embed=embed)

    @commands.command()
    async def reverse(self, ctx, *, stuff: str=None):
        """Reverse the text you give me!"""

        if stuff is None:
            await ctx.send("Dude, you need to give me some text to reverse", delete_after=5.0)
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            await ctx.send(stuff[::-1])

    @commands.command(aliases=["print", "printf", "System.out.println", "echo", "std::cout<<",
                               "puts"])
    async def say(self, ctx, *, stuff=None):
        """Make me say something!"""

        if stuff is None:
            await ctx.send("Dude, you need to give me something to say", delete_after=5.0)
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            await ctx.send(stuff)

    @commands.command()
    async def xkcd(self, ctx):
        """Posts a random xkcd comic"""

        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession().get("https://c.xkcd.com/random/comic/") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    number = url.replace("https://xkcd.com/", "")[:-1]
                    title = soup.find("div", id="ctitle").get_text()
                    comic = soup.find("div", id="comic")
                    image = "https:" + comic.img["src"]
                    caption = comic.img["title"]

            embed = discord.Embed(
                title=f"{title} | #{number}", color=find_color(ctx), url=url)

            embed.set_author(name="xkcd", url="https://xkcd.com/")
            embed.set_image(url=image)
            embed.set_footer(text=caption)

            await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=6.0)
            await asyncio.sleep(6)
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(Fun(bot))
