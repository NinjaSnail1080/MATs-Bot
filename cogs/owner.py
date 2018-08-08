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

from mat import restart_bot
from discord.ext import commands
import discord
import asyncio

import logging
import time
import os


class Owner:
    """Commands that can only be performed by the bot owner"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def armageddon(self, ctx, runtime: float=3.0):
        """Unleash hell upon a Discord server"""

        async def the_end(ctx, runtime: float):
            """Background task for armageddon command"""

            await ctx.send("This is the end")
            await asyncio.sleep(2)
            await ctx.send("The world is about to meet its demise")
            await asyncio.sleep(2)
            await ctx.send("Armageddon, Judgement Day, The Apocalypse")
            await asyncio.sleep(1.5)
            await ctx.send("It's upon us")
            await asyncio.sleep(2)
            await ctx.send("It will happen")
            await asyncio.sleep(2)
            await ctx.send("We are all going to die")
            await asyncio.sleep(2)
            await ctx.send("Goodbye, my friends")
            await asyncio.sleep(3)

            await ctx.send("T - 5")
            await asyncio.sleep(1)
            await ctx.send("4")
            await asyncio.sleep(1)
            await ctx.send("3")
            await asyncio.sleep(1)
            await ctx.send("2")
            await asyncio.sleep(1)
            await ctx.send("1")
            await asyncio.sleep(1)

            t = time.time()
            while time.time() < t + runtime:
                await ctx.send("@everyone")

        self.bot.loop.create_task(the_end(ctx, runtime * 60))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def quit(self, ctx, *, arg: str=None):
        """Quit the bot's program"""

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            print("Can't delete message in this server")
        await self.bot.wait_until_ready()

        if arg is None:
            pass
        elif arg == "-r":
            os.remove("bot.data.json")
            os.remove("server.data.json")
            os.remove("user.data.json")
        else:
            raise TypeError("\"arg\" param must be either \"-r\" or None")

        logging.info(f"Bot closed by {ctx.author.name} via \"quit\" command")
        await self.bot.logout()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx, *, arg: str=None):
        """Restart the bot's program"""

        await self.bot.change_presence(
            activity=discord.Game("Restarting..."), status=discord.Status.dnd)

        if arg is None:
            pass
        elif arg == "-r":
            os.remove("bot.data.json")
            os.remove("server.data.json")
            os.remove("user.data.json")
        else:
            raise TypeError("\"arg\" param must be either \"-r\" or None")

        await ctx.send("*Restarting*...")
        await self.bot.wait_until_ready()
        self.bot.clear()

        with open("restart", "w") as f:
            f.write(str(ctx.channel.id))

        restart_bot()

def setup(bot):
    bot.add_cog(Owner(bot))
