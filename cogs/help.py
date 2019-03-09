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

from utils import find_color, get_data, delete_message

from discord.ext import commands
import discord

import collections
import asyncio
import datetime

list_prefixes = "**Prefix**: `!mat` or @mention"


def chunks(L, s):
    """Yield s-sized chunks from L"""
    for i in range(0, len(L), s):
        yield L[i:i + s]


class Help(commands.Cog, command_attrs={"hidden": True}):
    """Help commands"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command("help")

        self.back = "\U00002b05"
        self.next = "\U000027a1"

    def check_reaction(self, message):
        def check(reaction, user):
            if reaction.message.id != message.id or user == self.bot.user:
                return False
            elif reaction.emoji == self.back:
                return True
            elif reaction.emoji == self.next:
                return True
            return False
        return check

    async def send_help_embeds(self, ctx, msg, embeds):
        duration = datetime.timedelta(minutes=10) + datetime.timedelta(seconds=-9.6)
        #* A second timedelta is being added because for some reason I don't understand, there's
        #* always an offset of about 9.6 seconds (time_passed is always about -9.6 seconds on the
        #* first loop through, which makes no sense because it should pretty much 0)
        await msg.add_reaction(self.back)
        await msg.add_reaction(self.next)
        index = 0

        while True:
            time_passed = datetime.datetime.utcnow() - msg.created_at
            time_left = duration - time_passed

            if index > len(embeds) - 1 or index < -len(embeds) + 1:
                index = 0
            if index >= 0:
                page = index + 1
            elif index < 0:
                page = len(embeds) + index + 1
            await msg.edit(content=f"**Page {page}/{len(embeds)}**", embed=embeds[index])
            try:
                #* The below operation is also acting as the timer before deleting this msg,
                #* hence the "timeout=time_left.total_seconds()"
                react, user = await self.bot.wait_for(
                    "reaction_add", timeout=time_left.total_seconds(),
                    check=self.check_reaction(msg))
            except asyncio.TimeoutError:
                break
            if react.emoji == self.back:
                index -= 1
            elif react.emoji == self.next:
                index += 1
            await msg.remove_reaction(react, user)
        await msg.delete()
        return await ctx.message.delete()

    @commands.command(pass_context=True)
    async def help(self, ctx, cat=None):
        """MAT's Bot | Help command"""

        try:
            disabled = get_data("server")[str(ctx.guild.id)]["disabled"]
        except:
            disabled = []

        cmds = collections.Counter()
        for c in self.bot.commands:
            if not c.hidden and c.name not in disabled:
                cmds[c.cog_name] += 1

        if cat is None:
            embed = discord.Embed(
                title="MAT's Bot | Help command", description=list_prefixes + "\n**Categories**:",
                color=find_color(ctx))

            embed.add_field(
                name="<:confetti:464831811558572035> Fun", value=f"{cmds['Fun']} "
                "commands\n`<prefix> help fun` for more info")
            embed.add_field(
                name="<:paint:464836778000515072> Image Manipulation", value=f"{cmds['Image']} "
                "commands\n`<prefix> help image` for more info")
            embed.add_field(
                name="<:info:540301057264189453> Info", value=f"{cmds['Info']} commands"
                "\n`<prefix> help info` for more info")
            embed.add_field(
                name="<:raisedfist:470319397291163678> Moderation",
                value=f"{cmds['Moderation']} commands\n`<prefix> help mod` for more info")
            embed.add_field(
                name=":wink: NSFW", value=f"{cmds['NSFW']} commands\n`<prefix> help nsfw` "
                "for more info")
            embed.add_field(
                name=":tools: Utility", value=f"{cmds['Utility']} commands\n`<prefix> "
                "help nsfw` for more info")
            if disabled:
                embed.add_field(name=":no_entry_sign: Disabled Commands",
                                value=f"`{'`, `'.join(disabled)}`", inline=False)
            embed.set_footer(text="Do \"<prefix> help all\" for a list of all of my commands")

            await ctx.send(
                content="I'm still in beta, so many more commands are coming in the near future!",
                embed=embed)

        elif cat.lower() == "fun":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Fun" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if len(cmds) == 0:
                embed = discord.Embed(
                    title="Help | Fun Commands", description=list_prefixes + "\n\n**All commands"
                    " in this category have been disabled for this server by one of its "
                    "Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Fun Commands", description=list_prefixes, color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted after "
                        "10 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            msg = await ctx.send(embed=embeds[0])
            return await self.send_help_embeds(ctx, msg, embeds)

        elif cat.lower() == "image":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Image" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if len(cmds) == 0:
                embed = discord.Embed(
                    title="Help | Image Manipulation Commands",
                    description=list_prefixes + "\n\n**All commands in this category have been "
                    "disabled for this server by one of its Administrators**",
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Image Manipulation Commands",
                    description=list_prefixes + "\n\n**For all of these commands you need to "
                    "either attach an image, insert an image url, or @mention another user "
                    "after the command to use their avatar. If you don't put anything, I'll "
                    "search the previous 10 messages for an image and use it if I find one. If "
                    "I don't, I'll just default to your user's avatar**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted after "
                        "10 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            msg = await ctx.send(embed=embeds[0])
            return await self.send_help_embeds(ctx, msg, embeds)

        elif cat.lower() == "info":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Info" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if len(cmds) == 0:
                embed = discord.Embed(
                    title="Help | Information Commands", description=list_prefixes + "\n\n**All "
                    "commands in this category have been disabled for this server by one of "
                    "its Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Information Commands", description=list_prefixes,
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted after "
                        "10 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            msg = await ctx.send(embed=embeds[0])
            return await self.send_help_embeds(ctx, msg, embeds)

        elif cat.lower() == "mod" or cat.lower() == "moderation":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Moderation" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)
            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Moderation Commands", description=list_prefixes,
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted after "
                        "10 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            msg = await ctx.send(embed=embeds[0])
            return await self.send_help_embeds(ctx, msg, embeds)

        elif cat.lower() == "music":
            await ctx.send("No commands yet ¯\_(ツ)_/¯")

        elif cat.lower() == "utility":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Utility" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if len(cmds) == 0:
                embed = discord.Embed(
                    title="Help | Utility Commands", description=list_prefixes + "\n\n**All "
                    "commands in this category have been disabled for this server by one of "
                    "its Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Utility Commands", description=list_prefixes,
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted after "
                        "10 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            msg = await ctx.send(embed=embeds[0])
            return await self.send_help_embeds(ctx, msg, embeds)

        elif cat.lower() == "nsfw":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "NSFW" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if len(cmds) == 0:
                embed = discord.Embed(
                    title="Help | NSFW Commands", description=list_prefixes + "\n\n**All commands"
                    " in this category have been disabled for this server by one of its "
                    "Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | NSFW Commands", description=list_prefixes,
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted after "
                        "10 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            msg = await ctx.send(embed=embeds[0])
            return await self.send_help_embeds(ctx, msg, embeds)

        elif cat.lower() == "all":
            cmds = sorted(list(self.bot.commands), key=lambda c: c.name)

            embed = discord.Embed(
                title="Help | All Commands", description=list_prefixes, color=find_color(ctx))
            embed.set_author(name="MAT's Bot")
            embed.set_footer(
                text="Do \"<prefix> help <command name>\" for help on a specific command")

            embed.add_field(
                name="<:confetti:464831811558572035> Fun",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in cmds
                                            if c.cog_name == "Fun" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name="<:paint:464836778000515072> Image Manipulation",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in cmds
                                            if c.cog_name == "Image" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name="<:info:540301057264189453> Info",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in cmds
                                            if c.cog_name == "Info" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name="<:raisedfist:470319397291163678> Moderation",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in cmds
                                            if c.cog_name == "Moderation" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name=":wink: NSFW",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in cmds
                                            if c.cog_name == "NSFW" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name=":tools: Utility",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in cmds
                                            if c.cog_name == "Utility" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            if disabled:
                embed.add_field(name=":no_entry_sign: Disabled Commands",
                                value=f"`{'`, `'.join(disabled)}`", inline=False)
            await ctx.send(
                content="I'm still in beta, so many more commands are coming in the near future!",
                embed=embed)

        else:
            for cmd in self.bot.commands:
                if cat.lower() == cmd.name:
                    embed = discord.Embed(
                        title=f"Help | {cmd.name} Command", description=cmd.help,
                        color=find_color(ctx))
                    embed.set_author(name="MAT's Bot")

                    if cmd.aliases:
                        embed.add_field(name="Aliases", value=f"`{'`, `'.join(cmd.aliases)}`")

                    await ctx.send(embed=embed)
                    return

            await ctx.send(
                "That's not a category. The ones you can pick are:\n\n`fun` (Fun commands)\n"
                "`image` (Image Manipulation commands)\n`info` (Information commands)\n`mod` "
                "(Moderation commands)\n`nsfw` (NSFW commands)\n`utility` (Utility commands)\n\n"
                "You can also put the name of a command for help on that command only")


def setup(bot):
    bot.add_cog(Help(bot))

