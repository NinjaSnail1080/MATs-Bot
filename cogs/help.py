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
    from mat_experimental import find_color, get_data, delete_message
except ImportError:
    from mat import find_color, get_data, delete_message

from discord.ext import commands
import discord

import collections

# list_prefixes = "**Prefixes**: `" + "` | `".join()) + "`"
list_prefixes = "**Prefixes**: `!mat` | `mat.` | `mat/`"


def chunks(l, s):
    """Yield s-sized chunks from l"""
    for i in range(0, len(l), s):
        yield l[i:i + s]


class Help:
    """Help commands"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.remove_command("help")

    @commands.command()
    async def help(self, ctx, cat=None):
        """MAT's Bot | Help command"""

        try:
            if "disabled" in get_data("server")[str(ctx.guild.id)]:
                disabled = get_data("server")[str(ctx.guild.id)]["disabled"]
            else:
                disabled = []
        except AttributeError:
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
                name="<:info:464831966382915584> Info", value=f"{cmds['Info']} commands"
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

            cmds = list(c for c in self.bot.commands if c.cog_name == "Fun" and not c.hidden and
                        c.name not in disabled)
            cmds = list(chunks(cmds, 25))

            embed = discord.Embed(
                title="Help | Fun Commands", description=list_prefixes, color=find_color(ctx))
            embed.set_author(name="MAT's Bot")

            for c in cmds[0]:
                embed.add_field(name=c.name, value=c.help, inline=False)

            extra_embeds = []
            if len(cmds) > 1:
                for i in cmds[1:]:
                    e = discord.Embed(color=find_color(ctx))
                    for c in i:
                        e.add_field(name=c.name, value=c.help, inline=False)
                    extra_embeds.append(e)

            await ctx.send(embed=embed)
            for e in extra_embeds:
                await ctx.send(embed=e)

        elif cat.lower() == "image":
            cmds = list(c for c in self.bot.commands if c.cog_name == "Image" and
                        not c.hidden and c.name not in disabled)
            cmds = list(chunks(cmds, 25))

            embed = discord.Embed(title="Help | Image Manipulation Commands",
                                  description=list_prefixes + "\n\n**For all of these commands "
                                  "you need to either attach an image or @mention another user "
                                  "after the command to use their avatar. If you don't, I'll "
                                  "default to your user and your avatar**", color=find_color(ctx))
            embed.set_author(name="MAT's Bot")

            for c in cmds[0]:
                embed.add_field(name=c.name, value=c.help, inline=False)

            extra_embeds = []
            if len(cmds) > 1:
                for i in cmds[1:]:
                    e = discord.Embed(color=find_color(ctx))
                    for c in i:
                        e.add_field(name=c.name, value=c.help, inline=False)
                    extra_embeds.append(e)

            await ctx.send(embed=embed)
            for e in extra_embeds:
                await ctx.send(embed=e)

        elif cat.lower() == "info":
            cmds = list(c for c in self.bot.commands if c.cog_name == "Info" and not c.hidden and
                        c.name not in disabled)
            cmds = list(chunks(cmds, 25))

            embed = discord.Embed(title="Help | Information Commands", description=list_prefixes,
                                  color=find_color(ctx))
            embed.set_author(name="MAT's Bot")

            for c in cmds[0]:
                embed.add_field(name=c.name, value=c.help, inline=False)

            extra_embeds = []
            if len(cmds) > 1:
                for i in cmds[1:]:
                    e = discord.Embed(color=find_color(ctx))
                    for c in i:
                        e.add_field(name=c.name, value=c.help, inline=False)
                    extra_embeds.append(e)

            await ctx.send(embed=embed)
            for e in extra_embeds:
                await ctx.send(embed=e)

        elif cat.lower() == "mod" or cat.lower() == "moderation":
            cmds = list(
                c for c in self.bot.commands if c.cog_name == "Moderation" and not c.hidden and
                c.name not in disabled)
            cmds = list(chunks(cmds, 25))

            embed = discord.Embed(title="Help | Moderation Commands", description=list_prefixes,
                                  color=find_color(ctx))
            embed.set_author(name="MAT's Bot")

            for c in cmds[0]:
                embed.add_field(name=c.name, value=c.help, inline=False)

            extra_embeds = []
            if len(cmds) > 1:
                for i in cmds[1:]:
                    e = discord.Embed(color=find_color(ctx))
                    for c in i:
                        e.add_field(name=c.name, value=c.help, inline=False)
                    extra_embeds.append(e)

            await ctx.send(embed=embed)
            for e in extra_embeds:
                await ctx.send(embed=e)

        elif cat.lower() == "music":
            await ctx.send("No commands yet ¯\_(ツ)_/¯")

        elif cat.lower() == "utility":
            cmds = list(c for c in self.bot.commands if c.cog_name == "Utility" and
                        not c.hidden and c.name not in disabled)
            cmds = list(chunks(cmds, 25))

            embed = discord.Embed(
                title="Help | Utility Commands", description=list_prefixes, color=find_color(ctx))
            embed.set_author(name="MAT's Bot")

            for c in cmds[0]:
                embed.add_field(name=c.name, value=c.help, inline=False)

            extra_embeds = []
            if len(cmds) > 1:
                for i in cmds[1:]:
                    e = discord.Embed(color=find_color(ctx))
                    for c in i:
                        e.add_field(name=c.name, value=c.help, inline=False)
                    extra_embeds.append(e)

            await ctx.send(embed=embed)
            for e in extra_embeds:
                await ctx.send(embed=e)

        elif cat.lower() == "nsfw":
            cmds = list(c for c in self.bot.commands if c.cog_name == "NSFW" and not c.hidden and
                        c.name not in disabled)

            if len(cmds) == 0:
                embed = discord.Embed(
                    title="Help | NSFW Commands", description=list_prefixes + "\n\n**All commands"
                    " in this category have been disabled for this server by one of its "
                    "Administrators**", color=find_color(ctx))
                embed.set_author(name="MAT's Bot")
                return await ctx.send(embed=embed)

            cmds = list(chunks(cmds, 25))

            embed = discord.Embed(
                title="Help | NSFW Commands", description=list_prefixes, color=find_color(ctx))
            embed.set_author(name="MAT's Bot")

            for c in cmds[0]:
                embed.add_field(name=c.name, value=c.help, inline=False)

            extra_embeds = []
            if len(cmds) > 1:
                for i in cmds[1:]:
                    e = discord.Embed(color=find_color(ctx))
                    for c in i:
                        e.add_field(name=c.name, value=c.help, inline=False)
                    extra_embeds.append(e)

            await ctx.send(embed=embed)
            for e in extra_embeds:
                await ctx.send(embed=e)

        elif cat.lower() == "all":
            embed = discord.Embed(
                title="Help | All Commands", description=list_prefixes, color=find_color(ctx))
            embed.set_author(name="MAT's Bot")
            embed.set_footer(
                text="Do \"<prefix> help <command name>\" for help on a specific command")

            embed.add_field(
                name="<:confetti:464831811558572035> Fun",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in self.bot.commands
                                            if c.cog_name == "Fun" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name="<:paint:464836778000515072> Image Manipulation",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in self.bot.commands
                                            if c.cog_name == "Image" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name="<:info:464831966382915584> Info",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in self.bot.commands
                                            if c.cog_name == "Info" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name="<:raisedfist:470319397291163678> Moderation",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in self.bot.commands
                                 if c.cog_name == "Moderation" and not c.hidden
                                 and c.name not in disabled]), inline=False)
            embed.add_field(
                name=":wink: NSFW",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in self.bot.commands
                                            if c.cog_name == "NSFW" and not c.hidden
                                            and c.name not in disabled]), inline=False)
            embed.add_field(
                name=":tools: Utility",
                value="\u200b" + ", ".join([f"`{c.name}`" for c in self.bot.commands
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
                        embed.add_field(name="Aliases", value=f"`{', '.join(cmd.aliases)}`")

                    await ctx.send(embed=embed)
                    return

            await ctx.send(
                "That's not a category. The ones you can pick are:\n\n`fun` (Fun commands)\n"
                "`image` (Image Manipulation commands)\n`info` (Information commands)\n`mod` "
                "(Moderation commands)\n`nsfw` (NSFW commands)\n`utility` (Utility commands)\n\n"
                "You can also put the name of a command for help on that command only")


def setup(bot):
    bot.add_cog(Help(bot))

