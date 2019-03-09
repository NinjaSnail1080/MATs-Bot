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

from utils import find_color, delete_message, __version__

from discord.ext import commands
import discord

import datetime
import typing


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
        embed.add_field(name="Version", value=__version__)
        embed.add_field(name="Author", value=app.owner)
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(name="Language", value="Python 3.6.4")
        embed.add_field(name="Library", value="discord.py (rewrite)")
        embed.add_field(name="License", value="GPL v3.0")
        embed.add_field(name="Github Repo", value="https://github.com/NinjaSnail1080/MATs-Bot",
                        inline=False)
        embed.set_footer(text="Dedicated to WooMAT1417#1142")

        await ctx.send(embed=embed)

    @commands.command(aliases=["allbans"])
    @commands.guild_only()
    async def allbanned(self, ctx):
        """Sends a list of all the banned users from the server"""

        await ctx.channel.trigger_typing()
        try:
            banned = await ctx.guild.bans()
        except discord.Forbidden:
            return await ctx.send("I'm sorry, but I don't have the proper perms to view the "
                                  "banned members. For that I need the Ban Members permission")
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
                value=", ".join(c.mention for c in vchannels), inline=False)
        else:
            embed.add_field(
                name=f"Voice Channels ({len(vchannels)})", value="None", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
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
    async def channelinfo(self, ctx, channel: typing.Union[discord.VoiceChannel, discord.TextChannel]=None):
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
                if await c.pins():
                    embed.add_field(name="Messages Pinned", value=len(await c.pins()))
                else:
                    embed.add_field(name="Messages Pinned", value="None")
                embed.add_field(name="Position", value=c.position + 1)
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
                if c.user_limit == 0:
                    embed.add_field(name="User Limit", value="No limit")
                else:
                    embed.add_field(name="User Limit", value=c.user_limit)
                embed.add_field(name="Position", value=c.position + 1)
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
    async def emojiinfo(self, ctx, emoji: discord.Emoji=None):
        """Info about an emoji. Only works with custom emojis.
        Format like this: `<prefix> emojiinfo <emoji>`
        """
        if emoji is None:
            await ctx.send("You need to include an emoji after the command. Keep in mind that it "
                           "only works with custom emojis.", delete_after=7.0)
            return await delete_message(ctx, 7)

        embed = discord.Embed(
            title=f"Info on the {emoji} emoji", color=find_color(ctx))

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
            name="Created", value=emoji.created_at.strftime("%b %-d, %Y"))
        embed.add_field(name="URL", value=emoji.url, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["guildinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Info about the server"""

        await ctx.channel.trigger_typing()
        s = ctx.guild

        on_members = []
        for m in s.members:
            if m.status != discord.Status.offline:
                on_members.append(m)

        bots = []
        for m in s.members:
            if m.bot:
                bots.append(m)

        anim_emojis = []
        for e in s.emojis:
            if e.animated:
                anim_emojis.append(e)

        embed = discord.Embed(
            title=s.name, description=f"Server ID: {s.id}", color=find_color(ctx))

        embed.set_thumbnail(url=s.icon_url)
        embed.add_field(
            name="Members", value=f"{s.member_count} (Online: {len(on_members)})")
        embed.add_field(name="Roles", value=len(s.roles))
        embed.add_field(name="Text Channels", value=len(s.text_channels))
        embed.add_field(name="Voice Channels", value=len(s.voice_channels))
        embed.add_field(name="Categories", value=len(s.categories))
        if anim_emojis:
            embed.add_field(
                name="Custom Emojis", value=f"{len(s.emojis)} (Animated: {len(anim_emojis)})")
        else:
            embed.add_field(name="Custom Emojis", value=len(s.emojis))
        embed.add_field(name="Bots", value=len(bots))
        embed.add_field(name="Region", value=str(
            s.region).replace("-", " ").title().replace("Us", "U.S.").replace("Eu", "EU"))
        embed.add_field(name="Verification Level", value=str(s.verification_level).capitalize())
        embed.add_field(name="Explicit Content Filter",
                        value=str(s.explicit_content_filter).replace("_", " ").title())
        if s.afk_channel is not None:
            if s.afk_timeout // 60 == 1:
                minute_s = " minute"
            else:
                minute_s = " minutes"
            embed.add_field(
                name="AFK Channel", value=s.afk_channel.mention + " after " + str(
                    s.afk_timeout // 60) + minute_s)
        else:
            embed.add_field(name="AFK Channel", value="No AFK channel")
        embed.add_field(
            name="Server Created", value=s.created_at.strftime("%b %-d, %Y"))
        if s.features:
            embed.add_field(
                name="Server Features", value="`" + "`, `".join(s.features) + "`", inline=False)
        embed.add_field(
            name="Server Owner", value=s.owner.mention + " (User ID: " + str(s.owner_id) + ")",
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

    @commands.command(brief="User not found. Try again")
    @commands.guild_only()
    async def userinfo(self, ctx, user: discord.Member=None):
        """Info about a user. By default I'll show your user info, but you can specify a different member of your server.
        Format like this: `<prefix> userinfo (OPTIONAL)<@mention user or user's name/id>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author

        roles = []
        for r in user.roles:
            if r.name != "@everyone":
                roles.append(f"`{r.name}`")
        roles = roles[::-1]

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
        embed.add_field(name="Status", value=str(user.status).title())
        embed.add_field(name="Color", value=str(user.color))
        embed.add_field(name=_type, value=activity)
        embed.add_field(name="Top Role", value=user.top_role)
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

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
