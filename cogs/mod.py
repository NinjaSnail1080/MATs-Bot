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

from utils import find_color, delete_message, send_log

from discord.ext import commands, tasks
import discord
import pytimeparse
import rapidjson as json

import re
import random
import asyncio
import collections
import typing
import datetime
import time
import string


class Moderation(commands.Cog):
    """Moderation tools"""

    def __init__(self, bot):
        self.bot = bot

        self.star_emojis = ["\U00002b50", "\U0001f31f", "\U0001f320", "\U00002734"]

        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    async def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        return True

    @commands.Cog.listener()
    async def on_message(self, message):
        #TODO: Eventually this will contain the antispam features
        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        #* This function checks if a giveaway is cancelled by its creator
        if reaction.emoji == "\U0001f6d1":
            for g in self.bot.botdata["giveaways"].copy():
                if g["msg"] == reaction.message.id and g["author"] == user.id:
                    self.bot.botdata["giveaways"].remove(g)
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE botdata
                            SET giveaways = $1::JSON[]
                        ;""", self.bot.botdata["giveaways"])

                    embed = discord.Embed(
                        description=f"{user.mention}'s giveaway for the prize, **{g['prize']}** "
                        "has been cancelled", color=reaction.message.guild.me.color)
                    await reaction.message.clear_reactions()
                    return await reaction.message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (payload.guild_id is None or
                payload.emoji.name not in self.star_emojis or
                    self.bot.guilddata[payload.guild_id]["starboard"] is None):
            return
        if payload.channel_id == self.bot.guilddata[payload.guild_id]["starboard"]["channel"]:
            return
        if payload.message_id in self.bot.guilddata[payload.guild_id]["starboard"]["messages"]:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        starboard = self.bot.get_channel(
            self.bot.guilddata[payload.guild_id]["starboard"]["channel"])
        num_reactions = self.bot.guilddata[payload.guild_id]["starboard"]["num_reactions"]

        star_reactions = sum(
            [r.count for r in message.reactions if r.emoji in self.star_emojis])

        if star_reactions >= num_reactions:
            msg_content = message.clean_content

            #* The following code is to better format custom emojis that appear in the content
            custom_emoji = re.compile(r"<:(\w+):(\d+)>")
            for m in custom_emoji.finditer(msg_content):
                msg_content = msg_content.replace(m.group(), m.group()[1:-19])

            embed = discord.Embed(description=msg_content, timestamp=message.created_at,
                                  color=find_color(message))
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            embed.add_field(name="Original", value=f"[Message]({message.jump_url})")
            embed.add_field(name="Channel", value=channel.mention)
            embed.add_field(name="Message ID", value=message.id)
            if message.attachments:
                embed.set_image(url=message.attachments[0].url)

            await starboard.send(embed=embed)
            self.bot.guilddata[payload.guild_id]["starboard"]["messages"].append(message.id)
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET starboard = $1::JSON
                    WHERE id = {}
                ;""".format(payload.guild_id),
                self.bot.guilddata[payload.guild_id]["starboard"])

    async def db_set_null(self, guild_id, to_set):
        self.bot.guilddata[guild_id][to_set] = None
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET {} = NULL
                WHERE id = {}
            ;""".format(to_set, guild_id))

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        #* Checks to see if the channel deleted was a guild's log, welcome, goodbye, or
        #* starboard channel
        if channel.id == self.bot.guilddata[channel.guild.id]["logs"]:
            await self.db_set_null(channel.guild.id, "logs")

        if self.bot.guilddata[channel.guild.id]["welcome"] is not None:
            if channel.id == self.bot.guilddata[channel.guild.id]["welcome"]["channel"]:
                await self.db_set_null(channel.guild.id, "welcome")

        if self.bot.guilddata[channel.guild.id]["goodbye"] is not None:
            if channel.id == self.bot.guilddata[channel.guild.id]["goodbye"]["channel"]:
                await self.db_set_null(channel.guild.id, "goodbye")

        if self.bot.guilddata[channel.guild.id]["starboard"] is not None:
            if channel.id == self.bot.guilddata[channel.guild.id]["starboard"]["channel"]:
                await self.db_set_null(channel.guild.id, "starboard")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if role.id == self.bot.guilddata[role.guild.id]["mute_role"]:
            self.bot.guilddata[role.guild.id]["mute_role"] = None
            await self.db_set_null(channel.guild.id, "mute_role")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        #TODO: Eventually this will also contain the antiraid features
        welcome = self.bot.guilddata[member.guild.id]["welcome"]
        if welcome is not None:
            channel = self.bot.get_channel(welcome["channel"])
            await channel.send(welcome["message"].format(member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        goodbye = self.bot.guilddata[member.guild.id]["goodbye"]
        if goodbye is not None:
            channel = self.bot.get_channel(goodbye["channel"])
            await channel.send(goodbye["message"].format(member.mention))

    @tasks.loop(seconds=1)
    async def check_giveaways(self):

        async def remove_giveaway(giveaway):
            self.bot.botdata["giveaways"].remove(giveaway)
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE botdata
                    SET giveaways = $1::JSON[]
                ;""", self.bot.botdata["giveaways"])

        for g in self.bot.botdata["giveaways"].copy():
            if datetime.datetime.utcnow() >= datetime.datetime.fromtimestamp(g["end_time"]):
                try:
                    channel = self.bot.get_channel(g["channel"])
                    msg = await channel.fetch_message(g["msg"])
                    author = channel.guild.get_member(g["author"])
                    blacklist = g["blacklist"]
                    num_winners = g["winners"]
                    prize = g["prize"]
                except:
                    #* If something went wrong (for example, the giveaway msg was deleted),
                    #* just get rid of it and move on
                    await remove_giveaway(g)
                    continue

                for r in msg.reactions:
                    if r.emoji == "\U0001f3ab":
                        pool = await r.users().flatten()
                        break
                for m in pool.copy():
                    if m.bot or m.id in blacklist:
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
                    await remove_giveaway(g)
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
                await remove_giveaway(g)

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10) #* To ensure that the database is fully set up before it starts

    def check_reaction(self, message, author):
        """For the `purge` and `prune` commands"""
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
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, users: commands.Greedy[discord.User], *, reason: str=None):
        """**Must have the "Ban Members" permission**
        Bans user(s) from the server
        Format like this: `<prefix> ban <@mention user(s)> <reason for banning>`
        """
        if not users:
            await ctx.send("You didn't format the command correctly, it's supposed to look like "
                           f"this: `{ctx.prefix}ban <user(s)> <reason for banning>`",
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
            embed = discord.Embed(description="__Reason__: " + reason, color=find_color(ctx))
            embed.set_author(name=f"{ctx.author.name} banned {banned[0]} from this server",
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url="https://i.imgur.com/0A6naoR.png")
            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        elif banned:
            embed = discord.Embed(
                description=f"**Banned**: `{'`, `'.join(banned)}`\n__Reason__: " + reason,
                color=find_color(ctx))
            embed.set_author(name=f"{len(banned)} users were banned by {ctx.author.name}",
                             icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url="https://i.imgur.com/0A6naoR.png")
            await ctx.send(embed=embed)
            await send_log(ctx, embed)

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
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_guild=True)
    async def dehoist(self, ctx, include_num: str=None):
        """**Must have the "Manage Server" permission**
        Dehoists members who have hoisted themselves (This means they've started their nickname with a special character like !, $, etc. for the sole purpose of appearing at the top of the members list).
        This command will change their nickname to "Hoisted"
        By default, this command will dehoist all members who's display names start with a special character. If you want to be extra strict and also dehoist members whose names start with a number, add `-strict` to the end of the command
        """
        members_dehoisted, members_failed = [], []
        start_time = time.time()
        if include_num.lower() == "-strict":
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

        with ctx.channel.typing():
            content = (f"=======================\nMembers Dehoisted ({len(members_dehoisted)}):"
                       "\n=======================\n\n" + "\n".join(members_dehoisted))
            if members_failed:
                content += (f"\n\n\n===================\nMembers Failed ({len(members_failed)}):"
                            "\n===================\n\n" + "\n".join(members_failed))

            try:
                async with self.bot.session.post("https://hastebin.com/documents",
                                                 data=content.encode("utf-8")) as w:
                    #* For whatever reason, "await w.json()" doesn't work, so I'm using this:
                    post = json.loads(await w.read())
                    # post = await w.json()
                    link = f"https://hastebin.com/raw/{post['key']}"
            except:
                #* On the rare occasion that it fails to post to hastebin
                link = None

        duration = round(time.time() - start_time, 1)
        if duration.is_integer():
            duration = int(duration)
        if link is not None:
            embed = discord.Embed(
                description=f"**{len(members_dehoisted)}** members dehoisted in "
                f"__{duration}__ seconds\n**{len(members_failed)}** members failed to dehoist"
                f"\n[Detailed list]({link})",
                color=find_color(ctx))
        else:
            embed = discord.Embed(
                description=f"**{len(members_dehoisted)}** members dehoisted in "
                f"__{duration}__ seconds\n**{len(members_failed)}** members failed to dehoist",
                color=find_color(ctx))
        embed.set_author(name=f"{ctx.author.name} performed a dehoist",
                            icon_url=ctx.author.avatar_url)

        await msg.delete()
        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> disable <command OR category>`\n\nYou can put a command and "
                      "I'll disable it for this server or you could put in a category (Fun, "
                      "Image, NSFW, etc.) and I'll disable all commands in that category. Note: "
                      "The category is case-sensitive")
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, cmd):
        """**Must have the Administrater permission**
        Disable a command or group of commands for this server
        Format like this: `<prefix> disable <command OR category>`
        Note: The category is case-sensitive
        """
        await ctx.channel.trigger_typing()
        if cmd.lower() == "help":
            await ctx.send("Yeah, great idea. Disable the freaking help command :rolling_eyes:",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        elif cmd.lower() == "enable":
            await ctx.send("I don't think I need to explain why it would be a bad idea to "
                           "disable that command", delete_after=7.0)
            return await delete_message(ctx, 7)

        if cmd.lower() in self.bot.guilddata[ctx.guild.id]["disabled"]:
            await ctx.send("This command is already disabled", delete_after=5.0)
            return await delete_message(ctx, 5)

        if cmd.lower() in set(c.name for c in self.bot.commands):
            self.bot.guilddata[ctx.guild.id]["disabled"].append(cmd.lower())
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET disabled = $1::TEXT[]
                    WHERE id = {}
                ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["disabled"])

            embed = discord.Embed(
                description=f"The `{cmd.lower()}` command is now disabled on this server",
                color=find_color(ctx))
            embed.set_author(name=ctx.author.name + " disabled a command",
                             icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        elif cmd in ["Fun", "Image", "Info", "Moderation", "NSFW", "Utility"]:
            for c in self.bot.get_cog(cmd).get_commands():
                if c.name != "enable":  #* So it doesn't disable the "enable" command
                    self.bot.guilddata[ctx.guild.id]["disabled"].append(c.name)

            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET disabled = $1::TEXT[]
                    WHERE id = {}
                ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["disabled"])

            embed = discord.Embed(
                description=f"All commands in the {cmd} category are now disabled on this server."
                f"\n\n`{'`, `'.join(c.name for c in self.bot.get_cog(cmd).get_commands())}`",
                color=find_color(ctx))
            embed.set_author(name=ctx.author.name + " disabled a group of commands",
                             icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        else:
            raise commands.BadArgument

    @commands.command(brief="Invalid Formatting. The command is supposed to look like this: "
                      "`<prefix> enable <command OR \"all\">`\n\nYou can put a command and "
                      "I'll enable it for this server or you could put in `all` and I'll enable "
                      "all the disabled commands")
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, cmd):
        """**Must have the Administrater permission**
        Enable a previously disabled command(s) for this server
        Format like this: `<prefix> enable <command OR "all">`
        If you put `all`, I'll enable all the disabled commands
        """
        await ctx.channel.trigger_typing()
        if not self.bot.guilddata[ctx.guild.id]["disabled"]:
            await ctx.send("This server doesn't have any disabled commands to begin with",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        if cmd.lower() in self.bot.guilddata[ctx.guild.id]["disabled"]:
            self.bot.guilddata[ctx.guild.id]["disabled"].remove(cmd.lower())
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET disabled = $1::TEXT[]
                    WHERE id = {}
                ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["disabled"])

            embed = discord.Embed(
                description=f"The `{cmd.lower()}` command is no longer disabled on this server",
                color=find_color(ctx))
            embed.set_author(name=ctx.author.name + " enabled a command",
                             icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        elif cmd.lower() == "all":
            disabled = self.bot.guilddata[ctx.guild.id]["disabled"]
            self.bot.guilddata[ctx.guild.id]["disabled"].clear()
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET disabled = $1::TEXT[]
                    WHERE id = {}
                ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["disabled"])

            embed = discord.Embed(
                description="There are no more disabled commands on this server\n\n**Commands "
                f"enabled**:\n`{'`, `'.join(disabled)}`", color=find_color(ctx))
            embed.set_author(name=ctx.author.name + " enabled all previously disabled commands",
                             icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        elif (cmd.lower() not in self.bot.guilddata[ctx.guild.id]["disabled"] and
                  cmd.lower() in set(c.name for c in self.bot.commands)):
            await ctx.send(f"This command is already enabled. Do `{ctx.prefix}help` to see a "
                           "list of all disabled commands", delete_after=7.0)
            return await delete_message(ctx, 7)

        elif (cmd.lower() not in self.bot.guilddata[ctx.guild.id]["disabled"] and
                  cmd.lower() not in set(c.name for c in self.bot.commands)):
            raise commands.BadArgument

    @commands.command(aliases=["raffle"], brief="Invalid formatting. The command should look "
                      "like this:\n`<prefix> giveaway (OPTIONAL)<blacklist> (OPTIONAL)<channel> "
                      "(OPTIONAL)<number of winners (defaults to 1)> <duration> <prize name>`"
                      "\n\nFor the blacklist, mention any users who aren't allowed to compete in "
                      "this giveaway\n\nIf you don't mention a channel, I'll just use the "
                      "channel the command was performed in\n\nThe duration should look "
                      "something like this: `2w` OR `30d12h30m` OR `1d30m` (NO SPACES). The only "
                      "characters supported are `w`, `d`, `h` or `hr`, `m`, and `s`")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx, blacklist: commands.Greedy[discord.Member]=[], channel: typing.Optional[discord.TextChannel]=None, num_winners: typing.Optional[int]=1, duration: str="", *, prize: str=None):
        """**Must have the "Manage Server" permission**
        Start a giveaway/raffle!
        Format like this: `<prefix> giveaway (OPTIONAL)<blacklist> (OPTIONAL)<channel> (OPTIONAL)<number of winners (defaults to 1)> <duration> <prize name>`
        For the blacklist, mention any users who aren't allowed to compete in this giveaway
        If you don't mention a channel, I'll just use the channel the command was performed in
        Note: The duration should look something like this: `2w` OR `30d12h30m` OR `1d30m` (NO SPACES). The only characters supported are `w`, `d`, `h` or `hr`, `m`, and `s`
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
            "msg": msg.id,
            "channel": channel.id,
            "author": ctx.author.id,
            "end_time": end_time,
            "blacklist": [m.id for m in blacklist],
            "winners": num_winners,
            "prize": prize
        }
        self.bot.botdata["giveaways"].append(new_giveaway)
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE botdata
                SET giveaways = $1::JSON[]
            ;""", self.bot.botdata["giveaways"])

    @commands.command(brief="Member not found. Try again")
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str=None):
        """**Must have the "Kick Members" permission**
        Kicks member(s) from the server
        Format like this: `<prefix> kick <@mention member(s)> <reason for kicking>`
        """
        if not members:
            await ctx.send("You didn't format the command correctly, it's supposed to look like "
                           f"this: `{ctx.prefix}kick <@mention member(s)> <reason for kicking>`",
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
            embed = discord.Embed(description="__Reason__: " + reason, color=find_color(ctx))
            embed.set_author(name=f"{ctx.author.name} kicked {kicked[0]} from the server",
                             icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        elif kicked:
            embed = discord.Embed(
                description=f"**Kicked**: `{'`, `'.join(kicked)}`\n__Reason__: " + reason,
                color=find_color(ctx))
            embed.set_author(name=f"{len(kicked)} members were kicked by {ctx.author.name}",
                             icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await send_log(ctx, embed)

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

    @commands.command(brief="Member or channel not found. Try again")
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, members: commands.Greedy[discord.Member], channel: typing.Optional[typing.Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]]=None, duration: str="", *, reason: str=None):
        """**Must have the "Manage Roles" (serverwide) or "Manage Permissions" (channel-specific) permission**
        Mutes a user(s) from sending messages in this server. This is done by assigning them a role with perms that prevents them from sending messages
        Format like this: `<prefix> mute <user(s)> (OPTIONAL)<channel> <duration> (OPTIONAL)<reason>`
        If you include a text, voice, OR category channel, they'll only be muted in that channel. If you don't specify one, they'll be muted for the entire server
        The duration is how long they'll be muted and should look something like this: `1w` OR `2h30m` OR `1d30m` (NO SPACES). The only characters supported are `w`, `d`, `h` or `hr`, `m`, and `s`
        """
        if channel is not None:
            if not ctx.author.permissions_in(channel).manage_roles:
                await ctx.send("You don't have the **Manage Permissions** perm in "
                               f"{channel.mention}, so you can't mute anyone in that channel",
                               delete_after=7.0)
                return await delete_message(ctx, 7)
        else:
            if not ctx.author.guild_permissions.manage_roles:
                raise commands.MissingPermissions(["manage_roles"])
        if not members:
            await ctx.send("You didn't format the command correctly, it's supposed to look like "
                           f"this: `{ctx.prefix}mute <@mention member(s)> (OPTIONAL)<#mention "
                           "channel> <duration> (OPTIONAL)<reason>`\n\nFor the duration, put "
                           "something like `1w`, `12h`, `2h30m`, `45m`, `3d12h5m30s`, etc. and "
                           "that's how long they will be muted", delete_after=15.0)
            return await delete_message(ctx, 15)
        if ctx.guild.me in members:
            return await ctx.send(":rolling_eyes:")

        parsed_duration = pytimeparse.parse(duration)
        if parsed_duration is None:
            await ctx.send("You didn't format the duration correctly. It should look something "
                           "like this: `1w` OR `2h30m` OR `1d30m` (NO SPACES)\n\nThe only "
                           "characters supported are `w`, `d`, `h` or `hr`, `m`, and `s`",
                           delete_after=15.0)
            return await delete_message(ctx, 15)
        elif parsed_duration > 604800 or parsed_duration < 60:
            await ctx.send("The duration must be at least a minute __and__ no longer than a week",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        if reason is None:
            reason = "No reason given"
        if len(reason) + len(ctx.author.name) + 23 > 512:
            max_length = 512 - (len(ctx.author.name) + 23)
            await ctx.send(f"Reason is too long. It must be under {max_length} characters",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        muted, cant_mute = [], []
        temp = await ctx.send("Muting...")
        with ctx.channel.typing():
            if channel is None:
                if self.bot.guilddata[ctx.guild.id]["mute_role"] is None:
                    mute_role = await ctx.guild.create_role(name="Muted",
                                                            color=discord.Color(0x23272A))
                    self.bot.guilddata[ctx.guild.id]["mute_role"] = mute_role.id
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE guilddata
                            SET mute_role = {}
                            WHERE id = {}
                        ;""".format(mute_role.id, ctx.guild.id))
                else:
                    mute_role = ctx.guild.get_role(self.bot.guilddata[ctx.guild.id]["mute_role"])

                for c in ctx.guild.channels:
                    await c.set_permissions(
                        mute_role, send_messages=False, connect=False, add_reactions=False)

                for member in members:
                    if not member.guild_permissions.administrator:
                        await member.add_roles(
                            mute_role, reason=f"{reason} | Action performed by {ctx.author.name}")
                        muted.append(member)
                    else:
                        cant_mute.append(member)
            else:
                for member in members:
                    if not member.guild_permissions.administrator:
                        await channel.set_permissions(
                            member, reason=f"{reason} | Action performed by {ctx.author.name}",
                            send_messages=False, connect=False, add_reactions=False)
                        muted.append(member)
                    else:
                        cant_mute.append(member)

        await temp.delete()

        if channel is None:
            to_send = (f"You have been muted from speaking in the server __{ctx.guild.name}__ "
                       f"for **{duration}** by {ctx.author.mention}")
        else:
            to_send = (f"You have been muted from speaking in the channel {channel.mention} in "
                       f"the server __{ctx.guild.name}__ for **{duration}** by "
                       f"{ctx.author.mention}")
        if reason != "No reason given":
            to_send += f" for this reason:```{reason}```"
        for m in muted:
            await m.send(to_send)

        if len(muted) == 1:
            if channel is None:
                embed = discord.Embed(
                    description=f"__Duration__: {duration}\n__Reason__: {reason}",
                    color=find_color(ctx))
                embed.set_author(name=f"{ctx.author.name} muted {muted[0]} from the server",
                                 icon_url=ctx.author.avatar_url)
            else:
                embed = discord.Embed(
                    description=f"__Channel__: {channel.mention}\n__Duration__: {duration}\n"
                                f"__Reason__: {reason}",
                    color=find_color(ctx))
                embed.set_author(name=f"{ctx.author.name} muted {muted[0]} from a channel",
                                 icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        elif muted:
            if channel is None:
                embed = discord.Embed(
                    description=f"**Muted**: {', '.join(m.mention for m in muted)}\n\n"
                                f"__Duration__: {duration}\n__Reason__: {reason}",
                    color=find_color(ctx))
            else:
                embed = discord.Embed(
                    description=f"**Muted**: {', '.join(m.mention for m in muted)}\n\n"
                                f"__Channel__: {channel.mention}\n__Duration__: {duration}"
                                f"\n__Reason__: {reason}",
                    color=find_color(ctx))
            embed.set_author(name=f"{len(muted)} members were muted by {ctx.author.name}",
                             icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await send_log(ctx, embed)

        if len(cant_mute) == 1:
            embed = discord.Embed(
                title=f"I couldn't mute {cant_mute[0].name}",
                description=f"{cant_mute[0].mention} is an Administrator of this server, so I "
                "couldn't mute them",
                color=find_color(ctx))
            await ctx.send(embed=embed)

        elif cant_mute:
            embed = discord.Embed(
                title="I couldn't mute all the members you listed",
                description="Some of the members you listed are Administrators of this server, "
                "so I couldn't mute them",
                color=find_color(ctx))
            embed.add_field(name="Here are the members I couldn't mute:",
                            value=f"{', '.join(m.mention for m in cant_mute)}")
            await ctx.send(embed=embed)

        await asyncio.sleep(parsed_duration)
        for m in muted:
            try:
                if channel is None:
                    await m.remove_roles(mute_role, reason="The temporary mute assigned by "
                                         f"{ctx.author.name} is over")
                    await m.send(f"You are no longer muted in the server, __{ctx.guild.name}__")
                else:
                    await channel.set_permissions(
                        m, reason=f"The temporary mute assigned by {ctx.author.name} is over",
                        send_messages=None, connect=None, add_reactions=None)
                    await m.send(f"You are no longer muted in the channel, {channel.mention} in "
                                 f"the server, __{ctx.guild.name}__")
            except: #* If something went wrong (e.g. the member left), just ignore it and move on
                continue

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nologs(self, ctx):
        """**Must have the Administrator permission**
        Disables the logs channel
        """
        self.bot.guilddata[ctx.guild.id]["logs"] = 0
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET logs = 0
                WHERE id = {}
            ;""".format(ctx.guild.id))

        await ctx.send(
            "Logging moderation commands has been turned off for this server "
            f"by {ctx.author.mention}. To turn them back on, just use the `setlogs` command.")

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> prune <days>`\n\nInactive members are denoted if they have not "
                      "logged on in `days` number of days and they have no roles.\nAfter running "
                      "this command, you will be shown how many members will be kicked and "
                      "you'll be asked to confirm the operation before I go ahead and actually "
                      "prune the server")
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def prune(self, ctx, days: int):
        """**Must have the "Kick Members" permission**
        Prune the server from its inactive members
        Format like this: `<prefix> prune <days>`
        The inactive members are denoted if they have not logged on in `days` number of days and they have no roles
        After running this command, you will be shown how many members will be kicked and you'll be asked to confirm the operation before I go ahead and actually prune the server
        """
        if days < 1 or days > 30:
            await ctx.send("For the number of days you must put an integer **above 0** and "
                           "**below 31**. Try again", delete_after=6.0)
            return await delete_message(ctx, 6)

        await ctx.channel.trigger_typing()
        est_pruned = await ctx.guild.estimate_pruned_members(days=days)
        if est_pruned == 0:
            await ctx.send(
                f"None of this server's members have been inactive for that long, so no one's "
                "gonna get pruned", delete_after=8.0)
            return await delete_message(ctx, 8)
        confirm = await ctx.send(
            f"Pruning will kick **{est_pruned} member{'' if est_pruned == 1 else 's'}** who have "
            f"not logged on in **{days} day{'' if days == 1 else 's'}** and are not assigned to "
            "any roles. They can rejoin the server using an Instant Invite\n\nReact with "
            "\U00002705 to confirm that you want to prune this server or \U0000274c to cancel")
        await confirm.add_reaction("\U00002705")
        await confirm.add_reaction("\U0000274c")

        try:
            react, user = await self.bot.wait_for(
                "reaction_add", timeout=20, check=self.check_reaction(confirm, ctx.author))
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

        temp = await ctx.send("Pruning...")
        with ctx.channel.typing():
            pruned = await ctx.guild.prune_members(
                days=days, reason="Action performed by " + ctx.author.name)
        await temp.delete()

        if pruned == 1:
            embed = discord.Embed(
                description=f"**1 member** who has not been seen in **{days} "
                f"day{'' if days == 1 else 's'}** was kicked. They can rejoin the server with a "
                "new instant invite", color=find_color(ctx))
        else:
            embed = discord.Embed(
                description=f"**{pruned} members** who have not been seen in **{days} "
                f"day{'' if days == 1 else 's'}** were kicked. They can rejoin the server with a "
                "new instant invite", color=find_color(ctx))
        embed.set_author(name=f"{ctx.guild.name} was pruned by {ctx.author.name}",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.group(aliases=["remove"], invoke_without_command=True)
    async def purge(self, ctx):
        """**Must have the "Manage Messages" permission**
        Mass-deletes messages from a certain channel.
        There are several different ways to use this command. Type just `<prefix> purge` for help
        """
        embed = discord.Embed(
            title="MAT's Purge Command | Help", description="An easy way to mass-delete "
            "messages from a channel!\n\nAdd **one** of these to the command to purge "
            f"messages that fit a certain criteria\n\n__Example usage__: `{ctx.prefix}purge "
            "contains banana`", color=find_color(ctx))

        embed.add_field(name="all (OPTIONAL)<number>", value="Deletes all "
                        "messages in the channel. If you also put in a number, it'll only "
                        "delete that many messages. I default to 1000, and I can't go over "
                        "2000", inline=False)
        embed.add_field(name="clear", value="Completely clears a channel by deleting and "
                        "replacing it with an identical one. I need the **Manage Channels** "
                        "permission in order to do this", inline=False)
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
        embed.add_field(name="before <message link OR date> (OPTIONAL)<number>", value="Deletes "
                        "a certain number of messages that come **before** the one with the "
                        "given link __OR__ date. To get the message link, click the 3 dots next "
                        "to the msg and press `Copy Link`. If you put a date instead, it must be "
                        "formatted like this: `mm-dd-yyyy`. If you don't put a number, I'll "
                        "default to 100. I can go up to 2000", inline=False)
        embed.add_field(name="after <message link OR date> (OPTIONAL)<number>", value="Deletes "
                        "all messages that come **after** the one with the given link __OR__ "
                        "date. To get the message link, click the 3 dots next to the msg and "
                        "press `Copy Link`. If you put a date instead, it must be formatted like "
                        "this: `mm-dd-yyyy`. If you don't put a number, I'll default to 100. I "
                        "can go up to 2000", inline=False)
        embed.add_field(name="around <message link OR date> (OPTIONAL)<number>", value="Deletes "
                        "a certain number of messages sent **around** the one with given link "
                        "__OR__ date. To get the message link, click the 3 dots next to the msg "
                        "and press `Copy Link`. If you put a date instead, it must be formatted "
                        "like this: `mm-dd-yyyy`. If you don't put a number, I'll default to "
                        "101. I can go up to 2000", inline=False)
        embed.add_field(name="reactions", value="Removes all reactions from messages that "
                        "have them", inline=False)
        embed.add_field(name="pins (OPTIONAL)<number to leave pinned>", value="Unpins all "
                        "pinned messages in this channel. You can also specify a certain "
                        "number of messages to leave pinned", inline=False)

        await ctx.send(embed=embed)

    async def remove(self, ctx, limit, check, description: str, before=None, after=None, around=None):
        if limit > 2000:
            await ctx.send(
                "I can't purge more than 2000 messages at a time. Put a smaller number",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        if limit >= 25:
            if ctx.command.name in ["all", "before", "around", "after"]:
                confirm = await ctx.send("React with \U00002705 to confirm that you want to "
                                         "purge 25+ messages in this channel. React with "
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
            purged = await ctx.channel.purge(
                limit=limit, check=check, before=before, after=after, around=around)
        await temp.delete()
        await ctx.message.delete()

        messages = collections.Counter()
        embed = discord.Embed(
            description=f"{len(purged)} {description} in {ctx.channel.mention}",
            color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " ran a purge command",
                         icon_url=ctx.author.avatar_url)
        if len(purged) >= 10:
            await send_log(ctx, embed)

        for m in purged:
            messages[m.author.display_name] += 1
        added_fields = []
        for a, m in messages.items():
            embed.add_field(name=a, value=f"{m} message{'' if m == 1 else 's'}")
            added_fields.append(a)
            if len(added_fields) == 24 and len(messages) > 25:
                authors_left = {a:m for a, m in messages.items() if a not in added_fields}
                embed.add_field(
                    name=f"...and {len(authors_left)} more",
                    value=f"{sum(authors_left.values())} message{'' if m == 1 else 's'}")
                break

        if len(purged) < 10:
            if self.bot.guilddata[ctx.guild.id]["logs"] != 0:
                embed.set_footer(text="The number of messages purged was less than 10, so a log "
                                 "wasn't sent to the logs channel")

        await ctx.send(embed=embed)

    @purge.command(brief="Invalid formatting. You must format the command like this: `<prefix> "
                   "purge after <message link OR date> (OPTIONAL)<number of msgs to delete>`\n\n"
                   "If you don't put a number, I'll defualt to 100. I can go up to 2000\n\nTo "
                   "get the message link, click the 3 dots next to the msg (on mobile, press and "
                   "hold the message) and press `Copy Link`.\n\nIf you put a date instead, it "
                   "must be formatted like this: `mm-dd-yyyy`. Anything else will cause an error."
                   "\n__Example__: `04-03-2019`")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def after(self, ctx, del_after: typing.Union[discord.Message, str], limit: int=100):

        try:
            #* If it's a date instead of a Message object
            if isinstance(del_after, str):
                del_after = datetime.datetime.strptime(del_after, "%m-%d-%Y")
        except:
            raise commands.BadArgument

        if isinstance(del_after, discord.Message):
            await self.remove(
                ctx, limit, None, f"messages after [this one]({del_after.jump_url}) were deleted",
                after=del_after)
        else:
            await self.remove(
                ctx, limit, None, f"messages sent after **{del_after.strftime('%b %-d, %Y')}** "
                "were deleted", after=del_after)

    @purge.command(name="all", brief="Invalid formatting. You must format the command like this: "
                   "`<prefix> purge all (OPTIONAL)<number of msgs to delete>`")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def all_(self, ctx, limit: int=1000):

        await self.remove(ctx, limit, None, "messages were deleted")

    @purge.command(brief="Invalid formatting. You must format the command like this: `<prefix> "
                   "purge around <message link OR date> (OPTIONAL)<number of msgs to delete>`\n\n"
                   "If you don't put a number, I'll defualt to 101. I can go up to 2000\n\nTo "
                   "get the message link, click the 3 dots next to the msg (on mobile, press and "
                   "hold the message) and press `Copy Link`.\n\nIf you put a date instead, it "
                   "must be formatted like this: `mm-dd-yyyy`. Anything else will cause an error."
                   "\n__Example__: `04-03-2019`")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def around(self, ctx, del_around: typing.Union[discord.Message, str], limit: int=101):

        try:
            #* If it's a date instead of a Message object
            if isinstance(del_around, str):
                del_around = datetime.datetime.strptime(del_around, "%m-%d-%Y")
        except:
            raise commands.BadArgument

        if isinstance(del_around, discord.Message):
            await self.remove(
                ctx, limit, None,
                f"messages sent around **{del_around.created_at.strftime('%b %-d, %Y')}** were "
                "deleted", around=del_around)
        else:
            await self.remove(
                ctx, limit, None, f"messages sent around **{del_around.strftime('%b %-d, %Y')}** "
                "were deleted", around=del_around)

    @purge.command(brief="Invalid formatting. You must format the command like this: `<prefix> "
                   "purge before <message link OR date> (OPTIONAL)<number of msgs to delete>`\n\n"
                   "If you don't put a number, I'll defualt to 100. I can go up to 2000\n\nTo "
                   "get the message link, click the 3 dots next to the msg (on mobile, press and "
                   "hold the message) and press `Copy Link`.\n\nIf you put a date instead, it "
                   "must be formatted like this: `mm-dd-yyyy`. Anything else will cause an error."
                   "\n__Example__: `04-03-2019`")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def before(self, ctx, del_before: typing.Union[discord.Message, str], limit: int=100):

        try:
            #* If it's a date instead of a Message object
            if isinstance(del_before, str):
                del_before = datetime.datetime.strptime(del_before, "%m-%d-%Y")
        except:
            raise commands.BadArgument

        if isinstance(del_before, discord.Message):
            await self.remove(
                ctx, limit, None, f"messages before [this one]({del_before.jump_url}) were "
                "deleted", before=del_before)
        else:
            await self.remove(
                ctx, limit, None,
               f"messages sent before **{del_before.strftime('%b %-d, %Y')}** were deleted",
                before=del_before)

    @purge.command()
    @commands.bot_has_permissions(
        manage_messages=True, read_message_history=True, manage_channels=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx):

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
        cleared = await ctx.channel.clone(reason=ctx.author.name + " cleared the channel")
        try:
            await cleared.edit(position=ctx.channel.position)
        except: #* If it's already in place
            pass

        if ctx.channel.id in self.bot.guilddata[ctx.guild.id]["triggers_disabled"]:
            self.bot.guilddata[ctx.guild.id]["triggers_disabled"].remove(ctx.channel.id)
            self.bot.guilddata[ctx.guild.id]["triggers_disabled"].append(cleared.id)
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET triggers_disabled = $1::BIGINT[]
                    WHERE id = {}
                ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["triggers_disabled"])

        embed = discord.Embed(description=cleared.mention + " was completely cleared",
                              color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " ran a purge command",
                         icon_url=ctx.author.avatar_url)

        await cleared.send(embed=embed)
        await send_log(ctx, embed)

    @purge.command(brief="Invalid formatting. You must include a substring for me to look "
                   "for, like this: `<prefix> purge contains <substring>`")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def contains(self, ctx, *, substr: str):

        await self.remove(ctx, 1000, lambda m: re.search(substr, m.content, re.IGNORECASE),
                          f"messages containing the string `{substr}` were deleted")

    @purge.command()
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def embeds(self, ctx):

        await self.remove(
            ctx, 1000, lambda m: len(m.embeds), "messages containing embeds were deleted")

    @purge.command(aliases=["emojis", "emote", "emotes"])
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def emoji(self, ctx):

        def check(m):
            custom_emoji = re.compile(r"<:(\w+):(\d+)>")
            return custom_emoji.search(m.clean_content)

        await self.remove(ctx, 1000, check, "messages containing custom emojis were deleted")

    @purge.command(aliases=["attachments"])
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def files(self, ctx):

        await self.remove(ctx, 1000, lambda m: len(m.attachments),
                          "messages containing attachments were deleted")

    @purge.command(name="bot", aliases=["bots"])
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def from_bot(self, ctx, *, prefix=None):

        def check(m):
            return m.webhook_id is None and m.author.bot or (
                prefix and m.content.startswith(prefix))

        if prefix is None:
            await self.remove(ctx, 1000, check, "messages by bots were deleted")
        else:
            await self.remove(ctx, 1000, check, "messages by bots and messages containing the "
                              f"prefix `{prefix}` were deleted")

    @purge.command(aliases=["user", "members", "users"], brief="Invalid formatting. You must "
                   "format the command like this: `<prefix> purge member <@mention user(s)>`")
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
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.has_permissions(manage_messages=True)
    async def pins(self, ctx, leave: int=None):

        all_pins = await ctx.channel.pins()
        if len(all_pins) == 0:
            await ctx.send("This channel has no pinned messages", delete_after=5.0)
            return await delete_message(ctx, 5)

        temp = await ctx.send("Please wait... This could take some time...")
        unpinned = []
        with ctx.channel.typing():
            for m in all_pins:
                if len(await ctx.channel.pins()) == leave:
                    break
                await m.unpin()
                unpinned.append(m)

        embed = discord.Embed(
            description=f"{len(unpinned)} messages were unpinned in {ctx.channel.mention}",
            color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " ran a purge command",
                         icon_url=ctx.author.avatar_url)

        await ctx.message.delete()
        await temp.delete()
        await ctx.send(embed=embed)
        if len(unpinned) > 0:
            await send_log(ctx, embed)

    @purge.command()
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
            description=f"{total_reactions} reactions were removed from {total_messages} "
            f"messages in {ctx.channel.mention}", color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " ran a purge command",
                         icon_url=ctx.author.avatar_url)

        await ctx.message.delete()
        await temp.delete()
        await ctx.send(embed=embed)
        if total_reactions > 0:
            await send_log(ctx, embed)

    @commands.command(brief="Incorrect formatting. You're supposed to provide a list of "
                      "@mentions or member names that I'll randomly choose from. Or don't put "
                      "anything and I'll randomly pick someone from the server")
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

        embed = discord.Embed(description=str(member) + " was kicked", color=find_color(ctx))
        embed.set_author(name="A randomkick was performed by " + ctx.author.name,
                         icon_url=ctx.author.avatar_url)
        await send_log(ctx, embed)

    @commands.command(aliases=["snipe"])
    @commands.has_permissions(manage_messages=True)
    async def restore(self, ctx):
        """**Must have the "Manage Messages" permission**
        Restores the last deleted message by a non-bot member
        Note: Because of how Discord works, I can't restore attachments to messages, just the text of the message
        """
        last_delete = self.bot.guilddata[ctx.guild.id]["last_delete"]
        if last_delete is None:
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
        embed.set_footer(text="Restored by " + ctx.author.name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rmgoodbye(self, ctx):
        """**Must have Administrator permissions**
        Removes a previously set custom goodbye message
        """
        if self.bot.guilddata[ctx.guild.id]["goodbye"] is None:
            await ctx.send("This server doesn't have a custom goodbye message. Use "
                           "the `setgoodbye` command to make one", delete_after=7.0)
            return await delete_message(ctx, 7)

        self.bot.guilddata[ctx.guild.id]["goodbye"] = None
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET goodbye = NULL
                WHERE id = {}
            ;""".format(ctx.guild.id))

        embed = discord.Embed(description=f"**Message**: ```{msg.format('(member)')}```",
                              color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " REMOVED the custom goodbye message",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rmstarboard(self, ctx):
        """**Must have Administrator permissions**
        Remove a previously set starboard channel
        """
        if self.bot.guilddata[ctx.guild.id]["starboard"] is None:
            await ctx.send("This server doesn't have a starboard channel. Use "
                           "the `setstarboard` command to set one", delete_after=7.0)
            return await delete_message(ctx, 7)

        starboard = self.bot.guilddata[ctx.guild.id]["starboard"]
        self.bot.guilddata[ctx.guild.id]["starboard"] = None
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET starboard = NULL
                WHERE id = {}
            ;""".format(ctx.guild.id))

        embed = discord.Embed(description="Now messages will no longer be sent to "
                              f"{self.bot.get_channel(starboard['channel']).mention} when they "
                              f"get at least {starboard['num_reactions']} \U00002b50 reactions",
                              color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " REMOVED the starboard channel",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rmwelcome(self, ctx):
        """**Must have Administrator permissions**
        Removes a previously set custom welcome message
        """
        if self.bot.guilddata[ctx.guild.id]["welcome"] is None:
            await ctx.send("This server doesn't have a custom welcome message. Use "
                           "the `setwelcome` command to make one", delete_after=7.0)
            return await delete_message(ctx, 7)

        self.bot.guilddata[ctx.guild.id]["welcome"] = None
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET welcome = NULL
                WHERE id = {}
            ;""".format(ctx.guild.id))

        embed = discord.Embed(description=f"**Message**: ```{msg.format('(member)')}```",
                              color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " REMOVED the custom welcome message",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command(brief="Invalid formatting. Format like this: `<prefix> setlogs <mention "
                      "channel or channel name>`.\nTo turn off the logs channel, use "
                      "the `nologs` command")
    @commands.has_permissions(administrator=True)
    async def setlogs(self, ctx, channel: discord.TextChannel):
        """**Must have Administrator permissions**
        Sets a "logs" channel for me to keep a log of all of my moderation commands.
        Format like this: `<prefix> setlogs <mention channel or channel name>`
        To turn off the logs channel, use the `nologs` command
        """
        self.bot.guilddata[ctx.guild.id]["logs"] = channel.id
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET logs = {}
                WHERE id = {}
            ;""".format(channel.id, ctx.guild.id))

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

        self.bot.guilddata[ctx.guild.id]["goodbye"] = {"message": msg, "channel": channel.id}
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET goodbye = $1::JSON
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["goodbye"])

        embed = discord.Embed(description=f"**Channel**: {channel.mention}\n**Message**:"
                              f"```{msg.format('(member)')}```", color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " set a new custom goodbye message",
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setstarboard(self, ctx, channel: discord.TextChannel, num_reactions: int=4):
        """**Must have Administrator permissions**
        Set up a starboard system where people can "star" a funny or otherwise significant message to have it saved in a channel.
        Format like this: `<prefix> setstarboard <#mention channel> <reaction threshold (defaults to 4)>`
        Say the reaction threshold is 4; whenever a message gets at least 4 total "star reactions", a copy of the message will be sent to the starboard channel where it can be saved.
        The "Star Reactions": \U00002b50, \U0001f31f, \U0001f320, or \U00002734
        """
        await ctx.channel.trigger_typing()
        starboard = {
            "channel": channel.id,
            "num_reactions": num_reactions,
            "messages": []
        }
        self.bot.guilddata[ctx.guild.id]["starboard"] = starboard
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET starboard = $1::JSON
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["starboard"])

        embed = discord.Embed(
            description=f"**Channel**: {channel.mention}\n**Reaction Threshold**: {num_reactions}"
            f"\n\nNow, whenever a message gets at least {num_reactions} \U00002b50 reactions, a "
            f"copy of the message will be sent to {channel.mention}", color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " set a starboard channel",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> setwelcome <#mention channel> <welcome message>`\n\nWhen you're "
                      "typing the message, put a pair of braces `{}` in to mark where the new "
                      "member's name will go. It's required that you put the braces in "
                      "there somewhere, but only once")
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

        self.bot.guilddata[ctx.guild.id]["welcome"] = {"message": msg, "channel": channel.id}
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET welcome = $1::JSON
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["welcome"])

        embed = discord.Embed(description=f"**Channel**: {channel.mention}\n**Message**:"
                              f"```{msg.format('(member)')}```", color=find_color(ctx))
        embed.set_author(name=ctx.author.name + " set a new custom welcome message",
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command(brief="Incorrect formatting. The command is supposed to look like this: "
                      "`<prefix> softban <@mention user> (OPTINAL)<days of msgs to delete>`\nThe "
                      "number of days worth of messages to delete must be at least 1 and no more "
                      "than 7. If you don't include it, I'll default to one day")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.User, days: int=1):
        """**Must have the "Ban Members" permission**
        Softban a user, that is, ban them and then immediately unban them to kick them from the server and delete their messages.
        Format like this: `<prefix> softban <@mention user> (OPTINAL)<days of msgs to delete>`
        If you don't include a number of days worth of messages to delete, I'll default to 1.
        """
        if days < 1 or days > 7:
            await ctx.send("The number of days worth of messages to delete must be **at least "
                           "1** and **no more than 7**", delete_after=7.0)
            return await delete_message(ctx, 7)

        if user is self.bot.user:
            return await ctx.send(":rolling_eyes:")

        await ctx.channel.trigger_typing()
        try:
            await ctx.guild.ban(
                user=user, reason=f"Softbanning {user} | Action performed by {ctx.author.name}",
                delete_message_days=days)
            await ctx.guild.unban(
                user=user, reason=f"Softbanning {user} | Action performed by {ctx.author.name}")
        except discord.Forbidden:
            await ctx.send(f"{user.mention} has a role that's higher than mine in the server "
                           "hierarchy, so I couldn't ban them", delete_after=7.0)
            return await delete_message(ctx, 7)

        if days == 1:
            days_text = "day"
        else:
            days_text = f"**{days}** days"
        embed = discord.Embed(description=f"All messages sent by {user.mention} in the past "
                              f"{days_text} have been deleted. They have also been kicked from "
                              "this server", color=find_color(ctx))
        embed.set_author(
            name=f"{ctx.author.name} softbanned {user}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def triggers(self, ctx):
        """**Must have the "Manage Messages" permission**
        Toggles my trigger words on/off for a channel or for the whole server
        To **toggle** trigger words on/off for a single channel, do: `<prefix> triggers toggle`
        To turn trigger words **off** for the entire server, do: `<prefix> triggers all off`
        Finally, to turn trigger words **on** for the entire server, do: `<prefix> triggers all on`
        """
        await ctx.send(
            "To **toggle** trigger words on/off for a single channel, do: `<prefix> triggers "
            "toggle`\n\nTo turn trigger words **off** for the entire server, do: `<prefix> "
            "triggers all off`\n\nFinally, to turn trigger words **on** for the entire server, "
            "do: `<prefix> triggers all on`")

    @triggers.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def all(self, ctx):
        #* Just send the same help message that "triggers" sends
        await ctx.send(
            "To **toggle** trigger words on/off for a single channel, do: `<prefix> triggers "
            "toggle`\n\nTo turn trigger words **off** for the entire server, do: `<prefix> "
            "triggers all off`\n\nFinally, to turn trigger words **on** for the entire server, "
            "do: `<prefix> triggers all on`")

    @all.command()
    @commands.has_permissions(manage_messages=True)
    async def off(self, ctx):

        if ctx.author.guild_permissions.manage_messages:
            for c in ctx.guild.text_channels:
                self.bot.guilddata[ctx.guild.id]["triggers_disabled"].append(c.id)
            await ctx.send("Ok, triggers have been turned off for all channels in this server")
        else:
            await ctx.send("You only have the **Manage Messages** permission for this channel. "
                           "In order to turn off triggers for all channels, you need the server-"
                           "wide **Manage Messages** perm", delete_after=8.0)
            return await delete_message(ctx, 8)

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET triggers_disabled = $1::BIGINT[]
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["triggers_disabled"])

        embed = discord.Embed(color=find_color(ctx))
        embed.set_author(name=f"{ctx.author.name} has DISABLED my triggers for ALL channels",
                         icon_url=ctx.author.avatar_url)
        await send_log(ctx, embed)

    @all.command()
    @commands.has_permissions(manage_messages=True)
    async def on(self, ctx):

        if ctx.author.guild_permissions.manage_messages:
            self.bot.guilddata[ctx.guild.id]["triggers_disabled"].clear()
            await ctx.send("Ok, triggers have been turned on for all channels in this server")
        else:
            await ctx.send("You only have the **Manage Messages** permission for this channel. "
                           "In order to turn triggers on for all channels, you need the server-"
                           "wide **Manage Messages** perm", delete_after=8.0)
            return await delete_message(ctx, 8)

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET triggers_disabled = $1::BIGINT[]
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["triggers_disabled"])

        embed = discord.Embed(color=find_color(ctx))
        embed.set_author(name=f"{ctx.author.name} has ENABLED my triggers for ALL channels",
                         icon_url=ctx.author.avatar_url)
        await send_log(ctx, embed)

    @triggers.command()
    @commands.has_permissions(manage_messages=True)
    async def toggle(self, ctx):

        if ctx.channel.id not in self.bot.guilddata[ctx.guild.id]["triggers_disabled"]:
            self.bot.guilddata[ctx.guild.id]["triggers_disabled"].append(ctx.channel.id)
            await ctx.send("Ok, I'll stop reacting to triggers in this channel")

        elif ctx.channel.id in self.bot.guilddata[ctx.guild.id]["triggers_disabled"]:
            self.bot.guilddata[ctx.guild.id]["triggers_disabled"].remove(ctx.channel.id)
            await ctx.send("Ok, I'll start reacting to triggers in this channel again!")

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET triggers_disabled = $1::BIGINT[]
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["triggers_disabled"])

    @commands.command(brief="User not found in the bans list. To see a list of all banned "
                      "members, use the `allbanned` command.")
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
                f"`{ctx.prefix}unban <user ID(s)> (OPTIONAL)<reason for unbanning>`",
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
            embed = discord.Embed(description="__Reason__: " + reason, color=find_color(ctx))
            embed.set_author(name=f"{ctx.author.name} has unbanned {unbanned[0]} from the server",
                             icon_url=ctx.author.avatar_url)
        else:
            embed = discord.Embed(
                description=f"**Unbanned**: `{'`, `'.join(unbanned)}`\n__Reason__: " + reason,
                color=find_color(ctx))
            embed.set_author(
                name=f"{len(unbanned)} members have been unbanned by {ctx.author.name}",
                icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
