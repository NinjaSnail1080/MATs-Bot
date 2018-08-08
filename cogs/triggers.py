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

from mat import find_color, get_data
from discord.ext import commands
import discord
import asyncio

import re
import os
import random

sigma_responses = ["Woah, who is that other bot? She looks g-g-gorgeous...", "D-D-Does s-s-she "
                   "have a boyf-f-friend?\nAsking for a friend!", "What a beautiful voice...",
                   "Oh, I hope she doesn't see my Playing status..."]


class Triggers:
    """Trigger words that the bot will respond to"""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.guild is not None:
            if get_data(
                "server")[str(message.guild.id)]["triggers"][str(message.channel.id)] == "false":
                return

        if message.author.id == 281807963147075584:
            return await message.channel.send(random.choice(sigma_responses))

        if random.randint(1, 500) == 1:
            return await message.channel.send(file=discord.File(
                f"data{os.sep}{random.choice(['crater.png', 'autism.jpg'])}"))

        e = discord.Embed(color=find_color(message))

        if re.search("pinged", message.content, re.IGNORECASE):
            await message.channel.send(
                content="Pinged?", embed=e.set_image(url="https://i.imgur.com/LelDalN.gif"))

        elif (re.search("think", message.content, re.IGNORECASE) or
                  re.search("thonk", message.content, re.IGNORECASE) or
                      re.search("thunk", message.content, re.IGNORECASE) or
                          re.search("thenk", message.content, re.IGNORECASE) or
                              re.search("hmm", message.content, re.IGNORECASE)):
            await message.add_reaction(":thonk:468520122848509962")

        elif message.content.lower() == "k":
            await message.channel.send(
                message.author.mention + " This is an auto-response. The person you are trying "
                "to reach has no idea what \"k\" is meant to represent. They assume you wanted "
                "to type \"ok\" but could not expand the energy to type two whole letters since "
                "you were stabbed. The police have been notified.")

        elif re.search("can't", message.content, re.IGNORECASE) and re.search(
            "believe", message.content, re.IGNORECASE):
            await message.channel.send("You better believe it, scrub")

        elif message.content.lower() == "jesus":
            await message.channel.send("Christ")

        elif message.content.lower() == "good bot" or message.content.lower() == "best bot":
            async for m in message.channel.history(limit=4):
                if m.author == self.bot.user:
                    await message.channel.send("Why thank you, human!")
                    break

        elif re.search("thank you", message.content, re.IGNORECASE) or re.search(
            "thanks", message.content, re.IGNORECASE):
            async for m in message.channel.history(limit=4):
                if m.author == self.bot.user:
                    await message.channel.send("You're welcome!")
                    break

        elif message.content.lower() == "f" or re.search(
            "press f", message.content, re.IGNORECASE):
            await message.channel.send("F")

        elif message.content.lower() == "first":
            await message.channel.send("second")
            await message.channel.trigger_typing()
            await asyncio.sleep(1)
            await message.channel.send("third")
            await message.channel.trigger_typing()
            await asyncio.sleep(1)
            await message.channel.send("∞th")

        elif (re.search("frick", message.content, re.IGNORECASE) or
                  re.search("heck", message.content, re.IGNORECASE)):
            await message.channel.send(
                embed=e.set_image(url="https://i.imgur.com/hG59Noq.jpg"))

        elif (re.search("ban ", message.content, re.IGNORECASE) or
                  re.search("banned", message.content, re.IGNORECASE)):
            await message.channel.send(
                content=":b:anned", embed=e.set_image(url="https://i.imgur.com/0A6naoR.png"))


def setup(bot):
    bot.add_cog(Triggers(bot))
