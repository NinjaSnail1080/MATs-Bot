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

from discord.ext import commands
import discord
import aiohttp

import random


class NSFW:
    """NSFW commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gonewild(self, ctx):
        """Sends a random post from r/gonewild (Not actually working yet. Heavy WIP)"""

        #* Heavy WIP
        if ctx.channel.is_nsfw():
            with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://www.reddit.com/r/gonewild/hot.json?sort=hot", headers=
                        {"User-Agent": "mats-bot-reddit : v1.0 (by u/NinjaSnail1080)"}) as w:
                        page = w.json

                        embed = discord.Embed(color=find_color(ctx, ctx.channel.guild))
                        embed.set_image(url=random.choice(
                            ["https://i.pinimg.com/736x/05/15/cf/0515cf0c3e92d83deae8d0c4d880ebd6"
                             "--honeypot-penny.jpg", "http://ancensored.com/files/images/vthumbs/"
                             "p/55b26456f635ac3dbd7910fe21f2ec8b_full.jpg", "http://www.celebset."
                             "net/pics/P/3309Penny%20Baker%20(Mens%20Club).jpg", "https://i.pinim"
                             "g.com/736x/e0/26/3c/e0263c9fca451d3779dc6d409ddeb896--bathing-beaut"
                             "ies-bubble-baths.jpg"]))
                        await ctx.send("**Heavily WIP. Not working yet**. When finished, this "
                                    "command will send a random post from r/gonewild.\n\nFor "
                                    "now, enjoy this picture of Penny Baker", embed=embed)
        else:
            await ctx.send("You must be in an NSFW channel to use that command.")


def setup(bot):
    bot.add_cog(NSFW(bot))
