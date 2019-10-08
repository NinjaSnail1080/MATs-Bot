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

from utils import delete_message, find_color, CommandDisabled, ChannelNotNSFW, VoteRequired, MusicCheckFailure

from discord.ext import commands
import discord

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


        elif isinstance(exc, VoteRequired):
            embed = discord.Embed(
                title="\U0001f44d Remember to vote!",
                description="Voting is required to use this command. On top of that, voting will "
                            "also allow you to have shorter command cooldowns. You can vote by "
                            "[clicking here](https://discordbots.org/bot/459559711210078209/vote)",
                url="https://discordbots.org/bot/459559711210078209/vote",
                color=find_color(ctx))
            await ctx.send(embed=embed, delete_after=45.0)
            return await delete_message(ctx, 45)


        elif isinstance(exc, commands.CommandOnCooldown):
            c = exc.cooldown
            retry_after = exc.retry_after

            if await self.bot.is_owner(ctx.author):
                return await ctx.reinvoke()

            #* Voting reward
            if await self.bot.dbl.get_user_vote(ctx.author.id):
                if c.per - exc.retry_after >= c.per * (2/3):
                    return ctx.reinvoke()
                retry_after = (c.per * (2/3)) - (c.per - exc.retry_after)

            embed = discord.Embed(
                title="This command is on cooldown",
                description=f"Try again in **{round(retry_after, 2)}** seconds.\n\n**Default "
                            f"Cooldown**: {c.rate} use{'' if c.rate == 1 else 's'} every "
                            f"{int(c.per)} second{'' if c.per == 1 else 's'}\n**[Voter](https://"
                            f"discordbots.org/bot/459559711210078209/vote) Cooldown**: {c.rate} "
                            f"use{'' if c.rate == 1 else 's'} every {int(c.per * (2/3))} "
                            f"second{'' if c.per == 1 else 's'}",
                color=find_color(ctx))
            #*Voting reward
            if await self.bot.dbl.get_user_vote(ctx.author.id):
                embed.set_footer(text=f"{ctx.author.display_name} has voted for MAT's Bot, so "
                                      "they get shorter cooldowns",
                                 icon_url=ctx.author.avatar_url)
            else:
                embed.set_footer(
                    text="Vote for MAT's Bot using the link above to get shorter cooldowns")
            await ctx.send(embed=embed, delete_after=30)
            await delete_message(ctx, 30)

            #* Voting reward
            if await self.bot.dbl.get_user_vote(ctx.author.id):
                await asyncio.sleep(c.per * (2/3))
                ctx.command.reset_cooldown(ctx)
            return


        elif isinstance(exc, commands.NotOwner):
            await ctx.send(
                f"Only my owner, {self.bot.owner}, can use that command",
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


        elif isinstance(exc, MusicCheckFailure):
            return


        elif isinstance(exc, discord.Forbidden):
            return


        elif isinstance(exc, discord.NotFound):
            return


        else:
            return await ctx.send(
                f"```Command: {ctx.command.qualified_name}\n{exc}```An unknown error occured "
                "and I wasn't able to complete that command. Sorry!\n\nPlease get in touch with "
                f"my owner, **{self.bot.owner}**, and tell him what happened so he can try "
                "and fix this issue. You can reach him at my support server: "
                "https://discord.gg/khGGxxj")


def setup(bot):
    bot.add_cog(Error_Handlers(bot))
