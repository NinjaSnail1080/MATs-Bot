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
import asyncio

import random
import datetime


class Error_Handlers:
    """Error Handlers for commands"""

    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, exception):
        exc = exception
        if str(exc) == ("Command raised an exception: Forbidden: FORBIDDEN (status code: 403): "
                        "Missing Permissions"):
            return
        elif "The check functions for command" in str(exc):
            return await ctx.send("This command can only be used in NSFW channels")
        elif str(exc) == "You do not own this bot.":
            app = await self.bot.application_info()
            return await ctx.send(f"Only my owner, **{app.owner.name}**, can use that command")
        elif isinstance(exc, commands.CommandNotFound):
            return await ctx.message.add_reaction(random.choice(
                ["\U00002753", "\U00002754", "\U0001f615", "\U0001f937", "\U0001f645"]))
        elif isinstance(exc, commands.BadArgument):
            await ctx.send(ctx.command.brief, delete_after=15.0)
            await asyncio.sleep(15)
            try:
                await ctx.message.delete()
            except: pass
            return
        # elif isinstance(exc, commands.NoPrivateMessage):
            # return await ctx.send(
                # "This command cannot be used in private messages", delete_after=5.0)
        elif isinstance(exc, discord.Forbidden):
            return
        elif isinstance(exc, commands.MissingRequiredArgument):
            return
        else:
            print("This exception was raised on %s:\n\n%s\n\n" %
                  (datetime.datetime.now().strftime("%b %-d, %Y at %X"), exc))
            app = await self.bot.application_info()
            await ctx.send(
                "```%s```An unknown error occured and I wasn't able to complete that "
                "command. Sorry!\n\nPlease get in touch with my owner, %s, and tell him what "
                "happened so he can try and fix this issue. You can reach him at my support "
                "server: https://discord.gg/zQjtXVm" % (exc, app.owner.name))


def setup(bot):
    bot.add_cog(Error_Handlers(bot))
