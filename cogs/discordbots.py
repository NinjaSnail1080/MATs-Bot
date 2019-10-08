"""
    MAT's Bot: An open-source, general purpose Discord bot written in Python.
    Copyright (C) 2018  NinjaSnail1080  (Discord Username: @NinjaSnail1080#8581)

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
import dbl

import config


class DiscordBotsAPI(commands.Cog):
    """Handles interactions with the discordbots.org OR top.gg API"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.dbl = dbl.Client(self.bot,
                                  config.DBL_TOKEN,
                                  session=self.bot.session,
                                  autopost=True)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.dbl.post_guild_count()

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        #TODO: Eventually this will contain economy stuff
        pass


def setup(bot):
    bot.add_cog(DiscordBotsAPI(bot))
