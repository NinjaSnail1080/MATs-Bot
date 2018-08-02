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
import discord
import validators


class Music:
    """Play some music"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, audio=None):
        """Play something in a voice channel (Heavy WIP, can only accept YouTube links for now)"""
        #TODO: Make this work!

        if validators.url(audio) or audio is not None:
            if ctx.author.voice is not None:
                voice = ctx.author.voice.channel
                vc = await voice.connect()

                # player = await vc.create_ytdl_player(audio)
                # player.start()
            else:
                await ctx.send("You must be in a voice channel to use that command")
        else:
            await ctx.send("Unfortunately, this command only accepts YouTube links right now. "
                           "It's a heavy WIP")


def setup(bot):
    bot.add_cog(Music(bot))
