"""
    MAT's Bot: An open-source, general purpose Discord bot written in Python.
    Copyright (C) 2018  NinjaSnail1080  (Discord Username: @NinjaSnail1080#8581)

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

from utils import find_color, delete_message

from discord.ext import commands
import discord
import speedtest

import datetime
import typing
import sys
import asyncio
import collections


class Info(commands.Cog):
    """Information"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        """About me!"""

        app = await self.bot.application_info()

        embed = discord.Embed(
            title=str(self.bot.user), description=app.description +
            f"\n\n**User/Client ID**: {app.id}", color=find_color(ctx))

        embed.set_thumbnail(url=app.icon_url)
        embed.add_field(name="Version", value=self.bot.__version__)
        embed.add_field(name="Author", value=app.owner)
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(
            name="Language",
            value=f"Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
        embed.add_field(
            name="Library", value="[discord.py](https://github.com/Rapptz/discord.py)")
        embed.add_field(
            name="License", value="[GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)")
        embed.add_field(name="Github Repo", value="https://github.com/NinjaSnail1080/MATs-Bot",
                        inline=False)
        embed.set_footer(text=f"Dedicated to {self.bot.get_user(422131370010214402)}")

        await ctx.send(embed=embed)

    @commands.command(aliases=["allbans"])
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def allbanned(self, ctx):
        """Sends a list of all the banned users from the server"""

        await ctx.channel.trigger_typing()
        banned = await ctx.guild.bans()
        if len(banned) == 0:
            return await ctx.send("This server hasn't banned any users yet")

        embed = discord.Embed(title=f"All users banned from {ctx.guild.name}",
                              description=f"Command performed by {ctx.author.mention}",
                              color=find_color(ctx))
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name=f"Banned ({len(banned)})",
            value="\n".join(str(b.user) + f" (ID: {b.user.id})" for b in banned), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def allchannels(self, ctx):
        """Sends a list of all the channels in the server"""

        await ctx.channel.trigger_typing()
        tchannels = ctx.guild.text_channels
        vchannels = ctx.guild.voice_channels

        embed = discord.Embed(title=f"All of the channels in {ctx.guild.name}",
                              description=f"Command performed by {ctx.author.mention}",
                              color=find_color(ctx))

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text="To get information on these channels, use the \"channelinfo\" "
                         "command and I'll provide some basic info on it as long as I have "
                         "access to the channel")
        embed.add_field(
            name=f"Text Channels ({len(tchannels)})",
            value=", ".join(c.mention for c in tchannels), inline=False)
        if vchannels:
            embed.add_field(
                name=f"Voice Channels ({len(vchannels)})",
                value=", ".join(f"\U0001f509{c.name}" for c in vchannels), inline=False)
        else:
            embed.add_field(
                name=f"Voice Channels ({len(vchannels)})", value="None", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def allroles(self, ctx):
        """Sends a list of all the roles in the server"""

        await ctx.channel.trigger_typing()
        embed = discord.Embed(title=f"All of the roles in {ctx.guild.name}",
                              description=f"Command performed by {ctx.author.mention}",
                              color=find_color(ctx))
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name=f"Roles ({len(ctx.guild.roles)})",
            value=", ".join(r.mention for r in ctx.guild.roles[::-1]), inline=False)

        await ctx.send(embed=embed)

    @commands.command(brief="Invalid formatting. You need to format the command like this: "
                      "`<prefix> channelinfo (OPTIONAL)<text channel OR voice channel (case-"
                      "sensitive)>`\n\nIf you don't provide a channel, I'll default to this one")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def channelinfo(self, ctx, *, channel: typing.Union[discord.VoiceChannel, discord.TextChannel]=None):
        """Info about a text or voice channel on this server. By default I'll show info about the channel the command was performed in, although you can specify a different one.
        Format like this: `<prefix> channelinfo (OPTIONAL)<text channel OR voice channel>`
        """
        await ctx.channel.trigger_typing()
        if channel is None:
            c = ctx.channel
        else:
            c = channel

        embed = discord.Embed(color=find_color(ctx))
        if isinstance(c, discord.TextChannel):
            try:
                embed.add_field(name="Channel", value=c.mention)
                embed.add_field(name="ID", value=c.id)
                embed.add_field(name="Category", value=str(c.category))
                embed.add_field(name="Position", value=c.position + 1)
                if await c.pins():
                    embed.add_field(name="Messages Pinned", value=len(await c.pins()))
                else:
                    embed.add_field(name="Messages Pinned", value="None")
                if c.is_nsfw():
                    embed.add_field(name="NSFW?", value="Yes")
                else:
                    embed.add_field(name="NSFW?", value="No")
                embed.add_field(name="Members With Access",
                                value=f"{len(c.members)} out of {c.guild.member_count}")
                if c.overwrites:
                    embed.add_field(name="Overwrites", value=len(c.overwrites))
                else:
                    embed.add_field(name="Overwrites", value="None")
                if c.is_news():
                    embed.add_field(name="News Channel?", value="Yes")
                else:
                    embed.add_field(name="News Channel?", value="No")
                try:
                    if await c.webhooks():
                        embed.add_field(name="Webhooks", value=len(await c.webhooks()))
                    else:
                        embed.add_field(name="Webhooks", value="None")
                except discord.Forbidden:
                    embed.add_field(name="Webhooks", value="Unknown")
                if not c.slowmode_delay:
                    embed.add_field(name="Slowmode Delay", value="Disabled")
                else:
                    embed.add_field(name="Slowmode Delay", value=f"{c.slowmode_delay} seconds")
                embed.add_field(name="Created", value=c.created_at.strftime("%b %-d, %Y"))
                if c.topic is None or c.topic == "":
                    embed.add_field(name="Channel topic", value="```No topic```", inline=False)
                else:
                    embed.add_field(name="Channel topic", value=f"```{c.topic}```", inline=False)

                await ctx.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("Unfortunately, I don't have access to that channel, so I wasn't "
                               "able to get information from it", delete_after=7.0)
                return await delete_message(ctx, 7)

        elif isinstance(c, discord.VoiceChannel):
            try:
                embed.add_field(name="Channel", value=f"\U0001f509{c.name}")
                embed.add_field(name="ID", value=c.id)
                embed.add_field(name="Category", value=str(c.category))
                embed.add_field(name="Position", value=c.position + 1)
                if c.user_limit == 0:
                    embed.add_field(name="User Limit", value="No limit")
                else:
                    embed.add_field(name="User Limit", value=c.user_limit)
                embed.add_field(name="Bitrate", value=f"{c.bitrate // 1000} kbps")
                if c.members:
                    embed.add_field(name="Members Inside", value=len(c.members))
                else:
                    embed.add_field(name="Members Inside", value="No members inside")
                if c.overwrites:
                    embed.add_field(name="Overwrites", value=len(c.overwrites))
                else:
                    embed.add_field(name="Overwrites", value="None")
                embed.add_field(name="Created", value=c.created_at.strftime("%b %-d, %Y"))

                await ctx.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("Unfortunately, I don't have access to that channel, so I wasn't "
                               "able to get information from it", delete_after=7.0)
                return await delete_message(ctx, 7)

    @commands.command(aliases=["emoteinfo"], brief="That's either not an emoji or it's one of "
                      "Discord's default emojis. You must put a custom emoji after the command "
                      "so I can get info on it")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def emojiinfo(self, ctx, emoji: discord.Emoji=None):
        """Info about an emoji. Only works with custom emojis.
        Format like this: `<prefix> emojiinfo <emoji>`
        """
        if emoji is None:
            await ctx.send("You need to include an emoji after the command. Keep in mind that it "
                           "only works with custom emojis.", delete_after=7.0)
            return await delete_message(ctx, 7)

        await ctx.channel.trigger_typing()
        emoji = await ctx.guild.fetch_emoji(emoji.id)
        #* To gain access to the "user" attribute

        embed = discord.Embed(title=f"Info On The {emoji} Emoji", color=find_color(ctx))

        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="Name", value=emoji.name)
        embed.add_field(name="ID", value=emoji.id)
        if emoji.require_colons:
            embed.add_field(name="Requires Colons?", value="Yes")
        else:
            embed.add_field(name="Requires Colons?", value="No")
        if emoji.animated:
            embed.add_field(name="Animated?", value="Yes")
        else:
            embed.add_field(name="Animated?", value="No")
        if emoji.managed:
            embed.add_field(name="Managed By Integration?", value="Yes")
        else:
            embed.add_field(name="Managed By Integration?", value="No")
        embed.add_field(
            name="Created On", value=emoji.created_at.strftime("%b %-d, %Y"))
        embed.add_field(
            name="Created By", value=f"{emoji.user.mention} (User ID: {emoji.user.id})",
            inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["perms", "memberperms"], brief="Invalid formatting. The command "
                      "is supposed to look like this: `<prefix> permissions (OPTIONAL)<@mention "
                      "member> (OPTIONAL)<#mention channel>`\nIf you don't put a member, I'll "
                      "use you. If you don't put a channel, I'll use the channel the command "
                      "was performed in")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def permissions(self, ctx, member: typing.Optional[discord.Member]=None, channel: typing.Union[discord.VoiceChannel, discord.TextChannel]=None):
        """Get a member's permissions in a channel
        Format like this: `<prefix> permissions (OPTIONAL)<@mention member> (OPTIONAL)<text OR voice channel>`
        If you don't put a member, I'll use you. If you don't put a channel, I'll use the channel the command was performed in
        ~~RIP mobile users~~
        """
        await ctx.channel.trigger_typing()
        if member is None:
            member = ctx.author
        if channel is None:
            channel = ctx.channel

        perms = dict(iter(member.permissions_in(channel)))

        if isinstance(channel, discord.TextChannel):
            embed = discord.Embed(
                description=f"**Permissions for {member.mention} in {channel.mention}**",
                color=find_color(ctx))
            for i in [_p for _p, _v in dict(iter(discord.Permissions.voice())).items() if _v]:
                perms.pop(i, None)
        elif isinstance(channel, discord.VoiceChannel):
            embed = discord.Embed(
                description=f"**Permissions for {member.mention} in \U0001f509{channel.name}**",
                color=find_color(ctx))
            for i in [_p for _p, _v in dict(iter(discord.Permissions.text())).items() if _v]:
                perms.pop(i, None)

        for p, v in perms.items():
            if v:
                embed.add_field(name=p.replace("_", " ").replace("guild", "server").replace(
                    "activation", "activity").title().replace("Tts", "TTS"), value="\U00002705")
            else:
                embed.add_field(name=p.replace("_", " ").replace("guild", "server").replace(
                    "activation", "activity").title().replace("Tts", "TTS"), value="\U0000274c")

        await ctx.send(embed=embed)

    @commands.command(aliases=["latency"])
    async def ping(self, ctx):
        """Get the bot's ping/latency in milliseconds"""

        await ctx.send(":ping_pong: My Discord WebSocket protocol latency/ping is about "
                       f"`{round(self.bot.latency * 1000, 2)}ms`")

    @commands.command(brief="Role not found. Try again (Role name is case-sensitive)")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roleinfo(self, ctx, *, role: discord.Role=None):
        """Info about a role on this server.
        Format like this: `<prefix> roleinfo <role name>`
        Note: Role name is case-sensitive
        """
        await ctx.channel.trigger_typing()
        if role is None:
            await ctx.send(
                "You need to include the name of a role after the command so I can get info on "
                f"it, like this:\n`{ctx.prefix}roleinfo <role name>`\nNote: Role name is "
                "case-sensitive", delete_after=9.0)
            return await delete_message(ctx, 9)

        embed = discord.Embed(color=find_color(ctx))
        embed.add_field(name="Role", value=role.mention)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Color", value=role.color)
        if role.managed:
            embed.add_field(name="Managed by Integration?", value="Yes")
        else:
            embed.add_field(name="Managed by Integration?", value="No")
        if role.hoist:
            embed.add_field(name="Displays Separately?", value="Yes")
        else:
            embed.add_field(name="Displays Separately?", value="No")
        if role.mentionable:
            embed.add_field(name="Mentionable?", value="Yes")
        else:
            embed.add_field(name="Mentionable?", value="No")
        embed.add_field(name="Position", value=role.position)
        embed.add_field(name="Members With Role",
                        value=f"{len(role.members)} out of {ctx.guild.member_count}")
        embed.add_field(name="Created", value=role.created_at.strftime("%b %-d, %Y"))

        perms = "`, `".join([p.replace("_", " ").replace("guild", "server").replace(
            "activation", "activity").capitalize().replace("Tts", "TTS") for p, v in dict(iter(
                role.permissions)).items() if v])
        if perms == "":
            embed.add_field(name="Permissions", value="`None`", inline=False)
        else:
            embed.add_field(
                name="Permissions", value=f"`{perms}`", inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["guildinfo"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def serverinfo(self, ctx):
        """Info about the server"""

        await ctx.channel.trigger_typing()
        s = ctx.guild

        on_members = [m for m in s.members if m.status is not discord.Status.offline]
        bots = [m for m in s.members if m.bot]
        anim_emojis = [e for e in s.emojis if e.animated]

        embed = discord.Embed(
            title=s.name, description=f"Server ID: {s.id}", color=find_color(ctx))
        embed.set_thumbnail(url=s.icon_url)
        embed.set_image(url=s.banner_url)

        embed.add_field(
            name="Members", value=f"{s.member_count} (Online: {len(on_members)})")
        embed.add_field(name="Roles", value=len(s.roles))
        embed.add_field(name="Text Channels", value=len(s.text_channels))
        embed.add_field(name="Voice Channels", value=len(s.voice_channels))
        embed.add_field(name="Categories", value=len(s.categories))
        if anim_emojis:
            embed.add_field(
                name="Custom Emojis",
                value=f"{len(s.emojis)} out of {s.emoji_limit} (Animated: {len(anim_emojis)})")
        else:
            embed.add_field(name="Custom Emojis", value=f"{len(s.emojis)} out of {s.emoji_limit}")
        embed.add_field(name="Bots", value=len(bots))
        try:
            if await s.webhooks():
                embed.add_field(name="Webhooks", value=len(await s.webhooks()))
            else:
                embed.add_field(name="Webhooks", value="None")
        except:
            embed.add_field(name="Webhooks", value="Unknown")
        embed.add_field(name="File Size Upload Limit", value=f"{s.filesize_limit // 1000000} MB")
        embed.add_field(name="Bitrate Limit", value=f"{int(s.bitrate_limit // 1000)} kbps")
        if s.premium_tier:
            embed.add_field(name="Nitro Server Boost Status", value=f"Level {s.premium_tier}")
        else:
            embed.add_field(name="Nitro Server Boost Status", value="No Levels Achieved")
        if s.premium_subscription_count:
            embed.add_field(name="Nitro Server Boosts", value=s.premium_subscription_count)
        else:
            embed.add_field(name="Nitro Server Boosts", value="None")
        if s.system_channel is not None:
            embed.add_field(name="System Channel", value=s.system_channel.mention)
        else:
            embed.add_field(name="System Channel", value="No System Channel")
        embed.add_field(name="Region", value=str(s.region).replace(
            "-", " ").replace("south", "south ").replace("hong", "hong ").title().replace(
                "Us", "U.S.").replace("Eu", "EUR").replace("Vip", "V.I.P."))
        if s.mfa_level:
            embed.add_field(name="Requires 2FA?", value="Yes")
        else:
            embed.add_field(name="Requires 2FA?", value="No")
        embed.add_field(name="Default Notification Level",
                        value=str(s.default_notifications)[18:].replace("_", " ").title())
        embed.add_field(name="Verification Level", value=str(s.verification_level).capitalize())
        embed.add_field(name="Explicit Content Filter",
                        value=str(s.explicit_content_filter).replace("_", " ").title())
        if s.afk_channel is not None:
            if s.afk_timeout // 60 == 1:
                minute_s = " minute"
            else:
                minute_s = " minutes"
            embed.add_field(
                name="AFK Channel", value="\U0001f509" + s.afk_channel.name + " after " + str(
                    s.afk_timeout // 60) + minute_s)
        else:
            embed.add_field(name="AFK Channel", value="No AFK channel")
        embed.add_field(name="Server Created", value=s.created_at.strftime("%b %-d, %Y"))
        if s.features:
            embed.add_field(
                name="Server Features",
                value="`" + "`, `".join([f.replace("_", " ") for f in s.features]) + "`",
                inline=False)
        embed.add_field(
            name="Server Owner", value=s.owner.mention + " (User ID: " + str(s.owner_id) + ")",
            inline=False)
        embed.add_field(name="Total Messages I've Read",
                        value=f"{self.bot.messages_read[str(s.id)]:,}",
                        inline=False)
        if self.bot.guilddata[s.id]["commands_used"]:
            cmds_used = collections.Counter(
                self.bot.guilddata[s.id]["commands_used"]).most_common(11)[1:]
            total = self.bot.guilddata[s.id]["commands_used"]["TOTAL"]
            embed.add_field(
                name="Most Popular Commands",
                value=f"__**Total**:__ {total:,} uses\n" + "\n".join(
                      f"**{cmds_used.index(c) + 1}**. `{c[0]}` ({c[1]} uses)" for c in cmds_used),
                inline=False)

        delta = datetime.datetime.utcnow() - s.created_at

        y = int(delta.total_seconds()) // 31557600  #* Number of seconds in 365.25 days
        mo = int(delta.total_seconds()) // 2592000 % 12  #* Number of seconds in 30 days
        d = int(delta.total_seconds()) // 86400 % 30  #* Number of seconds in 1 day
        h = int(delta.total_seconds()) // 3600 % 24  #* Number of seconds in 1 hour
        mi = int(delta.total_seconds()) // 60 % 60  #* etc.
        se = int(delta.total_seconds()) % 60

        footer = []
        if y != 0:
            footer.append(f"{y} {('year' if y == 1 else 'years')}, ")
        if mo != 0:
            footer.append(f"{mo} {'month' if mo == 1 else 'months'}, ")
        if d != 0:
            footer.append(f"{d} {'day' if d == 1 else 'days'}, ")
        if h != 0:
            footer.append(f"{h} {'hour' if h == 1 else 'hours'}, ")
        if mi != 0:
            footer.append(f"{mi} {'minute' if mi == 1 else 'minutes'}, ")
        footer.append(f"and {se} {'second' if se == 1 else 'seconds'}.")

        embed.set_footer(text=s.name + " has been around for roughly " + "".join(footer))

        await ctx.send(embed=embed)

    @commands.command(name="speedtest")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def speedtest_(self, ctx):
        """Test the current ping, download, and upload speeds of MY Wi-Fi network"""

        tester = speedtest.Speedtest()

        temp = await ctx.send("Retrieving speedtest.net server list...")
        with ctx.channel.typing():
            await self.bot.loop.run_in_executor(None, tester.get_servers)
            await asyncio.sleep(1)
            await temp.edit(content="Retrieving speedtest.net server list... "
                                    "Selecting best server based on ping...")
            await self.bot.loop.run_in_executor(None, tester.get_best_server)
            await asyncio.sleep(1)
            await temp.edit(content="Testing download speed... Please wait...")
            await self.bot.loop.run_in_executor(None, tester.download)
            await temp.edit(content="Testing upload speed... Please wait...")
            await self.bot.loop.run_in_executor(None, tester.upload)
            await self.bot.loop.run_in_executor(None, tester.results.share)
            await temp.delete()

        embed = discord.Embed(title="Speedtest Results of MAT's Wi-Fi Network",
                              color=find_color(ctx))
        embed.set_image(url=tester.results.dict()["share"])
        embed.set_footer(
            text=f"Test performed by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        """See some of my stats"""

        await ctx.channel.trigger_typing()
        cmds_used = self.bot.commands_used.most_common(11)[1:]

        embed = discord.Embed(
            description=f"User ID: {self.bot.user.id}",
            timestamp=datetime.datetime.utcnow(),
            color=find_color(ctx))
        embed.add_field(name="Server Count", value=f"{len(self.bot.guilds):,} servers")
        embed.add_field(name="User Count", value=f"{len(self.bot.users):,} unique users")
        embed.add_field(
            name="Channel Count",
            value=f"{len(list(self.bot.get_all_channels()) + self.bot.private_channels):,} "
                  "channels")
        embed.add_field(
            name="Memory Usage",
            value=f"{round(self.bot.process.memory_info().rss / 1000000, 2)} MB")
        embed.add_field(name="Total Messages Read", value=f"{self.bot.messages_read['TOTAL']:,}")
        embed.add_field(name="Total Commands Used", value=f"{self.bot.commands_used['TOTAL']:,}")
        embed.add_field(
            name="Most Popular Commands",
            value="\n".join(
                f"**{cmds_used.index(c) + 1}**. `{c[0]}` ({c[1]} total uses)" for c in cmds_used),
            inline=False)
        embed.set_author(name="MAT's Bot: Statistics", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="These statistics are accurate as of:")

        await ctx.send(embed=embed)

    @commands.command(name="uptime")
    async def uptime_(self, ctx):
        """Get my uptime, or how long I've been running since the last time I was started up"""

        uptime = datetime.datetime.utcnow() - self.bot.started_at

        y = int(uptime.total_seconds()) // 31557600  #* Number of seconds in 356.25 days
        mo = int(uptime.total_seconds()) // 2592000 % 12  #* Number of seconds in 30 days
        d = int(uptime.total_seconds()) // 86400 % 30  #* Number of seconds in 1 day
        h = int(uptime.total_seconds()) // 3600 % 24  #* Number of seconds in 1 hour
        mi = int(uptime.total_seconds()) // 60 % 60  #* etc.
        se = int(uptime.total_seconds()) % 60

        frmtd_uptime = []
        if y != 0:
            frmtd_uptime.append(f"**{y}** {'**year**' if y == 1 else '**years**'}, ")
        if mo != 0:
            frmtd_uptime.append(f"**{mo}** {'**month**' if mo == 1 else '**months**'}, ")
        if d != 0:
            frmtd_uptime.append(f"**{d}** {'**day**' if d == 1 else '**days**'}, ")
        if h != 0:
            frmtd_uptime.append(f"**{h}** {'**hour**' if h == 1 else '**hours**'}, ")
        if mi != 0:
            if len(frmtd_uptime) == 0:
                frmtd_uptime.append(f"**{mi}** {'**minute**' if mi == 1 else '**minutes**'} ")
            else:
                frmtd_uptime.append(f"**{mi}** {'**minute**' if mi == 1 else '**minutes**'}, ")
        if len(frmtd_uptime) == 0:
            frmtd_uptime.append(f"**{se}** {'**second**' if se == 1 else '**seconds**'}")
        else:
            frmtd_uptime.append(f"and **{se}** {'**second**' if se == 1 else '**seconds**'}")

        frmtd_started_at = self.bot.started_at.strftime("%B %-d, %Y at %-I:%M %p UTC")

        await ctx.send(f"I've been online for about {''.join(frmtd_uptime)} since I was last "
                       f"started up on __{frmtd_started_at}__")

    @commands.command(aliases=["memberinfo"], brief="User not found. Try again")
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def userinfo(self, ctx, user: discord.Member=None):
        """Info about a user. By default I'll show your user info, but you can specify a different member of your server.
        Format like this: `<prefix> userinfo (OPTIONAL)<@mention user>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author

        roles = [f"`{r.name}`" for r in user.roles if r.name != "@everyone"][::-1]

        if user.activity is not None:
            if user.activity.type is discord.ActivityType.listening:
                _type = "Listening to"
                activity = user.activity.title
            elif user.activity.type is discord.ActivityType.streaming:
                _type = "Streaming"
                activity = user.activity.name
            elif user.activity.type is discord.ActivityType.watching:
                _type = "Watching"
                activity = user.activity.name
            else:
                _type = "Playing"
                activity = user.activity.name
        else:
            _type = "Playing"
            activity = "Nothing"

        if user.status is discord.Status.online:
            status = "https://i.imgur.com/WcPjzNt.png"
        elif user.status is discord.Status.idle:
            status = "https://i.imgur.com/UdRIQ2S.png"
        elif user.status is discord.Status.dnd:
            status = "https://i.imgur.com/voWO5qd.png"
        else:
            status = "https://i.imgur.com/8OOawcF.png"

        embed = discord.Embed(description=f"User ID: {user.id}", color=find_color(ctx))

        embed.set_author(name=str(user), icon_url=status)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Display Name", value=user.display_name)
        embed.add_field(
            name="Status", value=str(user.status).replace("dnd", "do not disturb").title())
        if user.mobile_status is not discord.Status.offline or user.is_on_mobile():
            embed.add_field(name="Platform", value="Mobile")
        elif user.desktop_status is not discord.Status.offline:
            embed.add_field(name="Platform", value="Desktop")
        elif user.web_status is not discord.Status.offline:
            embed.add_field(name="Platform", value="Web")
        else:
            embed.add_field(name="Platform", value="None")
        embed.add_field(name=_type, value=activity)
        embed.add_field(name="Color", value=str(user.color))
        if user.voice is not None:
            embed.add_field(name="Voice Channel", value="\U0001f509" + user.voice.channel.name)
            if user.voice.mute or user.voice.self_mute:
                embed.add_field(name="Muted?", value="Yes")
            else:
                embed.add_field(name="Muted?", value="No")
            if user.voice.deaf or user.voice.self_deaf:
                embed.add_field(name="Deafened?", value="Yes")
            else:
                embed.add_field(name="Deafened?", value="No")
        else:
            embed.add_field(name="Voice Channel", value="None")
        if user.top_role is ctx.guild.default_role:
            embed.add_field(name="Top Role", value=user.top_role.name)
        else:
            embed.add_field(name="Top Role", value=user.top_role.mention)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%b %-d, %Y"))
        if user.bot:
            embed.add_field(name="Bot?", value="Yes")
        else:
            embed.add_field(name="Bot?", value="No")
        embed.add_field(name="Joined Discord", value=user.created_at.strftime("%b %-d, %Y"))
        if roles:
            embed.add_field(
                name=f"Roles ({len(roles)})", value=", ".join(roles), inline=False)
        else:
            embed.add_field(name="Roles", value="`No roles`")
        if user.id in self.bot.userdata:
            if self.bot.userdata[user.id]["commands_used"]:
                cmds_used = collections.Counter(
                    self.bot.userdata[user.id]["commands_used"]).most_common(11)[1:]
                total = self.bot.userdata[user.id]["commands_used"]["TOTAL"]
                list_cmds_used = list(
                    f"**{cmds_used.index(c) + 1}**. `{c[0]}` ({c[1]} uses)" for c in cmds_used)
                embed.add_field(
                    name="Most Used Commands",
                    value=f"__**Total**__: {total:,} uses\n" + "\n".join(list_cmds_used),
                    inline=False)

        delta = datetime.datetime.utcnow() - user.created_at

        y = int(delta.total_seconds()) // 31557600  #* Number of seconds in 356.25 days
        mo = int(delta.total_seconds()) // 2592000 % 12  #* Number of seconds in 30 days
        d = int(delta.total_seconds()) // 86400 % 30  #* Number of seconds in 1 day
        h = int(delta.total_seconds()) // 3600 % 24  #* Number of seconds in 1 hour
        mi = int(delta.total_seconds()) // 60 % 60  #* etc.
        se = int(delta.total_seconds()) % 60

        footer = []
        if y != 0:
            footer.append(f"{y} {'year' if y == 1 else 'years'}, ")
        if mo != 0:
            footer.append(f"{mo} {'month' if mo == 1 else 'months'}, ")
        if d != 0:
            footer.append(f"{d} {'day' if d == 1 else 'days'}, ")
        if h != 0:
            footer.append(f"{h} {'hour' if h == 1 else 'hours'}, ")
        if mi != 0:
            footer.append(f"{mi} {'minute' if mi == 1 else 'minutes'}, ")
        footer.append(f"and {se} {'second' if se == 1 else 'seconds'}.")

        embed.set_footer(
            text=user.name + " has been on Discord for roughly " + "".join(footer))

        if user.premium_since is not None:
            await ctx.send(content="\U0001f537 This member is a Nitro server booster since "
                                   f"{user.premium_since.strftime('%b %-d, %Y')}!",
                           embed=embed)
        else:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
