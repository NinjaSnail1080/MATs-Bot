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

import re
import random

sigma_responses = ["Woah, who is that other bot? She looks g-g-gorgeous...", "D-D-Does s-s-she "
                   "have a boyf-f-friend?\nAsking for a friend!", "What a beautiful voice...",
                   "Oh, I hope she doesn't see my Playing status..."]


class Triggers:
    "Trigger words that the bot will respond to"

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.author.id == 281807963147075584:
            await message.channel.send(random.choice(sigma_responses))

        e = discord.Embed(color=mat_color)

        if re.search("pinged", message.content, re.IGNORECASE) or re.search(
            "ping me", message.content, re.IGNORECASE):
            await message.channel.send(content="Pinged?", embed=e.set_image(
                url="https://media.discordapp.net/attachments/445766533096931370/45982534883881"
                "7792/ping.gif"))

        if re.search("think", message.content, re.IGNORECASE):
            await message.channel.send(content="Thinking...", embed=e.set_image(
                url="https://cdn.discordapp.com/attachments/445766533096931370/461043390365302785"
                "/giphy.gif"))

        elif re.search("hmm", message.content, re.IGNORECASE):
            await message.channel.send(content="Hmmmmmmmmmmmmmmm...", embed=e.set_image(
                url="https://cdn.discordapp.com/attachments/445772256140984330/452538872824332299"
                "/Thonk.gif"))

        if message.content.lower() == "k":
            await message.channel.send(
                message.author.mention + " This is an auto-response. The person you are trying "
                "to reach has no idea what \"k\" is meant to represent. They assume you wanted "
                "to type \"ok\" but could not expand the energy to type two whole letters since "
                "you were stabbed. The police have been notified.")

        if re.search("can't", message.content, re.IGNORECASE) and re.search(
            "believe", message.content, re.IGNORECASE):
            await message.channel.send("You better believe it, scrub")


def setup(bot):
    bot.add_cog(Triggers(bot))
