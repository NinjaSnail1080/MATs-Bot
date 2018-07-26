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
        Kicks a member from the server.
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

    @commands.command(hidden=True, aliases=["remove"])
    @commands.guild_only()
    async def purge(self, ctx, number: int):
        """HEAVY WIP. Do not use"""

        if ctx.author.permissions_in(ctx.channel).manage_messages:
            if number is not None:
                await ctx.channel.purge(limit=number + 1)

    @commands.command(brief="Incorrect formatting. You're supposed to provide a list of "
                      "@mentions or member names that I'll randomly choose from. Or don't put "
                      "anything and I'll randomly pick someone from the server")
    @commands.guild_only()
    async def randomkick(self, ctx, **members: discord.Member):
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
            member = random.choice(list(members))
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
        Restores the last deleted message"""

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
