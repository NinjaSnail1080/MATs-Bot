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

from utils import find_color, get_data, dump_data, delete_message

from discord.ext import commands
import discord
import pytimeparse
import aiohttp
import rapidjson as json

import re
import random
import asyncio
import collections
import typing
import datetime
import time
import string


async def send_log(guild, send_embed):
    """Creates a #logs channel if it doesn't already exist so people can keep track of what the
    mods are doing. Then send the embed from a moderation command
    """
    serverdata = get_data("server")
    if "logs" not in serverdata[str(guild.id)]:
        logs = await guild.create_text_channel(
            "logs", overwrites={guild.default_role: discord.PermissionOverwrite(
                send_messages=False)})
        await logs.send("I created this channel just now to keep a log of all my moderation "
                        "commands that have been used. Feel free to edit this channel "
                        "however you'd like, but make sure I always have access to it!"
                        "\n\nP.S. I don't have to use this channel if you don't want me to. You "
                        "can use the `setlogs` command to set a different logs channel or "
                        "the `nologs` command to disable logging moderation commands entirely.")
        serverdata[str(guild.id)]["logs"] = str(logs.id)
        dump_data(serverdata, "server")
    elif serverdata[str(guild.id)]["logs"] == "false":
        return
    else:
        logs = guild.get_channel(int(serverdata[str(guild.id)]["logs"]))

    await logs.send(embed=send_embed)


class Moderation(commands.Cog):
    """Moderation tools"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(self.check_giveaways())

    @commands.Cog.listener()
    async def on_message(self, message):
        #TODO: Eventually this will contain the antispam and antiraid features
        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        #* This function checks if a giveaway is cancelled by its creator
        if reaction.emoji == "\U0001f6d1":
            giveaways = get_data("giveaways")
            if (not any(int(g.get("msg", None)) == reaction.message.id for g in giveaways) or
                    not any(int(g.get("author", None)) == user.id for g in giveaways)):
                return
            for g in giveaways.copy():
                if g["msg"] == str(reaction.message.id):
                    giveaways.remove(g)
                    dump_data(giveaways, "giveaways")
                    embed = discord.Embed(
                        description=f"{user.mention}'s giveaway for the prize, **{g['prize']}** "
                        "has been cancelled", color=reaction.message.guild.me.color)
                    await reaction.message.clear_reactions()
                    return await reaction.message.edit(embed=embed)

    async def check_giveaways(self):
        while True:
            giveaways = get_data("giveaways")
            for g in giveaways.copy():
                if datetime.datetime.utcnow() >= datetime.datetime.fromtimestamp(
                    float(g["end_time"])):

                    try:
                        channel = self.bot.get_channel(int(g["channel"]))
                        msg = await channel.get_message(int(g["msg"]))
                        author = channel.guild.get_member(int(g["author"]))
                        blacklist = g["blacklist"]
                        num_winners = int(g["winners"])
                        prize = g["prize"]
                    except:
                        giveaways.remove(g)
                        dump_data(giveaways, "giveaways")
                        continue

                    for r in msg.reactions:
                        if r.emoji == "\U0001f3ab":
                            pool = await r.users().flatten()
                    for m in pool.copy():
                        if m.bot or str(m.id) in blacklist:
                            pool.remove(m)

                    try:
                        winners = random.sample(pool, num_winners)
                    except ValueError:
                        await channel.send(f"{author.mention}'s giveaway is over and not enough "
                                           f"people entered. This means nobody won **{prize}**")
                        embed = discord.Embed(
                            description=f"Nobody won **{prize}** in this giveaway",
                            timestamp=datetime.datetime.utcnow(),
                            color=channel.guild.me.color)
                        embed.set_author(name=f"{author.name}'s giveaway is over!",
                                         icon_url=author.avatar_url)
                        embed.set_footer(text="This giveaway ended:")
                        await msg.clear_reactions()
                        await msg.edit(embed=embed)
                        giveaways.remove(g)
                        dump_data(giveaways, "giveaways")
                        continue

                    for w in winners:
                        await w.send(f"\U0001f3c6 You just won **{prize}** in {author.mention}'s "
                                     f"giveaway in the server, __{msg.guild.name}__! \U0001f3c6")

                    if len(winners) == 1:
                        embed = discord.Embed(
                            description="\U0001f31f \U00002b50 Congratulations to "
                            f"{winners[0].mention}, who won **{prize}**! \U00002b50 \U0001f31f",
                            timestamp=datetime.datetime.utcnow(), color=channel.guild.me.color)
                    else:
                        embed = discord.Embed(
                            description=f"\U0001f31f \U00002b50 Congratulations to the "
                            f"{num_winners} winners of **{prize}**! \U00002b50 \U0001f31f",
                            timestamp=datetime.datetime.utcnow(),
                            color=channel.guild.me.color)
                        embed.add_field(
                            name="Winners", value="\n".join(w.mention for w in winners))
                    embed.set_author(name=f"{author.name}'s giveaway is over!",
                                     icon_url=author.avatar_url)
                    embed.set_footer(text="This giveaway ended:")

                    await msg.clear_reactions()
                    await msg.edit(embed=embed)
                    await channel.send(
                        f"Congratulations to {','.join(w.mention for w in winners)} for winning "
                        f"**{prize}** in {author.mention}'s giveaway! \U0001f3c6")
                    giveaways.remove(g)
                    dump_data(giveaways, "giveaways")
            await asyncio.sleep(1)

    def check_reaction(self, message, author):
        """For the purge command"""
        def check(reaction, user):
            if reaction.message.id != message.id or user != author:
                return False
            elif reaction.emoji == "\U00002705":
                return True
            elif reaction.emoji == "\U0000274c":
                return True
            return False
        return check

    @commands.command(brief="User not found. Try again")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, users: commands.Greedy[discord.User], *, reason: str=None):
        """**Must have the "Ban Members" permission**
        Bans user(s) from the server
        Format like this: `<prefix> ban <@mention user(s)> <reason for banning>`
        """
        if not users:
            await ctx.send("You didn't format the command correctly, it's supposed to look like "
                           "this: `<prefix> ban <user(s)> <reason for banning>`",
                           delete_after=10.0)
            return await delete_message(ctx, 10)

        if reason is None:
            reason = "No reason given"
        if len(reason) + len(ctx.author.name) + 23 > 512:
            max_length = 512 - (len(ctx.author.name) + 23)
            await ctx.send(f"Reason is too long. It must be under {max_length} characters",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        if self.bot.user in users:
            return await ctx.send(":rolling_eyes:")

        banned, cant_ban = [], []

        temp = await ctx.send("Banning...")
        with ctx.channel.typing():
            for user in users:
                try:
                    await ctx.guild.ban(
                        user=user, reason=reason + " | Action performed by " + ctx.author.name)
                    banned.append(str(user))
                except:
                    cant_ban.append(user)
            await temp.delete()

        if len(banned) == 1:
            embed = discord.Embed(
                title=f"{banned[0]} was banned by {ctx.author.name}",
                description="__Reason__: " + reason, color=find_color(ctx))
            embed.set_thumbnail(url="https://i.imgur.com/0A6naoR.png")
            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        elif banned:
            embed = discord.Embed(
                title=f"{len(banned)} users were banned by {ctx.author.name}",
                description=f"**Banned**: `{'`, `'.join(banned)}`\n__Reason__: " + reason,
                color=find_color(ctx))
            embed.set_thumbnail(url="https://i.imgur.com/0A6naoR.png")
            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        if len(cant_ban) == 1:
            embed = discord.Embed(
                title=f"I couldn't ban {cant_ban[0].name}",
                description=f"{cant_ban[0].mention} has a role that's higher than mine in the "
                "server hierarchy, so I couldn't ban them",
                color=find_color(ctx))
            await ctx.send(embed=embed)

        elif cant_ban:
            embed = discord.Embed(
                title="I couldn't ban all the users you listed",
                description="Some of the users you listed have a role that's higher than mine in "
                "the server hierarchy, so I couldn't ban them",
                color=find_color(ctx))
            embed.add_field(name="Here are the users I couldn't ban:",
                            value=f"{', '.join(u.mention for u in cant_ban)}")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_guild=True)
    async def dehoist(self, ctx, include_num: str=None):
        """**Must have the "Manage Server" permission**
        Dehoists members who have hoisted themselves (This means they've started their nickname with a special character like !, $, etc. for the sole purpose of appearing at the top of the members list).
        This command will change their nickname to "Hoisted"
        By default, this command will dehoist all members who's display names start with a special character. If you want to be extra strict and also dehoist members who's names start with a number, add `-strict` to the end of the command
        """
        members_dehoisted, members_failed = [], []
        start_time = time.time()
        if include_num == "-strict":
            bad_characters = list(string.punctuation + string.digits)
        else:
            bad_characters = list(string.punctuation)

        msg = await ctx.send("Dehoisting... Please wait...")
        with ctx.channel.typing():
            for member in ctx.guild.members:
                try:
                    if member.display_name[0] in bad_characters:
                        await member.edit(
                            nick="Hoisted", reason=f"Hoisted by {ctx.author.name}")
                        members_dehoisted.append(
                            f"{member.name} - User ID: {member.id}")
                except:
                    members_failed.append(
                        f"{member.name} - User ID: {member.id}")

            if len(members_dehoisted) == 0 and len(members_failed) == 0:
                await asyncio.sleep(1)
                await msg.delete()
                await ctx.send("No one in this server needed to be dehoisted", delete_after=6.0)
                return await delete_message(ctx, 6)

            content = (f"=======================\nMembers Dehoisted ({len(members_dehoisted)}):"
                       "\n=======================\n\n" + "\n".join(members_dehoisted))
            if members_failed:
                content += (f"\n\n\n===================\nMembers Failed ({len(members_failed)}):"
                            "\n===================\n\n" + "\n".join(members_failed))
            async with aiohttp.ClientSession() as session:
                async with session.post("https://hastebin.com/documents",
                                        data=content.encode("utf-8")) as w:
                    #* For whatever reason, "await w.json()" doesn't work, so I'm using this instead
                    post = json.loads(await w.read())
                    link = f"https://hastebin.com/raw/{post['key']}"

            seconds = round(time.time() - start_time, 1)
            if seconds.is_integer():
                seconds = int(seconds)
            embed = discord.Embed(
                title=f"{ctx.author.name} performed a dehoist",
                description=f"**{len(members_dehoisted)}** members dehoisted in "
                f"__{seconds}__ seconds\n**{len(members_failed)}** members failed to "
                f"dehoist\n[Detailed list]({link})",
                color=find_color(ctx))

            await msg.delete()
            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> disable <command OR category>`\n\nYou can put a command and "
                      "I'll disable it for this server or you could put in a category (Fun, "
                      "Image, NSFW, etc.) and I'll disable all commands in that category")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, cmd):
        """**Must have the Administrater permission**
        Disable a command or group of commands for this server
        Format like this: `<prefix> disable <command OR category>`
        """
        if cmd.lower() == "help":
            await ctx.send("Yeah, great idea. Disable the freaking help command :rolling_eyes:",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        elif cmd.lower() == "enable":
            await ctx.send("I don't think I need to explain why it would be a bad idea to "
                           "disable that command", delete_after=7.0)
            return await delete_message(ctx, 7)

        if "disabled" in get_data("server")[str(ctx.guild.id)]:
            if cmd.lower() in get_data("server")[str(ctx.guild.id)]["disabled"]:
                await ctx.send("This command is already disabled", delete_after=5.0)
                return await delete_message(ctx, 5)

        serverdata = get_data("server")
        if cmd.lower() in set(c.name for c in self.bot.commands):
            try:
                serverdata[str(ctx.guild.id)]["disabled"].append(cmd.lower())
            except:
                serverdata[str(ctx.guild.id)]["disabled"] = [cmd.lower()]
            dump_data(serverdata, "server")

            embed = discord.Embed(
                title=ctx.author.name + " disabled a command",
                description=f"The `{cmd.lower()}` command is now disabled on this server",
                color=find_color(ctx))

            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        elif cmd in ["Fun", "Image", "Info", "Moderation", "NSFW", "Utility"]:
            for c in self.bot.get_cog_commands(cmd):
                if c.name == "enable":  #* So it doesn't disable the "enable" command
                    continue
                try:
                    serverdata[str(ctx.guild.id)]["disabled"].append(c.name)
                except:
                    serverdata[str(ctx.guild.id)]["disabled"] = [c.name]
            dump_data(serverdata, "server")

            embed = discord.Embed(title=ctx.author.name + " disabled a group of commands",
            description=f"All commands in the {cmd} category are now disabled on this server.\n\n"
            f"`{'`, `'.join(c.name for c in self.bot.commands if c.cog_name == cmd)}`",
            color=find_color(ctx))

            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        else:
            raise commands.BadArgument

    @commands.command(brief="Invalid Formatting. The command is supposed to look like this: "
                      "`<prefix> enable <command OR \"all\">`\n\nYou can put a command and "
                      "I'll enable it for this server or you could put in `all` and I'll enable "
                      "all previously disabled commands")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, cmd):
        """**Must have the Administrater permission**
        Enable a previously disabled command(s) for this server
        Format like this: `<prefix> enable <command OR "all">`
        """
        if not "disabled" in get_data("server")[str(ctx.guild.id)]:
            await ctx.send("This server doesn't have any disabled commands to begin with",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        serverdata = get_data("server")
        if cmd.lower() in serverdata[str(ctx.guild.id)]["disabled"]:
            serverdata[str(ctx.guild.id)]["disabled"].remove(cmd.lower())
            dump_data(serverdata, "server")

            embed = discord.Embed(
                title=ctx.author.name + " enabled a command",
                description=f"The `{cmd.lower()}` command is no longer disabled on this server",
                color=find_color(ctx))

            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        elif cmd.lower() == "all":
            disabled = serverdata[str(ctx.guild.id)]["disabled"]
            serverdata[str(ctx.guild.id)].pop("disabled", None)
            dump_data(serverdata, "server")

            embed = discord.Embed(
                title=ctx.author.name + " enabled all previously disabled commands",
                description="There are no more disabled commands on this server\n\n**Commands "
                f"enabled**:\n`{'`, `'.join(disabled)}`", color=find_color(ctx))

            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        elif (cmd.lower() not in serverdata[str(ctx.guild.id)]["disabled"] and
                  cmd.lower() in set(c.name for c in self.bot.commands)):
            await ctx.send("This command is already enabled. Do `<prefix> help` to see a list of "
                           "all disabled commands", delete_after=7.0)
            return await delete_message(ctx, 7)

        elif (cmd.lower() not in serverdata[str(ctx.guild.id)]["disabled"] and
                  cmd.lower() not in set(c.name for c in self.bot.commands)):
            raise commands.BadArgument

    @commands.command(aliases=["raffle"], brief="Invalid formatting. The command should look "
                      "like this: `<prefix> giveaway (OPTIONAL)<blacklist> (OPTIONAL)<channel> "
                      "(OPTIONAL)<number of winners (defaults to 1)> <duration> <prize name>`\n"
                      "For the blacklist, mention any users who aren't allowed to compete in "
                      "this giveaway\nIf you don't mention a channel, I'll just use the channel "
                      "the command was performed in\nFor the duration, there's a specific format "
                      "it should be in. Here are some examples of what it should look like: "
                      "`1w3d` for 1 week and 3 days, `5h15m` for 5 hours and 15 minutes, `2w` "
                      "for 2 weeks, `45m` for 45 minutes, etc. (NO SPACES)")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx, blacklist: commands.Greedy[discord.Member]=[], channel: typing.Optional[discord.TextChannel]=None, num_winners: typing.Optional[int]=1, duration: str=None, *, prize: str=None):
        """**Must have the "Manage Server" permission**
        Start a giveaway/raffle!
        Format like this: `<prefix> giveaway (OPTIONAL)<blacklist> (OPTIONAL)<channel> (OPTIONAL)<number of winners (defaults to 1)> <duration> <prize name>`
        For the blacklist, mention any users who aren't allowed to compete in this giveaway
        If you don't mention a channel, I'll just use the channel the command was performed in
        Note: The duration should look something like this: `2w` OR `30d12h30m` OR `1d30m` (NO SPACES)
        """
        parsed_duration = pytimeparse.parse(duration)
        if prize is None or parsed_duration is None:
            raise commands.BadArgument
        if num_winners < 1:
            await ctx.send(
                f"There must be at least one winner of the giveaway. You put {num_winners}",
                delete_after=6.0)
            return await delete_message(ctx, 6)
        if parsed_duration < 900 or parsed_duration > 2592000:
            await ctx.send("The duration of the giveaway must be longer than 15 minutes and no "
                           "more than 30 days", delete_after=7.0)
            return await delete_message(ctx, 7)

        if channel is None:
            channel = ctx.channel
        end_time = datetime.datetime.utcnow().timestamp() + parsed_duration
        description = (f"__Prize__: **{prize}**\n__Duration__: **{duration}**\nReact with "
                       "\U0001f3ab to enter the giveaway!\nJust remove your reaction to exit the "
                       f"giveaway.\n\nAs the creator of this raffle, {ctx.author.mention} can "
                       "cancel it by reacting with \U0001f6d1\nNote: Don't delete this message, "
                       "or the giveaway won't work!")
        if blacklist:
            description += ("\n\nIf you're on the blacklist, you can react all you want, but you "
                            "won't be part of the drawing pool when a winner is selected")
        embed = discord.Embed(description=description, color=find_color(ctx),
                              timestamp=datetime.datetime.fromtimestamp(end_time))
        embed.set_author(
            name=f"{ctx.author.display_name} started a giveaway!", icon_url=ctx.author.avatar_url)
        if blacklist:
            embed.add_field(name="Blacklist", value=", ".join(m.mention for m in blacklist))
        embed.set_footer(text=f"{num_winners} winner{'' if num_winners == 1 else 's'} | "
                         "This giveaway will end:")
        msg = await channel.send(embed=embed)
        await msg.add_reaction("\U0001f3ab")
        await msg.add_reaction("\U0001f6d1")

        new_giveaway = {
            "msg": str(msg.id),
            "channel": str(channel.id),
            "author": str(ctx.author.id),
            "end_time": str(end_time),
            "blacklist": [str(m.id) for m in blacklist],
            "winners": str(num_winners),
            "prize": prize
        }
        giveaways = get_data("giveaways")
        giveaways.append(new_giveaway)
        dump_data(giveaways, "giveaways")

    @commands.command(brief="Member not found. Try again")
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str=None):
        """**Must have the "Kick Members" permission**
        Kicks member(s) from the server
        Format like this: `<prefix> kick <@mention member(s)> <reason for kicking>`
        """
        if not members:
            await ctx.send("You didn't format the command correctly, it's supposed to look like "
                           "this: `<prefix> kick <@mention member(s)> <reason for kicking>`",
                           delete_after=10.0)
            return await delete_message(ctx, 10)

        if reason is None:
            reason = "No reason given"
        if len(reason) + len(ctx.author.name) + 23 > 512:
            max_length = 512 - (len(ctx.author.name) + 23)
            await ctx.send(f"Reason is too long. It must be under {max_length} characters",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        if ctx.guild.me in members:
            return await ctx.send(":rolling_eyes:")

        kicked, cant_kick = [], []

        temp = await ctx.send("Kicking...")
        with ctx.channel.typing():
            for member in members:
                try:
                    await member.kick(reason=reason + " | Action performed by " + ctx.author.name)
                    kicked.append(str(member))
                except:
                    cant_kick.append(member)
            await temp.delete()

        if len(kicked) == 1:
            embed = discord.Embed(
                title=f"{kicked[0]} was kicked by {ctx.author.name}",
                description="__Reason__: " + reason, color=find_color(ctx))
            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        elif kicked:
            embed = discord.Embed(
                title=f"{len(kicked)} members were kicked by {ctx.author.name}",
                description=f"**Kicked**: `{'`, `'.join(kicked)}`\n__Reason__: " + reason,
                color=find_color(ctx))
            await ctx.send(embed=embed)
            await send_log(ctx.guild, embed)

        if len(cant_kick) == 1:
            embed = discord.Embed(
                title=f"I couldn't kick {cant_kick[0].name}",
                description=f"{cant_kick[0].mention} has a role that's higher than mine in the "
                "server hierarchy, so I couldn't kick them",
                color=find_color(ctx))
            await ctx.send(embed=embed)

        elif cant_kick:
            embed = discord.Embed(
                title="I couldn't kick all the members you listed",
                description="Some of the members you listed have a role that's higher than mine in "
                "the server hierarchy, so I couldn't kick them",
                color=find_color(ctx))
            embed.add_field(name="Here are the members I couldn't kick:",
                            value=f"{', '.join(m.mention for m in cant_kick)}")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def nologs(self, ctx):
        """**Must have the Administrator permission**
        Disables the logs channel
        """
        serverdata = get_data("server")
        serverdata[str(ctx.guild.id)]["logs"] = "false"
        dump_data(serverdata, "server")

        await ctx.send(
            "Logging moderation commands has been turned off for this server "
            f"by {ctx.author.mention}. To turn them back on, just use the `setlogs` command.")

    @commands.group(aliases=["remove"])
    @commands.guild_only()
    async def purge(self, ctx):
        """**Must have the "Manage Messages" permission**
        Mass-deletes messages from a certain channel.
        There are several different ways to use this command. Type just `<prefix> purge` for help
        """
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="MAT's Purge Command | Help", description="An easy way to mass-delete "
                "messages from a channel!\n\nAdd **one** of these to the command to purge "
                "messages that fit a certain criteria:", color=find_color(ctx))

            embed.add_field(name="all (OPTIONAL)<number>", value="Deletes all "
                            "messages in the channel. If you also put in a number, it'll only "
                            "delete that many messages. I default to 1000, and I can't go over "
                            "2000.", inline=False)
            embed.add_field(name="clear", value="Completely clears a channel by deleting and "
                            "replacing it with an identical one. I need the **Manage Channels** "
                            "permission in order to do this.", inline=False)
            embed.add_field(name="member <mention user(s)>", value="Deletes all messages by a "
                            "certain member or members of the server", inline=False)
            embed.add_field(name="contains <substring>", value="Deletes all messages that "
                            "contain a substring, which must be specified (not case-sensitive)",
                            inline=False)
            embed.add_field(name="files", value="Deletes all messages with files attached",
                            inline=False)
            embed.add_field(name="embeds", value="Deletes all messages with embeds (The messages "
                            "with a colored line off to the side, like this one. This means a "
                            "lot of bot messages will be deleted, along with any links and/or "
                            "videos that were posted)", inline=False)
            embed.add_field(name="bot (OPTIONAL)<bot prefix>", value="Deletes all messages by "
                            "bots. If you add in a bot's prefix I'll also delete all messages "
                            "that contain that prefix", inline=False)
            embed.add_field(name="emoji", value="Deletes all messages that contain a custom "
                            "emoji", inline=False)
            embed.add_field(name="before <message ID> (OPTIONAL)<number>", value="Deletes a "
                            "certain number of messages that come before the one with the given "
                            "ID. See [here](https://support.discordapp.com/hc/en-us/articles/"
                            "206346498-Where-can-I-find-my-User-Server-Message-ID-) if you don't "
                            "know how to get a message's ID. If you don't put a number, I'll "
                            "default to 100. I can go up to 2000.")
            embed.add_field(name="after <message ID>", value="Deletes all messages that come "
                            "after the one with the given message ID. See [here](https://support."
                            "discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-"
                            "Server-Message-ID-) if you don't know how to get a message's ID",
                            inline=False)
            embed.add_field(name="reactions", value="Removes all reactions from messages that "
                            "have them", inline=False)
            embed.add_field(name="pins (OPTIONAL)<number to leave pinned>", value="Unpins all "
                            "pinned messages in this channel. You can also specify a certain "
                            "number of messages to leave pinned.", inline=False)

            await ctx.send(embed=embed)

    async def remove(self, ctx, limit, check, description: str, before=None, after=None):
        if limit > 2000:
            await ctx.send(
                "I can't purge more than 2000 messages at a time. Put a smaller number",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        if limit >= 20:
            if ctx.command.name == "all":
                confirm = await ctx.send("React with \U00002705 to confirm that you want to "
                                         "purge 20+ messages in this channel. React with "
                                         "\U0000274c to cancel")
            else:
                confirm = await ctx.send("React with \U00002705 to confirm that you want to "
                                         "purge messages in this channel. React with \U0000274c "
                                         "to cancel")
            await confirm.add_reaction("\U00002705")
            await confirm.add_reaction("\U0000274c")

            try:
                react, user = await self.bot.wait_for(
                    "reaction_add", timeout=15, check=self.check_reaction(confirm, ctx.author))
            except asyncio.TimeoutError:
                await ctx.send(
                    "You took too long to react so the operation was cancelled", delete_after=6.0)
                await delete_message(ctx, 6)
                return await confirm.delete()

            if react.emoji == "\U0000274c":
                await ctx.send("Ok, the operation has been cancelled", delete_after=5.0)
                await delete_message(ctx, 5)
                return await confirm.delete()

            await confirm.delete()

        if before is None:
            before = ctx.message

        temp = await ctx.send("Purging...")
        with ctx.channel.typing():
            purged = await ctx.channel.purge(limit=limit, check=check, before=before, after=after)
        await temp.delete()
        await ctx.message.delete()

        messages = collections.Counter()
        embed = discord.Embed(
            title=ctx.author.name + " ran a purge command",
            description=f"{len(purged)} {description} in {ctx.channel.mention}",
            color=find_color(ctx))
        if len(purged) >= 10:
            await send_log(ctx.guild, embed)

        for m in purged:
            messages[m.author.display_name] += 1
        for a, m in messages.items():
            embed.add_field(name=a, value=f"{m} messages")

        if len(purged) < 10:
            if get_data("server")[str(ctx.guild.id)]["logs"] != "false":
                embed.set_footer(text="The number of messages purged was less than 10, so a log "
                                 "wasn't sent to the logs channel")
        try:
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title=ctx.author.name + " ran a purge command",
                description=f"{len(purged)} {description} in {ctx.channel.mention}",
                color=find_color(ctx))
            await ctx.send(embed=embed)

    @purge.command(brief="Invalid formatting. You must format the command like this: "
                   "`<prefix> purge after <message ID>`\nIf you don't know how to get a "
                   "message's ID, see here:\nhttps://support.discordapp.com/hc/en-us/articles/"
                   "206346498-Where-can-I-find-my-User-Server-Message-ID-")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def after(self, ctx, msg: int):

        try:
            message = await ctx.channel.get_message(msg)
        except:
            raise commands.BadArgument

        await self.remove(
            ctx, 1000, None, f"messages after [this one]({message.jump_url}) were deleted",
            after=message)

    @purge.command(name="all", brief="Invalid formatting. You must format the command like this: "
                   "`<prefix> purge all (OPTIONAL)<number of messages to delete>`")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def all_(self, ctx, limit: int=1000):

        await self.remove(ctx, limit, None, "messages were deleted")

    @purge.command(brief="Invalid formatting. You must format the command like this: "
                   "`<prefix> purge after <message ID> (OPTIONAL)<number>`\nIf you don't put a "
                   "number, I'll default to 100.\nAlso, if you don't know how to get a message's "
                   "ID, see here:\nhttps://support.discordapp.com/hc/en-us/articles/"
                   "206346498-Where-can-I-find-my-User-Server-Message-ID-")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def before(self, ctx, msg: int, limit: int=100):

        try:
            message = await ctx.channel.get_message(msg)
        except:
            raise commands.BadArgument

        await self.remove(
            ctx, limit, None, f"messages before [this one]({message.jump_url}) were deleted",
            before=message)

    @purge.command(name="bot", aliases=["bots"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def bot_(self, ctx, *, prefix=None):

        def check(m):
            return m.webhook_id is None and m.author.bot or (
                prefix and m.content.startswith(prefix))

        if prefix is None:
            await self.remove(ctx, 1000, check, "messages by bots were deleted")
        else:
            await self.remove(ctx, 1000, check, "messages by bots and messages containing the "
                              f"prefix `{prefix}` were deleted")

    @purge.command()
    @commands.guild_only()
    @commands.bot_has_permissions(
        manage_messages=True, read_message_history=True, manage_channels=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx):

        name = ctx.channel.name
        perms = dict(ctx.channel.overwrites)
        cat = ctx.channel.category
        topic = ctx.channel.topic
        pos = ctx.channel.position
        nsfw = ctx.channel.is_nsfw()

        no_triggers = False
        serverdata = get_data("server")
        if "triggers_disabled" in serverdata[str(ctx.guild.id)]:
            if str(ctx.channel.id) in serverdata[str(ctx.guild.id)]["triggers_disabled"]:
                serverdata[str(ctx.guild.id)]["triggers_disabled"].remove(str(ctx.channel.id))
                no_triggers = True

        confirm = await ctx.send("React with \U00002705 to confirm that you want to "
                                 "clear this channel. React with \U0000274c to cancel")
        await confirm.add_reaction("\U00002705")
        await confirm.add_reaction("\U0000274c")

        try:
            react, user = await self.bot.wait_for(
                "reaction_add", timeout=15, check=self.check_reaction(confirm, ctx.author))
        except asyncio.TimeoutError:
            await ctx.send(
                "You took too long to react so the operation was cancelled", delete_after=6.0)
            await delete_message(ctx, 6)
            return await confirm.delete()

        if react.emoji == "\U0000274c":
            await ctx.send("Ok, the operation has been cancelled", delete_after=5.0)
            await delete_message(ctx, 5)
            return await confirm.delete()

        await confirm.delete()

        await ctx.channel.delete(reason=ctx.author.name + " cleared the channel")
        cleared = await ctx.guild.create_text_channel(name=name, overwrites=perms, category=cat)
        await cleared.edit(topic=topic, position=pos, nsfw=nsfw)
        if no_triggers:
            serverdata[str(ctx.guild.id)]["triggers_disabled"].append(str(cleared.id))
            dump_data(serverdata, "server")

        embed = discord.Embed(
            title=ctx.author.name + " ran a purge command",
            description=cleared.mention + " was completely cleared", color=find_color(ctx))

        await cleared.send(embed=embed)
        await send_log(ctx.guild, embed)

    @purge.command(brief="Invalid formatting. You must include a substring for me to look "
                   "for, like this: `<prefix> purge contains <substring>`")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def contains(self, ctx, *, substr: str):

        await self.remove(ctx, 1000, lambda m: re.search(substr, m.content, re.IGNORECASE),
                          f"messages containing the string `{substr}` were deleted")

    @purge.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def embeds(self, ctx):

        await self.remove(
            ctx, 1000, lambda m: len(m.embeds), "messages containing embeds were deleted")

    @purge.command(aliases=["emojis", "emote", "emotes"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def emoji(self, ctx):

        def check(m):
            custom_emoji = re.compile(r"<:(\w+):(\d+)>")
            return custom_emoji.search(m.clean_content)

        await self.remove(ctx, 1000, check, "messages containing custom emojis were deleted")

    @purge.command(aliases=["attachments"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def files(self, ctx):

        await self.remove(ctx, 1000, lambda m: len(m.attachments),
                          "messages containing attachments were deleted")

    @purge.command(aliases=["user", "members", "users"], brief="Invalid formatting. You must "
                   "format the command like this: `<prefix> purge member <@memtion user(s) or "
                   "username(s)>`")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def member(self, ctx, *users: discord.Member):

        users = list(users)
        if not users:
            raise commands.BadArgument

        await self.remove(ctx, 1000, lambda m: m.author in users,
                          f"messages by {', '.join(u.mention for u in users)} were deleted")

    @purge.command(brief="Invalid formatting. You're supposed to format the command like this: "
                   "`<prefix> purge pins (OPTIONAL)<number to leave pinned>`")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def pins(self, ctx, leave: int=None):

        all_pins = await ctx.channel.pins()
        if len(all_pins) == 0:
            await ctx.send("This channel has no pinned messages", delete_after=5.0)
            return await delete_message(ctx, 5)

        temp = await ctx.send("Please wait... This could take some time...")
        with ctx.channel.typing():
            for m in all_pins:
                await m.unpin()
                if len(await ctx.channel.pins()) == leave:
                    break

        embed = discord.Embed(
            title=ctx.author.name + " ran a purge command",
            description=f"{len(all_pins)} messages were unpinned in {ctx.channel.mention}",
            color=find_color(ctx))

        await ctx.message.delete()
        await temp.delete()
        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    @purge.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def reactions(self, ctx):

        temp = await ctx.send("Please wait... This could take some time...")
        with ctx.channel.typing():
            total_reactions = 0
            total_messages = 0
            async for m in ctx.channel.history(limit=2000, before=ctx.message):
                if len(m.reactions):
                    total_reactions += sum(r.count for r in m.reactions)
                    total_messages += 1
                    await m.clear_reactions()

        embed = discord.Embed(
            title=ctx.author.name + " ran a purge command",
            description=f"{total_reactions} reactions were removed from {total_messages} "
            f"messages in {ctx.channel.mention}", color=find_color(ctx))

        await ctx.message.delete()
        await temp.delete()
        await ctx.send(embed=embed)
        if total_reactions > 0:
            await send_log(ctx.guild, embed)

    @commands.command(brief="Incorrect formatting. You're supposed to provide a list of "
                      "@mentions or member names that I'll randomly choose from. Or don't put "
                      "anything and I'll randomly pick someone from the server")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def randomkick(self, ctx, *members: discord.Member):
        """**Must have the "Kick Members" permission**
        Kicks a random member, feeling lucky?
        Format like this: `<prefix> randomkick (OPTIONAL)<list of members you want me to randomly pick from>`.
        If you don't mention anyone, I'll randomly select someone from the server.
        """
        rip_list = ["rip", "RIP", "Rip in spaghetti, never forgetti", "RIPeroni pepperoni",
                    "RIP in pieces", "Rest in pieces"]
        try:
            member = random.choice(members)
        except IndexError:
            member = random.choice(ctx.guild.members)

        try:
            await member.kick(
                reason="Unlucky individual selected by the randomkick performed by " +
                ctx.author.name)
            temp = await ctx.send("And the unlucky individual about to be kicked is...")
            with ctx.channel.typing():
                await asyncio.sleep(3)
                await temp.delete()
                await ctx.send(embed=discord.Embed(
                    color=find_color(ctx), title=member.name + "!!!",
                    description=random.choice(rip_list)))
        except discord.Forbidden:
            return await ctx.send(
                "Huh, it looks like I don't have permission to kick this person. Could one of "
                "you guys check my role to make sure I have either the Kick Members privilege or "
                "the Administrator privilege?\n\nIf I already, do, then I probably picked "
                "someone with a role higher than mine. So try again, or better yet, put my role "
                "above everyone else's. Then we can make this *really* interesting...")
        await send_log(ctx.guild, discord.Embed(
            title="A randomkick was performed by " + ctx.author.name,
            description=str(member) + " was kicked", color=find_color(ctx)))

    @commands.command(aliases=["snipe"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def restore(self, ctx):
        """**Must have the "Manage Messages" permission**
        Restores the last deleted message by a non-bot member
        Note: Because of how Discord works, I can't restore attachments to messages, just the text of the message
        """
        try:
            last_delete = get_data("server")[str(ctx.guild.id)]["last_delete"]
        except:
            await ctx.send(
                "Unable to find the last deleted message. Sorry!", delete_after=5.0)
            return await delete_message(ctx, 5)

        if len(f"```{last_delete['content']}```") <= 1024:
            embed = discord.Embed(
                title="Restored last deleted message",
                description=f"**Sent by**: {last_delete['author']}\n" + last_delete["creation"],
                color=find_color(ctx))
            embed.add_field(name="Message", value=f"```{last_delete['content']}```", inline=False)
            embed.add_field(name="Channel", value=last_delete["channel"])
        else:
            embed = discord.Embed(
                title="Restored last deleted message",
                description=f"**Message**:\n```{last_delete['content']}```",
                color=find_color(ctx))
            embed.add_field(name="Sent by", value=last_delete['author'])
            embed.add_field(name="Channel", value=last_delete["channel"])
            embed.add_field(name="Sent on", value=last_delete["creation"][13:])
        embed.set_footer(text="Restored by " + ctx.author.name)

        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def rmgoodbye(self, ctx):
        """**Must have Administrator permissions**
        Removes a previously set custom welcome message
        """
        serverdata = get_data("server")
        if "goodbye" not in serverdata[str(ctx.guild.id)]:
            await ctx.send("This server doesn't have a custom goodbye message. Use "
                           "the `setgoodbye` command to make one", delete_after=7.0)
            return await delete_message(ctx, 7)

        msg = serverdata[str(ctx.guild.id)]["goodbye"]["message"]
        serverdata[str(ctx.guild.id)].pop("goodbye", None)
        dump_data(serverdata, "server")

        embed = discord.Embed(
            title=ctx.author.name + " REMOVED the custom goodbye message",
            description=f"**Message**: ```{msg.format('(member)')}```",
            color=find_color(ctx))

        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def rmwelcome(self, ctx):
        """**Must have Administrator permissions**
        Removes a previously set custom goodbye message
        """
        serverdata = get_data("server")
        if "welcome" not in serverdata[str(ctx.guild.id)]:
            await ctx.send("This server doesn't have a custom welcome message. Use "
                           "the `setwelcome` command to make one", delete_after=7.0)
            return await delete_message(ctx, 7)

        msg = serverdata[str(ctx.guild.id)]["welcome"]["message"]
        serverdata[str(ctx.guild.id)].pop("welcome", None)
        dump_data(serverdata, "server")

        embed = discord.Embed(
            title=ctx.author.name + " REMOVED the custom welcome message",
            description=f"**Message**: ```{msg.format('(member)')}```",
            color=find_color(ctx))

        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    @commands.command(brief="Invalid formatting. Format like this: `<prefix> setlogs <mention "
                      "channel or channel name>`.\nTo turn off the logs channel, use "
                      "the `nologs` command")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel):
        """**Must have Administrator permissions**
        Sets a "logs" channel for me to keep a log of all of my moderation commands.
        Format like this: `<prefix> setlogs <mention channel or channel name>`
        To turn off the logs channel, use the `nologs` command
        """
        serverinfo = get_data("server")
        serverinfo[str(ctx.guild.id)]["logs"] = str(channel.id)
        dump_data(serverinfo, "server")

        await ctx.send(f"The logs channel is now set to {channel.mention}!")
        await channel.send(
            f"This is now the new logs channel, set by {ctx.author.mention}. Whenever "
            "someone uses one of my moderation commands, a message will be sent here to keep "
            "a log of them.")

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> setgoodbye <#mention channel> <goodbye message>`\n\nWhen you're "
                      "typing the message, put a pair of braces `{}` in to mark where the new "
                      "member's name will go. It's required that you put the braces in "
                      "there somewhere, but only once")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setgoodbye(self, ctx, channel: discord.TextChannel, *, msg: str):
        """**Must have Administrator permissions**
        Set a custom goodbye message to send whenever a member leaves the server.
        Format like this: `<prefix> setgoodbye <#mention channel> <goodbye message>`
        When you're typing the message, put a pair of braces `{}` in to mark where the member's name will go. The braces are required.
        Finally, to remove the custom goodbye message, just do `<prefix> rmgoodbye`
        """
        if len(re.findall("{}", msg)) != 1:
            raise commands.BadArgument

        serverdata = get_data("server")
        serverdata[str(ctx.guild.id)]["goodbye"] = {"message": msg, "channel": str(channel.id)}
        dump_data(serverdata, "server")

        embed = discord.Embed(title=ctx.author.name + " set a new custom goodbye message",
                              description=f"**Channel**: {channel.mention}\n**Message**: "
                              f"```{msg.format('(member)')}```", color=find_color(ctx))
        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> setwelcome <#mention channel> <welcome message>`\n\nWhen you're "
                      "typing the message, put a pair of braces `{}` in to mark where the new "
                      "member's name will go. It's required that you put the braces in "
                      "there somewhere, but only once")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel, *, msg: str):
        """**Must have Administrator permissions**
        Set a custom welcome message to send whenever a new member joins the server.
        Format like this: `<prefix> setwelcome <#mention channel> <welcome message>`
        When you're typing the message, put a pair of braces `{}` in to mark where the new member's name will go. The braces are required.
        Finally, to remove the custom welcome message, just do `<prefix> rmwelcome`
        """
        if len(re.findall("{}", msg)) != 1:
            raise commands.BadArgument

        serverdata = get_data("server")
        serverdata[str(ctx.guild.id)]["welcome"] = {"message": msg, "channel": str(channel.id)}
        dump_data(serverdata, "server")

        embed = discord.Embed(title=ctx.author.name + " set a new custom welcome message",
                              description=f"**Channel**: {channel.mention}\n**Message**: "
                              f"```{msg.format('(member)')}```", color=find_color(ctx))
        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def toggle(self, ctx):
        """**Must have the "Manage Messages" permission**
        Toggles my trigger words on/off for the channel the command was performed in
        """
        serverdata = get_data("server")
        try:
            no_triggers = serverdata[str(ctx.guild.id)]["triggers_disabled"]
        except:
            no_triggers = serverdata[str(ctx.guild.id)]["triggers_disabled"] = []

        if str(ctx.channel.id) not in no_triggers:
            no_triggers.append(str(ctx.channel.id))
            await ctx.send("Ok, I'll stop reacting to triggers in this channel")

        elif str(ctx.channel.id) in no_triggers:
            no_triggers.remove(str(ctx.channel.id))
            await ctx.send("Ok, I'll start reacting to triggers in this channel again!")

        serverdata[str(ctx.guild.id)]["triggers_disabled"] = no_triggers
        dump_data(serverdata, "server")

    @commands.command(brief="User not found in the bans list. To see a list of all banned "
                      "members, use the `allbanned` command.")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, users: commands.Greedy[discord.User], *, reason: str=None):
        """**Must have the "Ban Members" permission**
        Unbans a previously banned user(s) from the server
        Format like this: `<prefix> unban <user ID(s)> (OPTIONAL)<reason for unbanning>`
        To see a list of all banned members from this server and their IDs, use the `allbanned` command
        """
        if not users:
            await ctx.send(
                "You didn't format the command correctly, it's supposed to look like this: "
                "`<prefix> unban <user ID(s)> (OPTIONAL)<reason for unbanning>`",
                delete_after=10.0)
            return await delete_message(ctx, 10)

        if reason is None:
            reason = "No reason given"
        if len(reason) + len(ctx.author.name) + 23 > 512:
            max_length = 512 - (len(ctx.author.name) + 23)
            await ctx.send(f"Reason is too long. It must be under {max_length} characters",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        unbanned = []
        temp = await ctx.send("Unbanning...")
        with ctx.channel.typing():
            for user in users:
                try:
                    await ctx.guild.unban(
                        user=user, reason=reason + " | Action performed by " + ctx.author.name)
                    unbanned.append(str(user))
                except: pass
            await temp.delete()

        if not unbanned:
            raise commands.BadArgument
        elif len(unbanned) == 1:
            embed = discord.Embed(
                title=unbanned[0] + " has been unbanned by " + ctx.author.name,
                description="__Reason__: " + reason, color=find_color(ctx))
        else:
            embed = discord.Embed(
                title=f"{len(unbanned)} members have been unbanned by {ctx.author.name}",
                description=f"**Unbanned**: `{'`, `'.join(unbanned)}`\n__Reason__: " + reason,
                color=find_color(ctx))

        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
