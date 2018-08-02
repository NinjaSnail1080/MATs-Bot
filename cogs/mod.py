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

from mat import find_color, get_data, dump_data
from discord.ext import commands
import discord
import asyncio

import random
import collections
import re

#TODO: Fix the many problems I'm facing rn with how the commands interact with the json data files


async def send_log(guild, send_embed):
    """Creates a #logs channel if it doesn't already exist so people can keep track of what the
    mods are doing. Then send the embed from a moderation command
    """
    serverdata = get_data("server")
    import pprint
    pprint.pprint(serverdata, indent=4)
    if serverdata[str(guild.id)]["logs"] == "false":
        return
    elif serverdata[str(guild.id)]["logs"] == "null":
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
    else:
        logs = guild.get_channel(int(serverdata[str(guild.id)]["logs"]))

    await logs.send(embed=send_embed)


class Moderation:
    """Moderation tools"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Member not found. Try again")
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member=None, *, reason=None):
        """**Must have the "kick members" permission**
        Kicks a member from the server
        Format like this: `<prefix> kick <member> <reason for kicking>`
        """
        if not ctx.author.permissions_in(ctx.channel).kick_members:
            await ctx.send("You don't have permission to kick members", delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        if member is None:
            await ctx.send(
                "You didn't format the command correctly. It's supposed to look like this: "
                "`<prefix> kick <@mention member or member's name/id> <reason for kicking>`",
                delete_after=10.0)
            await asyncio.sleep(10)
            return await ctx.message.delete()
        elif member == ctx.guild.me:
            return await ctx.send(":rolling_eyes:")

        if reason is None:
            reason = "No reason given"
        if len(reason) + len(ctx.author.name) + 23 > 512:
            await ctx.send("Reason is too long. It must be under %d characters" % abs(
                len(ctx.author.name) + 23 - 512), delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        embed = discord.Embed(
            color=find_color(ctx), title=member.name + " was kicked by " + ctx.author.name,
            description="__Reason__: " + reason)
        try:
            await member.kick(reason=reason + " | Action performed by " + ctx.author.name)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            return await ctx.send(
                f"I don't have permissions to kick **{member.display_name}**. What's the point "
                "of having all these moderation commmands if I can't use them?\nEither I don't "
                "have perms to kick, period, or my role is too low. Can one of you guys in "
                "charge fix that please?")
        await send_log(ctx.guild, embed)

    @commands.command()
    @commands.guild_only()
    async def nologs(self, ctx):
        """**Must have the "Manage Server" permission**
        Disables the logs channel
        """
        if not ctx.author.permissions_in(ctx.channel).manage_guild:
            await ctx.send("You need the Manage Server permission in order to use this command",
                           delete_after=5.0)
            await asyncio.sleep(5.0)
            return await ctx.message.delete()

        serverdata = get_data("server")
        serverdata[str(ctx.guild.id)]["logs"] = "false"
        dump_data(serverdata, "server")

        await ctx.send(
            "Logging moderation commands has been turned off for this server "
            "by {}. To turn them back on, just use the `setlogs` command.".format(
                ctx.author.mention))

    @commands.group(aliases=["remove", "delete"])
    @commands.guild_only()
    async def purge(self, ctx):
        """**Must have the "Manage Messages" permission**
        Mass-deletes messages from a certain channel
        """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            await ctx.send("You need the Manage Messages permission in order to use that command",
                           delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        if (not ctx.guild.me.permissions_in(ctx.channel).manage_messages or
                not ctx.guild.me.permissions_in(ctx.channel).read_message_history):
            return await ctx.send(
                "I don't have the proper permissions to execute this command. I need the Manage "
                "Messages perm and the Read Message History perm. Could one of you guys in "
                "charge fix that and then get back to me?")

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
                            "replacing it with an identical one. I need the Manage Channels "
                            "permission in order to do this.", inline=False)
            embed.add_field(name="member <mention user(s) or username(s)>", value="Deletes all "
                            "messages by a certain member or members of the server", inline=False)
            embed.add_field(name="contains <substring>", value="Deletes all messages that "
                            "contain a substring, which must be specified (not case-sensitive)",
                            inline=False)
            embed.add_field(name="files", value="Deletes all messages with files attached to "
                            "them", inline=False)
            embed.add_field(name="embeds", value="Deletes all messages with embeds (The messages "
                            "with a colored line off to the side, like this one. This means a "
                            "lot of bot messages will be deleted, along with any links and/or "
                            "videos that were posted)", inline=False)
            embed.add_field(name="bot (OPTIONAL)<bot prefix>", value="Deletes all messages by "
                            "bots. If you add in a bot's prefix I'll also delete all messages "
                            "that contain that prefix", inline=False)
            embed.add_field(name="emoji", value="Deletes all messages that contain a custom "
                            "emoji", inline=False)
            embed.add_field(name="reactions", value="Removes all reactions from messages that "
                            "have them", inline=False)
            embed.add_field(name="pins (OPTIONAL)<number to leave pinned>", value="Unpins all "
                            "pinned messages in this channel. You can also specify a certain "
                            "number of messages to leave pinned.", inline=False)

            await ctx.send(embed=embed)

    async def remove(self, ctx, limit, check, description: str):
        if limit > 2000:
            await ctx.send("I can't purge more than 2000 messages. Put in a smaller number.",
                           delete_after=7.0)
            await asyncio.sleep(7)
            return await ctx.message.delete()

        temp = await ctx.send("Purging...")
        with ctx.channel.typing():
            purged = await ctx.channel.purge(limit=limit, check=check, before=ctx.message)
        await temp.delete()
        await ctx.message.delete()

        messages = collections.Counter()
        embed = discord.Embed(
            title=ctx.author.display_name + " ran a purge command",
            description=f"{len(purged)} {description} in {ctx.channel.mention}",
            color=find_color(ctx))
        if len(purged) >= 10:
            await send_log(ctx.guild, embed)

        for m in purged:
            messages[m.author.name] += 1
        for a, m in messages.items():
            embed.add_field(name=a, value=f"{m} messages")

        if len(purged) < 10:
            serverdata = get_data("server")
            if serverdata[str(ctx.guild.id)]["logs"] != "false":
                embed.set_footer(text="The number of messages purged was less than 10, so a log "
                                 "wasn't sent to the logs channel")
        await ctx.send(embed=embed)

    @purge.command(name="all", brief="Invalid formatting. You must format the command like this: "
                   "`<prefix> purge all (OPTIONAL)<number of messages to delete>`")
    async def _all(self, ctx, limit: int=1000):

        await self.remove(ctx, limit, None, "messages were deleted")

    @purge.command(name="bot", aliases=["bots"])
    async def _bot(self, ctx, *, prefix=None):

        def check(m):
            return m.webhook_id is None and m.author.bot or (
                prefix and m.content.startswith(prefix))

        if prefix is None:
            await self.remove(ctx, 1000, check, "messages by bots were deleted")
        else:
            await self.remove(ctx, 1000, check, "messages by bots and messages containing the "
                              "prefix `{}` were deleted".format(prefix))

    @purge.command()
    async def clear(self, ctx):
        if not ctx.guild.me.permissions_in(ctx.channel).manage_channels:
                return await ctx.send("I need the Manage Channels permission in order to do this "
                                      "command. Hey mods! You mind fixing that?")
        name = ctx.channel.name
        perms = dict(ctx.channel.overwrites)
        cat = ctx.channel.category
        topic = ctx.channel.topic
        pos = ctx.channel.position
        nsfw = ctx.channel.is_nsfw()

        await ctx.channel.delete(reason=ctx.author.display_name + " cleared the channel")
        cleared = await ctx.guild.create_text_channel(name=name, overwrites=perms, category=cat)
        await cleared.edit(topic=topic, position=pos, nsfw=nsfw)

        embed = discord.Embed(
            title=ctx.author.display_name + " ran a purge command",
            description=cleared.mention + " was completely cleared", color=find_color(ctx))

        await cleared.send(embed=embed)
        await send_log(ctx.guild, embed)

    @purge.command()
    async def contains(self, ctx, *, substr: str):

        await self.remove(ctx, 1000, lambda m: re.search(substr, m.content, re.IGNORECASE),
                          f"messages containing the string, `{substr}`, were deleted")

    @purge.command()
    async def embeds(self, ctx):

        await self.remove(
            ctx, 1000, lambda m: len(m.embeds), "messages containing embeds were deleted")

    @purge.command(aliases=["emojis", "emote", "emotes"])
    async def emoji(self, ctx):

        def check(m):
            custom_emoji = re.compile(r"<:(\w+):(\d+)>")
            return custom_emoji.search(m.content)

        await self.remove(ctx, 1000, check, "messages containing custom emojis were deleted")

    @purge.command(aliases=["attachments"])
    async def files(self, ctx):

        await self.remove(ctx, 1000, lambda m: len(m.attachments),
                          "messages containing attachments were deleted")

    @purge.command(aliases=["user", "members", "users"], brief="Invalid formatting. You must "
                   "format the command like this: `<prefix> purge member <@memtion user(s) or "
                   "username(s)>`")
    async def member(self, ctx, *users: discord.Member):

        users = list(users)
        if not users:
            raise commands.BadArgument

        await self.remove(ctx, 1000, lambda m: m.author in users,
                          "messages by {} were deleted".format(
                              ", ".join(list(u.mention for u in users))))

    @purge.command(brief="Invalid formatting. You're supposed to format the command like this: "
                   "`<prefix> purge pins (OPTIONAL)<number to leave pinned>`")
    async def pins(self, ctx, leave: int=None):

        all_pins = await ctx.channel.pins()
        if len(all_pins) == 0:
            await ctx.send("This channel has no pinned messages", delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        temp = await ctx.send("Please wait... This could take some time...")
        with ctx.channel.typing():
            for m in all_pins:
                await m.unpin()
                if leave is not None:
                    if len(await ctx.channel.pins()) == leave:
                        break

        embed = discord.Embed(
            title=ctx.author.display_name + " ran a purge command",
            description=f"{len(all_pins)} messages were unpinned in {ctx.channel.mention}",
            color=find_color(ctx))

        await ctx.message.delete()
        await temp.delete()
        await ctx.send(embed=embed)
        await send_log(ctx.guild, embed)

    @purge.command()
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
            title=ctx.author.display_name + " ran a purge command",
            description=f"{total_reactions} reactions were removed from {total_messages} "
            "messages", color=find_color(ctx))

        await ctx.message.delete()
        await temp.delete()
        await ctx.send(embed=embed)
        if total_reactions > 0:
            await send_log(ctx.guild, embed)

    @commands.command(brief="Incorrect formatting. You're supposed to provide a list of "
                      "@mentions or member names that I'll randomly choose from. Or don't put "
                      "anything and I'll randomly pick someone from the server")
    @commands.guild_only()
    async def randomkick(self, ctx, *members: discord.Member):
        """**Must have the "kick members" permission**
        Kicks a random member, feeling lucky?
        Format like this: `<prefix> randomkick (OPTIONAL)<list of members you want me to randomly pick from>`.
        If you don't mention anyone, I'll randomly select someone from the server.
        """
        if not ctx.author.permissions_in(ctx.channel).kick_members:
            await ctx.send("You don't have permission to kick members", delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        rip_list = ["rip", "RIP", "Rip in spaghetti, never forgetti", "RIPeroni pepperoni",
                    "RIP in pieces", "Rest in pieces"]
        try:
            member = random.choice(members)
        except IndexError:
            member = random.choice(ctx.guild.members)

        try:
            await member.kick(
                reason="Unlucky individual selected by the randomkick performed by " +
                ctx.author.display_name)
            temp = await ctx.send("And the unlucky individual about to be kicked is...")
            with ctx.channel.typing():
                await asyncio.sleep(2)
                await temp.delete()
                await ctx.send(embed=discord.Embed(
                    color=find_color(ctx), title=member.name + "!!!",
                    description=random.choice(rip_list)))
        except discord.Forbidden:
            return await ctx.send(
                "Damn, it looks like I don't have permission to kick this person. Could one of "
                "you guys check my role to make sure I have either the Kick Members privilege or "
                "the Administrator privilege?\n\nIf I already, do, then I probably picked "
                "someone with a role higher than mine. So try again, or better yet, put my role "
                "above everyone else's. Then we can make this *really* interesting...")
        await send_log(ctx.guild, discord.Embed(
            title="A randomkick was performed by " + ctx.author.display_name,
            description=member.name + " was kicked", color=find_color(ctx)))

    @commands.command(aliases=["snipe"])
    @commands.guild_only()
    async def restore(self, ctx):
        """**Must have the "Manage Messages" permission**
        Restores the last deleted message. I can't restore uploaded files though, unfortunately
        """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            await ctx.send("You need the Manage Messages permission in order to use this command",
                           delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        try:
            last_delete = get_data("server")[str(ctx.guild.id)]["last_delete"]
        except:
            await ctx.send(
                "Unable to find the last deleted message. Sorry!", delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        if last_delete['content'] == "":
            await ctx.send(
                "I can't restore this message. It was probably a file or something, and I can't "
                "restore uploaded files. Sorry!", delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        embed = discord.Embed(
            title="Restored last deleted message",
            description=f"**Sent by**: {last_delete['author']}\n" + last_delete["creation"],
            color=find_color(ctx))
        if len(f"```{last_delete['content']}```") <= 1024:
            embed.add_field(
                name="Message", value=f"```{last_delete['content']}```", inline=False)
        else:
            embed.add_field(
                name="Message", value="*The message was too long to put here*", inline=False)
        embed.set_footer(text="Restored by " + ctx.author.display_name)

        await ctx.send(embed=embed)
        if len(f"```{last_delete['content']}```") > 1024:
            await ctx.send(f"The restored message that was too long to send in the above embed"
                           ":```{}```".format(last_delete['content']))

        embed.add_field(name="Channel", value=last_delete["channel"])
        await send_log(ctx.guild, embed)

    @commands.command(brief="Invalid formatting. Format like this: `<prefix> setlogs <mention "
                      "channel or channel name>`.\nTo turn off the logs channel, use "
                      "the `nologs` command")
    @commands.guild_only()
    async def setlogs(self, ctx, channel: discord.TextChannel=None):
        """**Must have the "Manage Server" permission**
        Sets a "logs" channel for me to keep a log of all of my moderation commands.
        Format like this: `<prefix> setlogs <mention channel or channel name>`
        To turn off the logs channel, use the `nologs` command
        """
        if not ctx.author.permissions_in(ctx.channel).manage_guild:
            await ctx.send("You need the Manage Server permission in order to use this command",
                           delete_after=5.0)
            await asyncio.sleep(5.0)
            return await ctx.message.delete()

        if channel is None:
            raise commands.BadArgument

        serverinfo = get_data("server")
        serverinfo[str(ctx.guild.id)]["logs"] = str(channel.id)
        dump_data(serverinfo, "server")

        await ctx.send(f"The logs channel is now set to {channel.mention}!")
        await channel.send(
            f"This is now the new logs channel, set by {ctx.author.mention}. Whenever "
            "someone uses one of my moderation commands, a message will be sent here to keep "
            "a log of them.")

    @commands.command()
    @commands.guild_only()
    async def toggle(self, ctx):
        """**Must have the "Manage Messages" permission**
        Toggles my trigger words on/off for the channel the command was performed in
        """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            await ctx.send("You need the Manage Messages permission in order to use this command",
                           delete_after=5.0)
            await asyncio.sleep(5)
            return await ctx.message.delete()

        serverdata = get_data("server")
        triggers = serverdata[str(ctx.guild.id)]["triggers"]

        if triggers[str(ctx.channel.id)] == "true":
            triggers[str(ctx.channel.id)] = "false"
            embed = discord.Embed(
                title=ctx.author.display_name + " has turned off my trigger words!",
                description="**Channel Affected**: " + ctx.channel.mention,
                color=find_color(ctx))
            await ctx.send("Ok, I'll stop reacting to triggers in this channel")

        elif triggers[str(ctx.channel.id)] == "false":
            triggers[str(ctx.channel.id)] = "true"
            embed = discord.Embed(
                title=ctx.author.display_name + " has turned my trigger words back on!",
                description="**Channel Affected**: " + ctx.channel.mention,
                color=find_color(ctx))
            await ctx.send("Ok, I'll start reacting to triggers in this channel again!")

        serverdata[str(ctx.guild.id)]["triggers"] = triggers
        dump_data(serverdata, "server")


def setup(bot):
    bot.add_cog(Moderation(bot))
