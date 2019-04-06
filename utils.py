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
import discord
import aiohttp
from PIL import Image
import rapidjson as json

import datetime
import asyncio
import random
import functools
import os
import io
import re
import sys
import uuid

import config

__version__ = open("VERSION.txt").readline()


class CommandDisabled(commands.CommandError):
    """Raised when the user attempts to use a command that has been disabled by a server admin via the "disable" command"""
    pass


class ChannelNotNSFW(commands.CommandError):
    """Raised when the user attempts to use an NSFW command in a non-NSFW channel"""
    pass


def get_data(to_return=None):
    """Gets data from all of the .data.json file"""

    if os.path.exists("bot.data.json"):
        with open("bot.data.json", "r") as f:
            botdata = dict(json.load(f))
    else:
        with open("bot.data.json", "w") as f:
            botdata = {"messages_read": {}, "commands_used": {}}
            json.dump(botdata, f)

    if os.path.exists("server.data.json"):
        with open("server.data.json", "r") as f:
            serverdata = dict(json.load(f))
    else:
        with open("server.data.json", "w") as f:
            serverdata = {}
            json.dump(serverdata, f)

    if os.path.exists("user.data.json"):
        with open("user.data.json", "r") as f:
            userdata = dict(json.load(f))
    else:
        with open("user.data.json", "w") as f:
            userdata = {}
            json.dump(userdata, f)

    if os.path.exists("reminders.data.json"):
        with open("reminders.data.json", "r") as f:
            reminders = list(json.load(f))
    else:
        with open("reminders.data.json", "w") as f:
            reminders = []
            json.dump(reminders, f)

    if os.path.exists("giveaways.data.json"):
        with open("giveaways.data.json", "r") as f:
            giveaways = list(json.load(f))
    else:
        with open("giveaways.data.json", "w") as f:
            giveaways = []
            json.dump(giveaways, f)

    if to_return is None:
        return
    elif to_return == "bot":
        return botdata
    elif to_return == "server":
        return serverdata
    elif to_return == "user":
        return userdata
    elif to_return == "reminders":
        return reminders
    elif to_return == "giveaways":
        return giveaways
    else:
        raise TypeError("\"to_return\" param must be either \"bot\", \"server\", \"user\", "
                        "\"reminders\", or \"giveaways\"")


def dump_data(to_dump, file):
    """Dumps data to the .data.json files"""

    if file == "bot":
        with open("bot.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)

    elif file == "server":
        with open("server.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)

    elif file == "user":
        with open("user.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)

    elif file == "reminders":
        with open("reminders.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)

    elif file == "giveaways":
        with open("giveaways.data.json", "w") as f:
            json.dump(to_dump, f, indent=4)
    else:
        raise TypeError("\"file\" param must be either \"bot\", \"server\", \"user\", "
                        "\"reminders\", or \"giveaways\"")


async def delete_message(ctx, time: float):
    """Deletes a command's message if the command was formatted incorectly"""

    await asyncio.sleep(time)
    try:
        await ctx.message.delete()
    except:
        pass
    return


async def get_reddit(ctx, level: int, limit: int, img_only: bool, include_timestamp: bool, error_msg: str, *subs):
    """Get a random post from a subreddit"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.reddit.com/r/{'+'.join(subs)}/hot.json?limit={limit}",
                headers=config.R_USER_AGENT) as w:

                resp = await w.json()

        is_nsfw = False
        for p in resp["data"]["children"].copy():
            if p["data"]["stickied"] or p["data"]["pinned"]:
                resp["data"]["children"].remove(p)
            elif p["data"]["over_18"] and not ctx.channel.is_nsfw():
                resp["data"]["children"].remove(p)
                is_nsfw = True
            elif img_only:
                if not p["data"]["url"].lower().endswith(("jpg", "jpeg", "png", "gif", "webp")):
                    if "imgur.com" in p["data"]["url"] and "/a/" not in p["data"]["url"]:
                        copy = p
                        copy["data"]["url"] += ".png"
                        resp["data"]["children"] = [
                            copy if x == p else x for x in resp["data"]["children"]]
                    else:
                        resp["data"]["children"].remove(p)

        data = random.choice(resp["data"]["children"])["data"]

        #* To format some special characters (like &, <, >, etc.) correctly
        data["title"] = BeautifulSoup(data["title"], "lxml").get_text()
        data["selftext"] = BeautifulSoup(data["selftext"], "lxml").get_text()

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
                           f"/{data['author']}/)\n\n{data['selftext']}")
            if len(data["selftext"]) > 2048 - len(description):
                data["selftext"] = ("*Sorry, but this content is too long for me to send in "
                                    "a single message. Click on the title above to go "
                                    "straight to the post*")
            if include_timestamp:
                embed = discord.Embed(
                    title=data["title"], description=f"By [u/{data['author']}](http://www.reddit."
                    f"com/user/{data['author']}/)\n\n{data['selftext']}",
                    timestamp=datetime.datetime.utcfromtimestamp(data["created_utc"]),
                    url="https://www.reddit.com" + data["permalink"], color=find_color(ctx))
            else:
                embed = discord.Embed(
                    title=data["title"], description=f"By [u/{data['author']}](http://www.reddit."
                    f"com/user/{data['author']}/)\n\n{data['selftext']}",
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
    """Find the bot's rendered color. Or if it's a DM, return Discord's "blurple" color"""

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


async def send_dank_memer_img(loop, ctx, resp, is_gif: bool=False):
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
        filepath = await loop.run_in_executor(None, functools.partial(save_image, resp))
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
