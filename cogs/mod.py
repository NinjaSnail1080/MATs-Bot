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


async def send_log(guild, send_embed):
    #TODO: Implement the server.data.json file into this
    """Creates a #logs channel if it doesn't already exist so people can keep track of what the
    mods are doing. Then send the embed from a moderation command
    """
    logs = None
    for c in guild.text_channels:
        if re.search("logs", c.name):
            logs = c
            break
    if logs is None:
        logs = await guild.create_text_channel(
            "logs", overwrites={guild.default_role: discord.PermissionOverwrite(
                send_messages=False)})
        await logs.send("I created this channel just now to keep a log of all my moderation "
                        "commands that have been used. Feel free to edit this channel "
                        "however you'd like, but make sure I always have access to it!"
                        "\n\nP.S. I don't have to use this channel if you don't want me to. "
                        "You could make an entirely new channel and as long as it has the "
                        "word, \"logs\" in its name, I'll be able to use it.")
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

    @commands.group(aliases=["remove", "delete"])
    @commands.guild_only()
    async def purge(self, ctx):
        """**Must have the "Manage Messages" permission**
        Mass-deletes messages from a certain channel"""

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

            embed.add_field(name="all (OPTIONAL)<number>", value="Deletes all messages in the "
                            "channel. If you also put in a number, it'll only delete that many "
                            "messages", inline=False)
            embed.add_field(name="member <mention user(s) or username(s)>", value="Deletes all "
                            "messages by a certain member or members of the server", inline=False)
            embed.add_field(name="contains <substring>", value="Deletes all messages that "
                            "contain a substring, which must be specified", inline=False)
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
        purged = await ctx.channel.purge(limit=limit, check=check, before=ctx.message)
        await ctx.message.delete()

        messages = collections.Counter()
        embed = discord.Embed(
            title=ctx.author.display_name + " ran a purge command",
            description=f"{len(purged)} {description} in {ctx.channel.mention}",
            color=find_color(ctx))
        if len(purged) > 0:
            await send_log(ctx.guild, embed)

        for m in purged:
            messages[m.author.display_name] += 1
        for a, m in messages.items():
            embed.add_field(name=a, value=f"{m} messages")

        await ctx.send(embed=embed)

    @purge.command(brief="Invalid formatting. You must format the command like this: `<prefix> "
                   "purge all (OPTIONAL)<number of messages to delete>`", name="all")
    async def _all(self, ctx, limit: int=None):

        await self.remove(ctx, limit, None, "messages were deleted")

    @purge.command(name="bot", aliases=["bots"])
    async def _bot(self, ctx, *, prefix=None):

        def check(m):
            return m.webhook_id is None and m.author.bot or (
                prefix and m.content.startswith(prefix))

        if prefix is None:
            await self.remove(ctx, None, check, "messages by bots were deleted")
        else:
            await self.remove(ctx, None, check, "messages by bots and messages containing the "
                              "prefix `{}` were deleted".format(prefix))

    @purge.command()
    async def contains(self, ctx, *, substr):

        await self.remove(ctx, None, lambda m: substr in m.content,
                          f"messages containing `{substr}` were deleted")

    @purge.command()
    async def embeds(self, ctx):

        await self.remove(
            ctx, None, lambda m: len(m.embeds), "messages containing embeds were deleted")

    @purge.command(aliases=["emojis", "emote", "emotes"])
    async def emoji(self, ctx):

        def check(m):
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            return custom_emoji.search(m.content)

        await self.remove(ctx, None, check, "messages containing custom emojis were deleted")

    @purge.command(aliases=["attachments"])
    async def files(self, ctx):

        await self.remove(ctx, None, lambda m: len(m.attachments),
                          "messages containing attachments were deleted")

    @purge.command(aliases=["user", "members", "users"], brief="Invalid formatting. You must "
                   "format the command like this: `<prefix> purge member <@memtion user(s) or "
                   "username(s)>`")
    async def member(self, ctx, *users: discord.Member):

        users = list(u.display_name for u in users)
        if not users:
            raise commands.BadArgument

        await self.remove(ctx, None, lambda m: m.author.display_name in users,
                          "messages by __{}__ were deleted".format("__, __".join(list(users))))

    @purge.command(brief="Invalid formatting. You're supposed to format the command like this: "
                   "`<prefix> purge pins (OPTIONAL)<number to leave pinned>`")
    async def pins(self, ctx, leave: int=None):

        all_pins = await ctx.channel.pins()
        if len(all_pins) == 0:
            return await ctx.send("This channel has no pinned messages!")

        temp = await ctx.send("Please wait... This could take some time...")
        with ctx.channel.typing():
            for m in all_pins:
                await m.unpin()
                if leave is not None:
                    if len(await ctx.channel.pins()) <= leave:
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
            async for m in ctx.channel.history(limit=None, before=ctx.message):
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
                name="Message", value="*The message was too long to put here, so I'll send "
                "it after this embed.*", inline=False)
        embed.add_field(name="Channel", value=last_delete["channel"])
        embed.set_footer(text="Restored by " + ctx.author.display_name)
        await ctx.send(embed=embed)
        if len(f"```{last_delete['content']}```") > 1024:
            await ctx.send(f"```{last_delete['content']}```")
        # await send_log(ctx.guild, embed)

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
