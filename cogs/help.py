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

from utils import find_color, delete_message, chunks, send_basic_paginator

from discord.ext import commands
import discord

import collections
import asyncio
import datetime
import random


class Help(commands.Cog):
    """Help commands"""

    def __init__(self, bot):
        self.bot = bot

    def show_info(self, ctx, show_detail=False):
        all_prefixes = self.bot.default_prefixes.copy()

        default_prefixes = []
        for p in self.bot.default_prefixes:
            if p.endswith(" ") and show_detail:
                default_prefixes.append(f"*`{p}`")
            else:
                default_prefixes.append(f"`{p}`")

        custom_prefixes = []
        if ctx.guild is not None:
            all_prefixes += self.bot.guilddata[ctx.guild.id]["prefixes"]
            for p in self.bot.guilddata[ctx.guild.id]["prefixes"]:
                if p.endswith(" ") and show_detail:
                    custom_prefixes.append(f"*`{p}`")
                else:
                    custom_prefixes.append(f"`{p}`")

        msg = f"**Prefixes**: {', '.join(default_prefixes)} __or__ {self.bot.user.mention}"
        if custom_prefixes:
            msg += f"\n**Server-Specific Prefix(es)**: {', '.join(custom_prefixes)}"

        if show_detail:
            msg += ("\n\nYou must use one of the prefixes before each command in your message."
                    f"\n__Example__: `{random.choice(all_prefixes)}"
                    f"{random.choice([c.name for c in self.bot.commands if not c.hidden])} <any "
                    "other required specs>`\n\n*An asterisk* (*) *next to a prefix listed above "
                    "means there must be a space in between the prefix and the command*")

        msg += ("\n\nIf you're having problems or want to give feedback, you can join my "
                "[support server](https://discord.gg/khGGxxj).\n[Vote for me](https://discordbots"
                ".org/bot/459559711210078209/vote) and get special privileges, like shorter "
                "command cooldowns.\nInvite me to other servers [here](https://discordapp.com/o"
                "auth2/authorize?client_id=459559711210078209&scope=bot&permissions=2146958591).")

        return msg

    @commands.command()
    async def help(self, ctx, cat=None):
        """MAT's Bot | Help command"""

        await ctx.channel.trigger_typing()
        if ctx.guild is not None:
            disabled = self.bot.guilddata[ctx.guild.id]["disabled"]
        else:
            disabled = []

        cog_cmds = collections.Counter()
        for c in self.bot.commands:
            if not c.hidden and c.name not in disabled:
                cog_cmds[c.cog_name] += 1

        if cat is None:
            embed = discord.Embed(
                title="MAT's Bot | Help command",
                description=self.show_info(ctx, True) + "\n\n__**Categories**__:",
                color=find_color(ctx))

            embed.add_field(
                name="<:confetti:464831811558572035> Fun", value=f"{cog_cmds['Fun']} "
                "commands\n`<prefix> help fun` for more info")
            embed.add_field(
                name="<:paint:464836778000515072> Image Manipulation",
                value=f"{cog_cmds['Image']} commands\n`<prefix> help image` for more info")
            embed.add_field(
                name="<:info:540301057264189453> Info", value=f"{cog_cmds['Info']} commands"
                "\n`<prefix> help info` for more info")
            embed.add_field(
                name="<:raisedfist:470319397291163678> Moderation",
                value=f"{cog_cmds['Moderation']} commands\n`<prefix> help mod` for more info")
            embed.add_field(
                name=":wink: NSFW", value=f"{cog_cmds['NSFW']} commands\n`<prefix> help nsfw` "
                "for more info")
            embed.add_field(
                name=":tools: Utility", value=f"{cog_cmds['Utility']} commands\n`<prefix> "
                "help utility` for more info")
            if disabled:
                embed.add_field(name=":no_entry_sign: Disabled Commands",
                                value=f"`{'`, `'.join(disabled)}`", inline=False)
            embed.set_footer(text="Do \"<prefix> help all\" for a list of all of my commands")

            await ctx.send(embed=embed)

        elif cat.lower() == "economy":
            await ctx.send("No commands yet ¯\_(ツ)_/¯")

        elif cat.lower() == "fun":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Fun" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if not cmds:
                embed = discord.Embed(
                    title="Help | Fun Commands", description=self.show_info(ctx) + "\n\n**All "
                    "commands in this category have been disabled for this server by one of its "
                    "Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 8))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Fun Commands",
                    description=f"**Page {cmds.index(i) + 1}/{len(cmds)}** "
                    f"({cog_cmds['Fun']} commands)\n\n" + self.show_info(ctx),
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted if it's "
                        "left idle for longer than 5 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            return await send_basic_paginator(ctx, embeds, 5)

        elif cat.lower() == "image":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Image" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if not cmds:
                embed = discord.Embed(
                    title="Help | Image Manipulation Commands",
                    description=self.show_info(ctx) + "\n\n**All commands in this category "
                    "have been disabled for this server by one of its Administrators**",
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 8))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Image Manipulation Commands",
                    description=f"**Page {cmds.index(i) + 1}/{len(cmds)}** "
                    f"({cog_cmds['Image']} commands)\n\n" + self.show_info(ctx) + "\n\n**For all "
                    "of these commands you need to either attach an image, insert an image url, "
                    "or @mention another user after the command to use their avatar. If you "
                    "don't put anything, I'll search the previous 10 messages for an image and "
                    "use it if I find one. If I don't, I'll just default to your user's avatar**",
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted if it's "
                        "left idle for longer than 5 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            return await send_basic_paginator(ctx, embeds, 5)

        elif cat.lower() == "info" or cat.lower() == "information":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Info" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if not cmds:
                embed = discord.Embed(
                    title="Help | Information Commands", description=self.show_info(ctx) +
                    "\n\n**All commands in this category have been disabled for this server by "
                    "one of its Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 7))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Information Commands",
                    description=f"**Page {cmds.index(i) + 1}/{len(cmds)}** "
                    f"({cog_cmds['Info']} commands)\n\n" + self.show_info(ctx),
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted if it's "
                        "left idle for longer than 5 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            return await send_basic_paginator(ctx, embeds, 5)

        elif cat.lower() == "mod" or cat.lower() == "moderation":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Moderation" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)
            cmds = list(chunks(cmds, 5))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Moderation Commands",
                    description=f"**Page {cmds.index(i) + 1}/{len(cmds)}** "
                    f"({cog_cmds['Moderation']} commands)\n\n" + self.show_info(ctx),
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted if it's "
                        "left idle for longer than 5 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            return await send_basic_paginator(ctx, embeds, 5)

        elif cat.lower() == "music":
            await ctx.send("No commands yet ¯\_(ツ)_/¯")

        elif cat.lower() == "utility":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "Utility" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if not cmds:
                embed = discord.Embed(
                    title="Help | Utility Commands", description=self.show_info(ctx) +
                    "\n\n**All commands in this category have been disabled for this server by "
                    "one of its Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 8))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | Utility Commands",
                    description=f"**Page {cmds.index(i) + 1}/{len(cmds)}** "
                    f"({cog_cmds['Utility']} commands)\n\n" + self.show_info(ctx),
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted if it's "
                        "left idle for longer than 5 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            return await send_basic_paginator(ctx, embeds, 5)

        elif cat.lower() == "nsfw":
            cmds = sorted(list(c for c in self.bot.commands if c.cog_name == "NSFW" and
                               not c.hidden and c.name not in disabled), key=lambda c: c.name)

            if not cmds:
                embed = discord.Embed(
                    title="Help | NSFW Commands", description=self.show_info(ctx) + "\n\n**"
                    "All commands in this category have been disabled for this server by one of "
                    "its Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 8))

            embeds = []
            for i in cmds:
                embed = discord.Embed(
                    title="Help | NSFW Commands",
                    description=f"**Page {cmds.index(i) + 1}/{len(cmds)}** "
                    f"({cog_cmds['NSFW']} commands)\n\n" + self.show_info(ctx),
                    color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                if len(cmds) > 1:
                    embed.set_footer(
                        text=f"Click one of the emojis below to go to the next page or the "
                        "previous one. This help message will be automatically deleted if it's "
                        "left idle for longer than 5 minutes")
                for c in i:
                    embed.add_field(name=c.name, value=c.help, inline=False)
                embeds.append(embed)

            return await send_basic_paginator(ctx, embeds, 5)

        elif cat.lower() == "all":
            cmds = sorted(list(self.bot.commands), key=lambda c: c.name)

            embed = discord.Embed(
                title="Help | All Commands", description=self.show_info(ctx),
                color=find_color(ctx))
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
            await ctx.send(embed=embed)

        else:
            for cmd in self.bot.commands:
                if cat.lower() == cmd.name:
                    embed = discord.Embed(
                        title=f"Help | {cmd.name} Command",
                        description=cmd.help.replace("<prefix> ", ctx.prefix),
                        color=find_color(ctx))
                    embed.set_author(name="MAT's Bot")

                    if cmd.aliases:
                        embed.add_field(name="Aliases", value=f"`{'`, `'.join(cmd.aliases)}`")

                    return await ctx.send(embed=embed)

            await ctx.send(
                "That's not a category. The ones you can pick are:\n\n`fun` (Fun commands)\n"
                "`image` (Image Manipulation commands)\n`info` (Information commands)\n`mod` "
                "(Moderation commands)\n`nsfw` (NSFW commands)\n`utility` (Utility commands)\n\n"
                "You can also put the name of a command for help on that command only")


def setup(bot):
    bot.add_cog(Help(bot))

