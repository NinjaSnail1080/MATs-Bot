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
from bs4 import BeautifulSoup
import discord
import asyncio
import aiohttp
import ascii

import random
import re


class Fun:
    """Fun stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ascii(self, ctx, image=None):
        """Converts an image into ascii art"""
        if image is not None:
            try:
                with ctx.channel.typing():
                    art = ascii.loadFromUrl(image, 60, False)
                    if len(art) > 2000:
                        art = "".join(art.split())
                        split_art = re.findall(".{1,1920}", art)
                        for a in split_art:
                            message = re.sub("(.{60})", "\\1\n", a, 0, re.DOTALL)
                            await ctx.send("```\n" + message + "```")
                    else:
                        await ctx.send("```\n" + art + "```")
            except:
                await ctx.send("Huh, something went wrong. I wasn't able to convert this image "
                               "into ascii art. Try again with a different picture.")
        else:
            await ctx.send("You need to include a link to the image you want to convert.\n\n"
                           "Format like this:  `!mat ascii https://www.example.com/image.png`")

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
    async def diceroll(self, ctx, sides=None):
        """Rolls a dice. By default a 6-sided one though the number of sides can be specified"""
        if sides is None:
            sides = "6"
        dice = str(random.randrange(1, int(sides) + 1))
        temp = await ctx.send("Rolling a " + sides + "-sided dice...")
        with ctx.channel.typing():
            await asyncio.sleep(2)
            await temp.delete()
            await ctx.send(dice + "!")

    @commands.command()
    async def lenny(self, ctx):
        """A list of Lenny faces for all your copypasting needs"""
        embed = discord.Embed(
            title="A list of Lenny faces for all your copypasting needs",
            color=mat_color, url="https://www.lennyfaces.net/")

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

    @commands.command()
    async def xkcd(self, ctx):
        """Posts a random xkcd comic"""
        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://c.xkcd.com/random/comic/") as w:
                        url = str(w.url)
                        soup = BeautifulSoup(await w.text(), "lxml")
                        title = soup.find("div", id="ctitle").get_text()
                        comic = soup.find("div", id="comic")
                        image = "https:" + comic.img["src"]
                        caption = comic.img["title"]

                embed = discord.Embed(title="xkcd | " + title, color=mat_color, url=url)
                embed.set_image(url=image)
                embed.set_footer(text=caption)

                await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I "
                           "wasn't able to get a comic. Try again in a little bit.")


def setup(bot):
    bot.add_cog(Fun(bot))
