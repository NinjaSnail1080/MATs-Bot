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

from discord.ext import commands
from bs4 import BeautifulSoup
from PIL import Image
import discord

import datetime
import asyncio
import random
import functools
import os
import io
import re
import uuid

import config


class CommandDisabled(commands.CommandError):
    """Raised when the user attempts to use a command that has been disabled by a server admin via the "disable" command"""
    pass


class ChannelNotNSFW(commands.CommandError):
    """Raised when the user attempts to use an NSFW command in a non-NSFW channel"""
    pass


class VoteRequired(commands.CommandError):
    """Raised when a user attempts to use a vote-locked command without having voted"""


def chunks(L, s):
    """Yield s-sized chunks from L"""

    for i in range(0, len(L), s):
        yield L[i:i + s]


def has_voted():
    """Checks if user has voted for the bot"""

    async def predicate(ctx):
        try:
            if (await ctx.bot.dbl.get_user_vote(ctx.author.id) or
                    await ctx.bot.is_owner(ctx.author)):
                return True
            else:
                raise VoteRequired
        except AttributeError: #* If it's on the experimental bot
            return True

    return commands.check(predicate)


async def delete_message(ctx, time: float):
    """Deletes a command's message after a certain amount of time"""

    try:
        await ctx.message.delete(delay=time)
    except discord.Forbidden:
        pass
    return


async def send_log(ctx, send_embed):
    """Creates a #logs channel if it doesn't already exist so people can keep track of what the
    mods are doing. Then send the embed from a moderation command
    """
    if ctx.bot.guilddata[ctx.guild.id]["logs"] is None:
        logs = await ctx.guild.create_text_channel(
            "logs", overwrites={ctx.guild.default_role: discord.PermissionOverwrite(
                send_messages=False)})

        await logs.send("I created this channel just now to keep a log of all my moderation "
                        "commands that have been used. Feel free to edit this channel "
                        "however you'd like, but make sure I always have access to it!"
                        "\n\nP.S. I don't have to use this channel if you don't want me to. You "
                        "can use the `setlogs` command to set a different logs channel or "
                        "the `nologs` command to disable logging moderation commands entirely.")

        ctx.bot.guilddata[ctx.guild.id]["logs"] = logs.id
        async with ctx.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET logs = {}
                WHERE id = {}
            ;""".format(logs.id, ctx.guild.id))

    elif not ctx.bot.guilddata[ctx.guild.id]["logs"]:
        return
    else:
        logs = ctx.guild.get_channel(ctx.bot.guilddata[ctx.guild.id]["logs"])

    await logs.send(embed=send_embed)


async def send_basic_paginator(ctx, embeds, timeout: int, wrap_ends: bool=True):
    """Send the basic embed paginator with 2 reactions"""

    def check_reaction(message):
        def check(reaction, user):
            if reaction.message.id != message.id or user == ctx.bot.user:
                return False
            elif reaction.emoji == "\U00002b05":
                return True
            elif reaction.emoji == "\U000027a1":
                return True
            return False
        return check

    index = 0
    msg = await ctx.send(embed=embeds[index])
    while True:
        await msg.edit(embed=embeds[index])
        if wrap_ends:
            await msg.add_reaction("\U00002b05")
            await msg.add_reaction("\U000027a1")
        else:
            if index == 0:
                await msg.add_reaction("\U000027a1")
            elif index == len(embeds) - 1:
                await msg.add_reaction("\U00002b05")
            else:
                await msg.add_reaction("\U00002b05")
                await msg.add_reaction("\U000027a1")
        try:
            react, user = await ctx.bot.wait_for(
                "reaction_add", timeout=datetime.timedelta(minutes=timeout).total_seconds(),
                check=check_reaction(msg))
        except asyncio.TimeoutError:
            break
        if react.emoji == "\U00002b05":
            index -= 1
        elif react.emoji == "\U000027a1":
            index += 1
        if index > len(embeds) - 1 or index < -len(embeds) + 1:
            index = 0
        await msg.clear_reactions()
    await msg.delete()
    return await ctx.message.delete()


async def send_advanced_paginator(ctx, embeds, timeout: int):
    """Send the advanced embed paginator with 3 reactions"""

    def check_reaction(message):
        def check(reaction, user):
            if reaction.message.id != message.id or user == ctx.bot.user:
                return False
            elif reaction.emoji in ["\U000025c0", "\U000025b6", "\U0001f522"]:
                return True
            return False
        return check

    def check_message(author, channel):
        def check(message):
            return message.author == author and message.channel == channel
        return check

    index = 0
    msg = await ctx.send(embed=embeds[index])
    for e in ["\U000025c0", "\U000025b6", "\U0001f522"]:
        await msg.add_reaction(e)

    while True:
        try:
            react, user = await ctx.bot.wait_for(
                "reaction_add", timeout=datetime.timedelta(minutes=timeout).total_seconds(),
                check=check_reaction(msg))
        except asyncio.TimeoutError:
            break
        if react.emoji == "\U000025c0":
            index -= 1
        elif react.emoji == "\U000025b6":
            index += 1
        elif react.emoji == "\U0001f522":
            jump_msg = await ctx.send(
                f"{user.mention}, type the page number you'd like to jump to")
            while True:
                try:
                    message = await ctx.bot.wait_for(
                        "message", timeout=10, check=check_message(user, ctx.channel))
                except asyncio.TimeoutError:
                    await jump_msg.delete()
                    await ctx.send(f"{user.mention} took too long to respond, so the "
                                    "operation was cancelled", delete_after=5.0)
                    break
                if message.content.isdigit():
                    if int(message.content) >= 1 and int(message.content) <= len(embeds):
                        index = int(message.content) - 1
                    else:
                        await ctx.send("Invalid page number", delete_after=3.0)
                else:
                    await ctx.send("That's not a page number", delete_after=3.0)
                await jump_msg.delete()
                await message.delete()
                break
        await msg.remove_reaction(react, user)

        if index > len(embeds) - 1 or index < -len(embeds) + 1:
            index = 0
        await msg.edit(embed=embeds[index])

    await msg.delete()
    return await ctx.message.delete()


async def get_reddit(ctx, level: int, limit: int, img_only: bool, include_timestamp: bool, error_msg: str, *subs):
    """Get a random post from a subreddit"""

    try:
        async with ctx.bot.session.get(
            f"https://www.reddit.com/r/{'+'.join(subs)}/hot.json?limit={limit}",
            headers=config.R_USER_AGENT) as w:

            resp = await w.json()

        is_nsfw = False
        for p in resp["data"]["children"].copy():
            if p["data"]["stickied"] or p["data"]["pinned"]:
                resp["data"]["children"].remove(p)
                continue
            if p["data"]["over_18"] and not ctx.channel.is_nsfw():
                resp["data"]["children"].remove(p)
                is_nsfw = True
                continue
            if img_only:
                if not p["data"]["url"].lower().endswith(("jpg", "jpeg", "png", "gif", "webp")):
                    if "imgur.com" in p["data"]["url"] and "/a/" not in p["data"]["url"]:
                        fix = p
                        fix["data"]["url"] += ".png"
                        resp["data"]["children"][resp["data"]["children"].index(p)] = fix
                    else:
                        resp["data"]["children"].remove(p)

        data = random.choice(resp["data"]["children"])["data"]

        #* To format some special characters (like &, <, >, etc.) correctly
        data["title"] = BeautifulSoup(data["title"], "lxml").get_text()
        data["selftext"] = BeautifulSoup(data["selftext"], "lxml").get_text()

        #* To change reddit spoiler markers into discord spoiler markers
        data["selftext"] = data["selftext"].replace(">!", "||").replace("!<", "||")

        #* To change the html code for a zero-width space into something Python can understand
        zwspace = re.compile("&#x200b;", re.IGNORECASE)
        data["title"] = zwspace.sub("\u200B", data["title"])
        data["selftext"] = zwspace.sub("\u200B", data["selftext"])

        if len(data["title"]) > 256:
            data["title"] = data["title"][:253] + "..."

        if level == 1:
            if len(data["selftext"]) > 2048:
                data["selftext"] = ("*Sorry, but this content is too long for me to send in "
                                    "a single message. Click on the title above to go "
                                    "straight to the post*")
            if include_timestamp:
                embed = discord.Embed(
                    title=data["title"], description=data["selftext"],
                    timestamp=datetime.datetime.utcfromtimestamp(data["created_utc"]),
                    url="https://www.reddit.com" + data["permalink"], color=find_color(ctx))
            else:
                embed = discord.Embed(
                    title=data["title"], description=data["selftext"],
                    url="https://www.reddit.com" + data["permalink"], color=find_color(ctx))

            if data["url"].lower().endswith(("jpg", "jpeg", "png", "gif", "bmp", "webp")):
                embed.set_image(url=data["url"])
            else:
                if data["thumbnail"] != "self":
                    embed.set_thumbnail(url=data["thumbnail"])
            if ctx.command.cog_name == "NSFW":
                embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")
            else:
                embed.set_footer(text=f"👍 - {data['score']}")

            return await ctx.send(embed=embed)

        elif level == 2:
            description = (f"By [u/{data['author']}](http://www.reddit.com/user"
                           f"/{data['author']})\n\n")
            if len(data["selftext"]) > 2048 - len(description):
                data["selftext"] = ("*Sorry, but this content is too long for me to send in "
                                    "a single message. Click on the title above to go "
                                    "straight to the post*")
            if include_timestamp:
                embed = discord.Embed(
                    title=data["title"], description=f"By [u/{data['author']}](http://www.reddit."
                    f"com/user/{data['author']})\n\n{data['selftext']}",
                    timestamp=datetime.datetime.utcfromtimestamp(data["created_utc"]),
                    url="https://www.reddit.com" + data["permalink"], color=find_color(ctx))
            else:
                embed = discord.Embed(
                    title=data["title"], description=f"By [u/{data['author']}](http://www.reddit."
                    f"com/user/{data['author']})\n\n{data['selftext']}",
                    url="https://www.reddit.com" + data["permalink"], color=find_color(ctx))

            if data["url"].lower().endswith(("jpg", "jpeg", "png", "gif", "webp")):
                embed.set_image(url=data["url"])
            else:
                if data["thumbnail"] != "self":
                    embed.set_thumbnail(url=data["thumbnail"])

            if ctx.command.name == "reddit":
                embed.set_author(name=f"Random post from {data['subreddit_name_prefixed']}",
                                 url=f"https://www.reddit.com/{data['subreddit_name_prefixed']}")
            else:
                embed.set_author(name=data["subreddit_name_prefixed"],
                                 url=f"https://www.reddit.com/{data['subreddit_name_prefixed']}")
            embed.set_footer(
                text=f"👍 - {data['score']}\u3000💬 - {data['num_comments']}")

            return await ctx.send(embed=embed)

    except Exception as e:
        if isinstance(e, KeyError) or isinstance(e, IndexError):
            if not is_nsfw:
                await ctx.send("This subreddit doesn't exist. Try again", delete_after=5.0)
                return await delete_message(ctx, 5)
            else:
                await ctx.send("This subreddit is NSFW, which means you must be in an "
                               "NSFW-marked channel in order to get a post from it",
                               delete_after=7.0)
                return await delete_message(ctx, 7)
        else:
            await ctx.send(f"Huh, something went wrong and I wasn't able to get {error_msg}. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)


def find_color(ctx):
    """Find the bot's rendered color. If it's the default color or we're in a DM, return Discord's "blurple" color"""

    try:
        if ctx.guild.me.color == discord.Color.default():
            color = discord.Color.blurple()
        else:
            color = ctx.guild.me.color
    except AttributeError:  #* If it's a DM channel
        color = discord.Color.blurple()
    return color


async def send_nekobot_image(ctx, resp):
    """Send an image for a command that called the NekoBot API"""

    if not resp["success"]:
        await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                       "again later", delete_after=5.0)
        return await delete_message(ctx, 5)

    embed = discord.Embed(color=find_color(ctx))
    embed.set_image(url=resp["message"])
    embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")

    await ctx.send(embed=embed)


async def send_dank_memer_img(ctx, resp, is_gif: bool=False):
    """Send an image for a command that called the Dank Memer Imgen API"""

    def save_image(resp):
        if is_gif:
            filepath = f"{ctx.command.name}-{uuid.uuid4()}.gif"
            with open(filepath, "wb") as f:
                f.write(resp)
        else:
            img = Image.open(io.BytesIO(resp))
            filepath = f"{ctx.command.name}-{uuid.uuid4()}.png"
            img.save(filepath)
        return filepath

    try:
        filepath = await ctx.bot.loop.run_in_executor(None, functools.partial(save_image, resp))
        filename = ctx.command.name + filepath[-4:]

        f = discord.File(filepath, filename=filename)
        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url=f"attachment://{filename}")
        embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")

        await ctx.send(file=f, embed=embed)
    except:
        await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                       "again later", delete_after=5.0)
        await delete_message(ctx, 5)
    finally:
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
        except:
            pass
