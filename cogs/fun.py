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


class Fun:
    """Fun stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ascii(self, ctx, *, image=None):
        """Converts an image into ascii art. Will work for most images.
        Format like this:`<prefix> ascii <image URL>`
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
                            await ctx.send("```" + art + "```")
                    else:
                        await ctx.send("```" + art + "```")
            except OSError:
                await ctx.send("Huh, something went wrong. I wasn't able to convert this into "
                               "ascii art. Try again with a different image.", delete_after=7.0)
            except TypeError:
                await ctx.send("Huh, something went wrong. I wasn't able to convert this into "
                               "ascii art. Try again with a different image.", delete_after=7.0)
        elif image is None:
            await ctx.send("You need to include a link to the image you want to convert.\n\n"
                           "Format like this: `<prefix> ascii <image URL>`", delete_after=10.0)
        elif not validators.url(image):
            await ctx.send("Invalid url. The link to your image needs to look something like this"
                           ":\n\n`http://www.example.com/something/image.png`", delete_after=10.0)

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
            #! Temporary operation to figure out exactly what this exception is and what causes it
            import traceback
            print(traceback.format_exc())
            #! Temporary operation ^
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=5.0)

    @commands.command()
    async def diceroll(self, ctx, sides: int=6):
        """Rolls a dice. By default a 6-sided one though the number of sides can be specified.
        Format like this: `<prefix> diceroll (OPTIONAL)<# of sides>`
        """
        try:
            if sides <= 2:
                raise ValueError
            dice = str(random.randint(1, sides))
            temp = await ctx.send("Rolling a %d-sided dice..." % sides)
            with ctx.channel.typing():
                await asyncio.sleep(1.5)
                await temp.delete()
                await ctx.send(dice + "!")
        except ValueError:
            await ctx.send("The number of sides must be an **integer above 2**. Try again.",
                           delete_after=5.0)

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

    @commands.command(aliases=["print", "printf", "System.out.println", "echo", "std::cout<<",
                               "puts"])
    async def say(self, ctx, *, stuff=None):
        """Make me say something!"""

        if stuff is None:
            await ctx.send("Um, you do realize that you need to give me something to say, right?",
                           delete_after=5.0)
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
                title=title + " | #" + number, color=find_color(ctx), url=url)

            embed.set_author(name="xkcd", url="https://xkcd.com/")
            embed.set_image(url=image)
            embed.set_footer(text=caption)

            await ctx.send(embed=embed)
        except:
            #! Temporary operation to figure out exactly what this exception is and what causes it
            import traceback
            print(traceback.format_exc())
            #! Temporary operation ^
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=5.0)


def setup(bot):
    bot.add_cog(Fun(bot))
