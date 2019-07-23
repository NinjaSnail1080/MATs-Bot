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

from utils import delete_message

from discord.ext import commands
import discord

import asyncio
import time
import os
import pprint


class Owner(commands.Cog, command_attrs={"hidden": True}):
    """Commands that can only be performed by the bot owner"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not await self.bot.is_owner(ctx.author):
            raise commands.NotOwner
        return True

    @commands.command()
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

    @commands.command()
    async def deletemsg(self, ctx, msgs: commands.Greedy[discord.Message]):
        """Delete a message or messages (intended to be used in DM channels)"""

        for msg in msgs:
            await msg.delete()
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    @commands.command()
    async def execute(self, ctx, *, query):
        """Execute a query in the database"""

        try:
            with ctx.channel.typing():
                async with self.bot.pool.acquire() as conn:
                    result = await conn.execute(query)
            await ctx.send(f"Query complete:```{result}```")
        except Exception as e:
            await ctx.send(f"Query failed:```{e}```")

    @commands.command()
    async def fetch(self, ctx, *, query):
        """Run a query in the database and fetch the result"""

        try:
            with ctx.channel.typing():
                async with self.bot.pool.acquire() as conn:
                    result = await conn.fetch(query)

            fmtd_result = pprint.pformat([dict(i) for i in result])
            await ctx.send(f"Query complete:```{fmtd_result}```")
        except Exception as e:
            await ctx.send(f"Query failed:```{e}```")

    @commands.command()
    async def quit(self, ctx):
        """Quit the bot's program"""

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            print("\n\nClosing...\n")

            for task in asyncio.all_tasks(self.bot.loop):
                task.cancel()
                print("Cancelled task: " + str(task._coro))

            print("\nLogging out...")
            await self.bot.logout()
        finally:
            await self.bot.pool.close()
            await self.bot.session.close()
            self.bot.loop.close()
            print("\nClosed\n")

    @commands.command()
    async def reload(self, ctx, *, cog=None):
        """Reload one or all of MAT's cogs"""

        try:
            if cog is None:
                for extension in self.bot.extensions.keys():
                    self.bot.reload_extension(extension)
                await ctx.send(f"Reloaded all cogs", delete_after=5.0)
                return await delete_message(ctx, 5.0)
            else:
                self.bot.reload_extension("cogs." + cog.lower())
                await ctx.send(f"Reloaded `{cog.capitalize()}`", delete_after=5.0)
                return await delete_message(ctx, 5.0)
        except:
            await ctx.send("Invalid cog name", delete_after=5.0)
            return await delete_message(ctx, 5)


def setup(bot):
    bot.add_cog(Owner(bot))
