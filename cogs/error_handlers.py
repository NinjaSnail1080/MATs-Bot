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

try:
    from mat_experimental import get_data, delete_message
except ImportError:
    from mat import get_data, delete_message

from discord.ext import commands
import discord
import asyncio

import random


class Error_Handlers:
    """Error Handlers for commands"""

    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, exception):
        exc = exception
        if str(exc) == ("Command raised an exception: Forbidden: FORBIDDEN (status code: 403): "
                        "Missing Permissions"):
            return

        elif "check functions for command" in str(exc):
            if ctx.command.cog_name == "NSFW" and not ctx.channel.is_nsfw():
                await ctx.send("This command can only be used in NSFW channels", delete_after=6.0)
                return await delete_message(ctx, 6)

            elif "disabled" in get_data("server")[str(ctx.guild.id)]:
                if ctx.command.name in get_data("server")[str(ctx.guild.id)]["disabled"]:
                    await ctx.send("Sorry, but this command has been disabled on your server "
                                   "by one of its Administrators", delete_after=7.0)
                    return await delete_message(ctx, 7)

            #! Temporary
            elif ctx.command.cog_name == "Moderation":
                await ctx.send("All Moderation commands are locked for the time being until some "
                               "bugs are fixed", delete_after=7.0)
                return await delete_message(ctx, 7)
            #! Temporary ^

        elif str(exc) == "You do not own this bot.":
            app = await self.bot.application_info()
            await ctx.send(
                f"Only my owner, **{app.owner.name}**, can use that command", delete_after=6.0)
            return await delete_message(ctx, 6)

        elif isinstance(exc, commands.CommandNotFound):
            return await ctx.message.add_reaction(random.choice(
                ["\U00002753", "\U00002754", "\U0001f615", "\U0001f937", "\U0001f645"]))

        elif (isinstance(exc, commands.BadArgument) or
                  isinstance(exc, commands.MissingRequiredArgument)):
            await ctx.send(ctx.command.brief, delete_after=15.0)
            return await delete_message(ctx, 15)

        elif isinstance(exc, commands.NoPrivateMessage):
            return await ctx.send(
                "This command cannot be used in private messages. You must be in a server")

        elif isinstance(exc, discord.Forbidden):
            return

        elif (str(exc) == "Command raised an exception: TypeError: must be str, not NoneType" and
                  ctx.command.cog_name == "Moderation"):
            #* To stop the command from raising an exception if the reason given is too long
            return

        else:
            app = await self.bot.application_info()
            return await ctx.send(
                f"```Command: {ctx.command.name}\n{exc}```An unknown error occured and I wasn't "
                "able to complete that command. Sorry!\n\nPlease get in touch with my "
                "owner, NinjaSnail1080, and tell him what happened so he can try and fix this "
                "issue. You can reach him at my support server: https://discord.gg/P4Fp3jA")


def setup(bot):
    bot.add_cog(Error_Handlers(bot))
