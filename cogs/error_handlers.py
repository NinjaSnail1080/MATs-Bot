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

from utils import delete_message, find_color, CommandDisabled, ChannelNotNSFW

from discord.ext import commands
import discord
import asyncpg

import asyncio
import random


class Error_Handlers(commands.Cog):
    """Error Handlers for commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        exc = exception
        if str(exc) == ("Command raised an exception: Forbidden: FORBIDDEN (status code: "
                        "403): Missing Permissions"):
            return

        elif str(exc) == ("Command raised an exception: NotFound: 404 NOT FOUND (error code: "
                          "10008): Unknown Message"):
            return


        elif isinstance(exc, ChannelNotNSFW):
            await ctx.send("This command can only be used in NSFW-marked channels",
                           delete_after=6.0)
            return await delete_message(ctx, 6)


        elif isinstance(exc, CommandDisabled):
            await ctx.send("Sorry, but this command has been disabled on your server by one of "
                           "its Administrators", delete_after=7.0)
            return await delete_message(ctx, 7)


        elif isinstance(exc, commands.CommandOnCooldown):
            if await self.bot.is_owner(ctx.author):
                return await ctx.reinvoke()

            c = exc.cooldown
            embed = discord.Embed(
                description="__This command is on cooldown__. Try again in **"
                            f"{round(exc.retry_after, 2)}** seconds.\n\n**Default Cooldown**: "
                            f"{c.rate} use{'' if c.rate == 1 else 's'} every {int(c.per)} "
                            f"second{'' if c.per == 1 else 's'}",
                color=find_color(ctx))
            await ctx.send(embed=embed)
            await delete_message(ctx, 15)

            #* Voting reward
            # if await self.bot.dbl.get_user_vote(ctx.author.id):
            #     await asyncio.sleep(c.per * (2/3))
            #     await ctx.reinvoke()
            return


        elif isinstance(exc, commands.NotOwner):
            await ctx.send(
                f"Only my owner, {self.bot.owner.name}, can use that command",
                delete_after=6.0)
            return await delete_message(ctx, 6)


        elif isinstance(exc, commands.BotMissingPermissions):
            if len(exc.missing_perms) == 1:
                return await ctx.send(
                    "I don't have the proper perms to perform this command. To do this, I would "
                    f"need the **{str(exc.missing_perms[0]).replace('_', ' ').title()}** "
                    "permission. Could one of you guys in charge fix that and then get "
                    "back to me?")
            else:
                m_perms = exc.missing_perms
                return await ctx.send(
                    "I don't have the proper perms to perform this command. "
                    "To do this, I would need these permissions:\n"
                    f"**{'**, **'.join(str(p).replace('_', ' ').title() for p in m_perms)}**\n"
                    "Could one of you guys in charge fix that and then get back to me?")


        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send(
                f"You need the **{str(exc.missing_perms[0]).replace('_', ' ').title()}** "
                "permission in order to use this command", delete_after=7.0)
            return await delete_message(ctx, 7)


        elif isinstance(exc, commands.CommandNotFound):
            return await ctx.message.add_reaction(random.choice(
                ["\U00002753", "\U00002754", "\U0001f615", "\U0001f937", "\U0001f645"]))


        elif (isinstance(exc, commands.BadArgument) or
                  isinstance(exc, commands.MissingRequiredArgument) or
                      isinstance(exc, commands.BadUnionArgument)):
            #* I'm using command.brief as a custom error message for each command,
            #* not as some brief help text like it's intended to be used as.
            await ctx.send(ctx.command.brief.replace("<prefix> ", ctx.prefix), delete_after=60.0)
            return await delete_message(ctx, 60)


        elif isinstance(exc, commands.NoPrivateMessage):
            return await ctx.send(
                "This command cannot be used in private messages. You must be in a server")


        elif isinstance(exc, discord.Forbidden):
            return


        elif isinstance(exc, discord.NotFound):
            return


        else:
            return await ctx.send(
                f"```Command: {ctx.command.qualified_name}\n{exc}```An unknown error occured "
                "and I wasn't able to complete that command. Sorry!\n\nPlease get in touch with "
                f"my owner, {self.bot.owner.mention}, and tell him what happened so he can try "
                "and fix this issue. You can reach him at my support server: "
                "https://discord.gg/P4Fp3jA")


def setup(bot):
    bot.add_cog(Error_Handlers(bot))
