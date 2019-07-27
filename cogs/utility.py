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

from utils import find_color, delete_message, send_log, chunks, send_advanced_paginator, send_basic_paginator

from discord.ext import commands, tasks
from google_images_download import google_images_download
import discord
import qrcode
import pyshorteners
import validators
import pytimeparse
import googletrans
import dateutil.tz
import requests

import random
import string
import typing
import datetime
import asyncio
import functools
import os
import uuid
import re
import rapidjson as json

import config


class Utility(commands.Cog):
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot

        self.weather_icons = {
            "clear-day": "https://i.imgur.com/uVGCuS3.png",
            "clear-night": "https://i.imgur.com/Fvc8XVx.png",
            "rain": "https://i.imgur.com/NajZzEk.png",
            "snow": "https://i.imgur.com/8QihUDs.png",
            "sleet": "https://i.imgur.com/vXlvzAU.png",
            "wind": "https://i.imgur.com/AeQZLEg.png",
            "fog": "https://i.imgur.com/UcGbkuY.png",
            "cloudy": "https://i.imgur.com/ziJfuvj.png",
            "partly-cloudy-day": "https://i.imgur.com/5bJIn72.png",
            "partly-cloudy-night": "https://i.imgur.com/tbwORXJ.png"
        }

        self.currency_symbols = requests.get(
            f"http://data.fixer.io/api/symbols?access_key={config.FIXER}").json()["symbols"]

        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @tasks.loop(seconds=1)
    async def check_reminders(self):

        async def remove_reminder(reminder):
            self.bot.botdata["reminders"].remove(reminder)
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE botdata
                    SET reminders = $1::JSON[]
                ;""", self.bot.botdata["reminders"])

        for r in self.bot.botdata["reminders"].copy():
            if datetime.datetime.utcnow() >= datetime.datetime.fromtimestamp(
                r["started_at"] + r["duration"]):

                try:
                    author = self.bot.get_user(r["author"])
                    channel = self.bot.get_channel(r["channel"])
                    msg = await channel.fetch_message(r["msg"])
                except:
                    #* If something went wrong (for example, the bot can't see the user anymore),
                    #* just get rid of it and move on
                    await remove_reminder(r)
                    continue

                formatted_start = datetime.datetime.fromtimestamp(r["started_at"]).strftime(
                    "%B %-d, %Y at %X UTC")
                embed = discord.Embed(
                    title="Reminder", description=f"{author.mention}, on __{formatted_start}__, "
                    f"you used the `remindme` command in [this message]({msg.jump_url}) so that "
                    "I could remind you of something important later. The time has come, so here "
                    f"it is:```{r['remind_of']}```",
                    timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
                await author.send(embed=embed)
                await remove_reminder(r)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(10) #* To ensure that the database is fully set up before it starts

    @commands.command(aliases=["shorten"], brief="You need to include a link to shorten. Format "
                      "like this: `<prefix> bitly <URL to shorten>`\n\nAlternatively, you can "
                      "also put an existing bit.ly link and I'll expand it back into the "
                      "original URL")
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def bitly(self, ctx, *, url):
        """Shortens or expands a link with Bitly.
        Format like this: `<prefix> bitly <URL to shorten>`
        You can also put an existing bit.ly link and I'll expand it into the original URL
        """
        if validators.url(url):
            await ctx.channel.trigger_typing()
            try:
                s = pyshorteners.Shortener(
                    engine=pyshorteners.Shorteners.BITLY, bitly_token=config.BITLY)

                if "bit.ly" not in url:
                    title = "MAT's Link Shortener"
                    link = s.short(url)
                else:
                    title = "MAT's Link Expander"
                    link = s.expand(url)

                embed = discord.Embed(
                    title=title, description="Powered by [Bitly](https://bitly.com/)",
                    color=find_color(ctx))
                embed.add_field(name="Before", value=url, inline=False)
                embed.add_field(name="After", value=link, inline=False)

                await ctx.send(embed=embed)
            except:
                await ctx.send("Oops, something went wrong while trying to shorten/expand this "
                               "URL. Try again", delete_after=5.0)
                return await delete_message(ctx, 5)
        else:
            await ctx.send("Invalid URL. The link must look something like this: `http://www."
                           "example.com/something.html`.\nTry again", delete_after=6.0)
            return await delete_message(ctx, 6)

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                      "`<prefix> cconvert (OPTIONAL)<amount> <base currency> <currency to "
                      "convert to>`.\n\nIf you leave out the amount, I'll just give you the "
                      "exchange rate between the two currencies.\nFor the currencies themselves, "
                      "you must put the 3-letter code (e.g. USD, EUR, GBY, INR, JPY, etc.). For "
                      "a full list of supported currencies and their codes, see here: "
                      "https://currencylayer.com/currencies\n\n__Example Usage__: `<prefix> "
                      "cconvert 25 usd eur` (Will convert 25 U.S. Dollars to Euros)")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def cconvert(self, ctx, amount: typing.Optional[float]=1.0, src: str="", dest: str=""):
        """Convert between currencies.
        Format like this: `<prefix> cconvert (OPTIONAL)<amount> <base currency> <currency to convert to>`
        If you leave out the amount, I'll just give you the exchange rate between the two currencies.
        For the currencies, put the 3-letter code (e.g. USD, EUR, GBY, INR, JPY, etc.). For a full list of supported currencies and their codes, see [here](https://currencylayer.com/currencies)
        """
        src, dest = src.upper(), dest.upper()
        if src not in self.currency_symbols or dest not in self.currency_symbols:
            raise commands.BadArgument

        if amount <= 0:
            await ctx.send(
                "The amount must be greater than zero. Don't you know how money works?",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        with ctx.channel.typing():
            async with self.bot.session.get("http://data.fixer.io/api/latest"
                                            f"?access_key={config.FIXER}"
                                            f"&symbols={src},{dest}") as w:
                resp = await w.json()

        if not resp["success"]:
            await ctx.send(f"```Error {resp['error']['code']}\n{resp['error']['info']}```"
                           "An unknown error has occured. Try again, and if it persists, get in"
                           f"touch with my owner, {self.bot.owner.mention}. You can find him on "
                           "my support server: https://discord.gg/P4Fp3jA")
            return

        #* Default base is 1 Euro. I can't change it cause my API plan is the Free version and
        #* I'm too cheap to get the Basic plan that costs $10 per month.
        base_in_src = 1 / resp["rates"][src] #* Reverses "1 EUR to X src" to "1 src to X EUR"
        dest_in_src = base_in_src * resp["rates"][dest] #* Gets "X dest to 1 src" w/ proportions
        converted = dest_in_src * amount
        #! Improvise, Adapt, Overcome

        if amount.is_integer():
            amount = int(amount)
        if converted.is_integer():
            converted = int(converted)

        embed = discord.Embed(
            title="MAT's Currency Converter",
            description="Powered by [Fixer](https://fixer.io/)\n\n"
                        f"**Exchange Rate**: `1 {src} = {round(dest_in_src, 5)} {dest}`",
            timestamp=datetime.datetime.utcfromtimestamp(resp["timestamp"]),
            color=find_color(ctx))
        if amount != 1:
            embed.add_field(name="FROM:", value=f"```{amount} {src}```", inline=False)
            embed.add_field(name="TO:", value=f"```{converted} {dest}```", inline=False)
        embed.set_footer(text="These rates are accurate as of")

        await ctx.send(embed=embed)

    @commands.command(brief="You need to include a word for me to define")
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def define(self, ctx, *, word):
        """Get the definition of a word"""

        def parse_definitions(resp):
            """Parses definitions for the "define" command"""

            sort_defs = {}
            for d in resp["definitions"]:
                if d["partOfSpeech"] not in sort_defs:
                    sort_defs[d["partOfSpeech"]] = []
                sort_defs[d["partOfSpeech"]].append(d["definition"])
            sort_defs.pop(None, None)

            return sort_defs

        await ctx.channel.trigger_typing()
        try:
            async with self.bot.session.get(
                f"https://wordsapiv1.p.mashape.com/words/{word}/definitions",
                headers=config.WORDS_API) as w:

                resp = await w.json()
                data = parse_definitions(resp)

            async with self.bot.session.get(
                f"https://wordsapiv1.p.mashape.com/words/{word}/examples",
                headers=config.WORDS_API) as w:

                resp = await w.json()
                examples = resp["examples"]
                random.shuffle(examples)

            async with self.bot.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}",
                                            headers=config.WORDS_API) as w:
                resp = await w.json()
                syllables = resp["syllables"]["list"]
                syllables[0] = syllables[0].capitalize()
        except:
            await ctx.send("Word not found. Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

        embed = discord.Embed(
            title=f"Definitions of {word.title()}",
            description="Powered by [WordsAPI](https://www.wordsapi.com/)\n\n"
            f"__**{' • '.join(syllables)}**__\n\u200b",
            color=find_color(ctx))
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        for part, meanings in data.items():
            embed.add_field(
                name=part.title(), value="*" + "*,\n\n*".join(meanings[:4]) + "*\n\u200b",
                inline=False)

        if examples:
            embed.add_field(
                name="EXAMPLES",
                value="*" + "*,\n*".join([e.capitalize() for e in examples[:4]]) + "*\n\u200b",
                inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def experimental(self, ctx):
        """Sends an invite link for MAT's Experimental Bot, the development version of me, so you can invite it to your server and get access to new features and commands before they get released on me, the main bot!"""

        await ctx.send(
            "Here's an invite link for my development version, MAT's Experimental Bot!\nhttps://"
            "discordapp.com/oauth2/authorize?client_id=475897686680403980&scope=bot&permissions="
            "2146958847\nUsing my development version will allow you to have access to new "
            "features and commands before they get released on me, the main bot. However, please "
            "note that the experimental bot likely won't be online very often")

    @commands.command(aliases=["googleimages", "images"])
    @commands.cooldown(1, 18, commands.BucketType.user)
    async def gimages(self, ctx, *, keywords):
        """Get images from Google Images.
        Format like this: `<prefix> gimages <search terms>`
        SafeSearch will be turned on if this command is used in a non-NSFW channel
        """
        def download_images(arguments):
            downloader = google_images_download.googleimagesdownload()
            paths = downloader.download(arguments)
            return paths[0][arguments["keywords"]] #* List of image urls

        await ctx.channel.trigger_typing()
        args = {
            "keywords": keywords,
            "limit": 100,
            "safe_search": not ctx.channel.is_nsfw(),
            "no_download": True
        }
        urls = await self.bot.loop.run_in_executor(None, functools.partial(download_images, args))

        embeds = []
        for url in urls:
            embed = discord.Embed(
                title=f"Google Images Search Results For: {args['keywords']}",
                description=f"**Page {urls.index(url) + 1}/{len(urls)}**",
                timestamp=datetime.datetime.utcnow(), color=find_color(ctx))
            embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar_url)
            embed.set_footer(text="This message will be automatically deleted if left idle for "
                             "longer than 5 minutes")
            embed.set_image(url=url)
            embeds.append(embed)
        return await send_advanced_paginator(ctx, embeds, 5)

    @commands.command(brief="Invalid formatting. You need to include the hex value of the color. "
                      "Format like this:\n`<prefix> hextorgb <#hex value>`\nThe hex value will "
                      "look something like this: `#4286f4`")
    async def hextorgb(self, ctx, color: discord.Color):
        """Converts a color's hex value to its RGB values"""

        try:
            embed = discord.Embed(title="MAT's Color Converter", color=color)
            embed.add_field(name="Hex", value=color)
            embed.add_field(name="RGB", value=color.to_rgb())

            await ctx.send(embed=embed)
        except:
            raise commands.BadArgument

    @commands.command()
    async def invite(self, ctx):
        """Generates an invite link so you can add me to your own server!"""

        await ctx.send(
            "Here's my invite link so you can add me to your own server!\nhttps://discordapp.com/"
            "oauth2/authorize?client_id=459559711210078209&scope=bot&permissions=2146958591")

    @commands.command(aliases=["suicide"])
    async def lifeline(self, ctx):
        """Is someone on this server talking about ending their life? Use this command to bring up the suicide prevention hotlines and other resources for each country. It doesn't guarantee that they'll call it, but at least it's something you can do to try and help!"""

        embed = discord.Embed(
            title="There is help.", description="[Click here to see the suicide "
            "prevention hotlines and other resources for the country you live in]"
            "(https://13reasonswhy.info/)\nIf you call, they'll be able to help you, I promise.",
            color=find_color(ctx))

        await ctx.send(embed=embed)

    @commands.command(brief="You need to include some search terms. Format like this: `<prefix> "
                      "lmgtfy <search terms>`")
    async def lmgtfy(self, ctx, *, terms: str):
        """Generates a LMGTFY (Let Me Google That For You) link.
        Format like this: `<prefix> lmgtfy <search terms>`
        """
        link = "http://lmgtfy.com/?q=" + terms.lower().replace(" ", "+")
        embed = discord.Embed(
            title=terms.title() + "?", description=f"[Let Me Google That For You]({link})",
            color=find_color(ctx))
        embed.set_thumbnail(url="https://lmgtfy.com/assets/sticker-b222a421fb6cf257985abfab188be7"
                                "d6746866850efe2a800a3e57052e1a2411.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=["avatar"], brief="Invalid formatting. The command is supposed to "
                      "look like this: `<prefix> pfp (OPTIONAL)<@mention user or user's name/id>`"
                      "\n\nNote: If you used `-d`, then you must provide a user for it to work")
    async def pfp(self, ctx, user: typing.Optional[discord.Member]=None, default=None):
        """Get a user's profile pic. By default it retrieves your own but you can specify a different user.
        Format like this: `<prefix> pfp (OPTIONAL)<user>`
        Add `-d` to the end of the command to get the user's default pfp
        """
        if user is None:
            user = ctx.author

        if default == "-d":
            embed = discord.Embed(
                title=user.display_name + "'s Default Profile Pic", color=find_color(ctx),
                url=str(user.default_avatar_url))
            embed.set_image(url=user.default_avatar_url)
        else:
            embed = discord.Embed(
                title=user.display_name + "'s Profile Pic", color=find_color(ctx),
                url=str(user.avatar_url))
            embed.set_image(url=user.avatar_url)

        await ctx.send(embed=embed)

    @commands.group(aliases=["prefixes"], invoke_without_command=True)
    async def prefix(self, ctx):
        """Shows my prefixes for this server. You can also add or remove server-specific prefixes (this requires the Manage Server perm)"""
        if self.bot.guilddata[ctx.guild.id]["prefixes"]:
            guild_prefixes = self.bot.guilddata[ctx.guild.id]["prefixes"]
        else:
            guild_prefixes = ["None"]
        await ctx.send(f"__Default Prefixes__: `{'`, `'.join(self.bot.default_prefixes)}` "
                       f"**or** {self.bot.user.mention}\n__Server-Specific Prefix(es)__: "
                       f"`{'`, `'.join(guild_prefixes)}`\n\nDo `{ctx.prefix}prefix help` for "
                       "info on how to add or remove a server-specific prefix (a custom prefix "
                       "that only works on this server)")

    @prefix.command()
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx, pre: str):

        if len(self.bot.guilddata[ctx.guild.id]["prefixes"]) == 10:
            await ctx.send("This server already has 10 custom prefixes, which is the maximum. As "
                           "much as I'm sure you need yet another one, you can't add it unless "
                           "you remove one of the already existing prefixes", delete_after=12.0)
            return await delete_message(ctx, 12)

        prefixes = set(self.bot.guilddata[ctx.guild.id]["prefixes"])
        prefixes.add(pre)
        self.bot.guilddata[ctx.guild.id]["prefixes"] = list(prefixes)

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET prefixes = $1::TEXT[]
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["prefixes"])

        embed = discord.Embed(description=f"```{pre}```This new custom prefix will only work on "
                                          f"this server\nExample usage: `{pre}help`",
                              color=find_color(ctx))
        embed.set_author(name=f"{ctx.author.name} added a new server-specific command",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @prefix.command()
    async def help(self, ctx):
        await ctx.send("**Must have the `Manage Server` permission**\n\n__To **Add** a Server-"
                       f"Specific Prefix__: `{ctx.prefix}prefix add <new prefix>`\n__To "
                       f"**Remove** a Server-Specific Prefix__: `{ctx.prefix}prefix remove "
                       "<prefix to remove>`\n\nThe prefix must be in \"quotation marks\". If you "
                       "wish for there to be a space in between the prefix and the command, or "
                       "if the prefix already includes a space (e.g. `!mat help` as opposed to "
                       f"`!mathelp`), it must be included at the end like this: `{ctx.prefix}"
                       "prefix add/remove \"cmd \"`. Then `cmd help` would work if the prefix "
                       f"was added. If you just did `{ctx.prefix}prefix add \"cmd\"`, without "
                       "the space, then `cmdhelp` would work")

    @prefix.command(aliases=["delete"])
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, pre: str):

        try:
            self.bot.guilddata[ctx.guild.id]["prefixes"].remove(pre)
        except ValueError:
            await ctx.send(f"This server doesn't have `{pre}` as a custom prefix. Make sure it's "
                           "spelled correctly and you included a space if there is one (surround "
                           "the prefix in \"quotation marks\" if that's the case)",
                            delete_after=15.0)
            return await delete_message(ctx, 15)

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET prefixes = $1::TEXT[]
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["prefixes"])

        embed = discord.Embed(
            description=f"```{pre}```This custom prefix will no longer work on this server",
            color=find_color(ctx))
        embed.set_author(name=f"{ctx.author.name} REMOVED a server-specific command",
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await send_log(ctx, embed)

    @commands.command(aliases=["qrcode"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def qr(self, ctx, *, content=None):
        """Encode text into a QR code.
        Format like this: `<prefix> qr <text to encode>`
        """
        if content is None:
            await ctx.send("You need to include some text to encode. Format like this: "
                           f"`{ctx.prefix}qr <text to encode>`", delete_after=7.0)
            return await delete_message(ctx, 7)
        else:
            def encode():
                filename = f"qr-{uuid.uuid4()}.png"
                qrcode.make(content).save(filename)
                return filename

            await ctx.channel.trigger_typing()
            filename = await self.bot.loop.run_in_executor(None, encode)
            try:
                await ctx.send(
                    content=f"```{content}``` as a QR code:", file=discord.File(filename))
            except discord.HTTPException:
                await ctx.send(
                    content=f"The above content as a QR code:", file=discord.File(filename))
        if os.path.isfile(filename):
            os.remove(filename)

    @commands.command(brief="Invalid formatting. You're supposed to format the command like this:"
                      " `<prefix> random <length (defaults to 64)> <level (defaults to 3)>`\n"
                      "Note: There are 5 levels you can choose from. Do `<prefix> random levels` "
                      "for more info")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def random(self, ctx, levels: typing.Optional[str]=None, length: int=64, level: int=3):
        """Generates a string of random characters.
        Format like this: `<prefix> random <length (defaults to 64)> <level (defaults to 3)>`
        There are 5 levels you can choose from. Do `<prefix> random levels` for more info
        """
        if levels == "levels":
            await ctx.send("__Random Command Levels__:\n\n**Level 1**: Lowercase letters\n**Level"
                           " 2**: Lowercase and uppercase letters\n**Level 3**: Letters and "
                           "numbers\n**Level 4**: Letters, numbers, and symbols\n**Level 5**: "
                           "All of the above plus whitespace characters (spaces, tabs, newlines, "
                           "etc.)")
            return
        try:
            await ctx.channel.trigger_typing()
            if length > 1500:
                length = 1500

            if level == 1:
                await ctx.send(
                    "```" + "".join(
                        random.choice(string.ascii_lowercase) for _ in range(length)) + "```")
            elif level == 2:
                await ctx.send(
                    "```" + "".join(
                        random.choice(string.ascii_letters) for _ in range(length)) + "```")
            elif level == 3:
                await ctx.send(
                    "```" + "".join(random.choice(
                        string.ascii_letters + string.digits) for _ in range(length)) + "```")
            elif level == 4:
                await ctx.send(
                    "```" + "".join(random.choice(
                        string.ascii_letters + string.digits + string.punctuation) for _ in range(
                            length)) + "```")
            elif level == 5:
                    await ctx.send("```" + "".join(
                        random.choice(string.printable) for _ in range(length)) + "```")
            else:
                raise commands.BadArgument
        except ValueError:
            raise commands.BadArgument
        except discord.HTTPException:
            #* In the unlikely event that the whitespaces in Level 5 cause the message length to
            #* be more than 2000 characters:
            await ctx.send("Huh, something went wrong here. Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(brief="Invalid formatting. The command is supposed to be formatted like "
                      "this: `<prefix> <time till I remind you> <text to remind you of>`\nThe "
                      "time should look something like these: `3w`, `5d`, `3h30m`, `6d12h45m`, "
                      "etc. (NO SPACES)", aliases=["remind"])
    async def remindme(self, ctx, time: str, *, remind_of: str=None):
        """Need to be reminded of something in the future? Don't worry, just use this command!
        Format like this: `<prefix> remindme <time til I remind you> <text to remind you of>`
        The time should look something like this: `2w` OR `7h30m` OR `5d8h45m` (NO SPACES). The only characters supported are `w`, `d`, `h` or `hr`, `m`, and `s`
        """
        parsed_time = pytimeparse.parse(time)
        if parsed_time is None or remind_of is None:
            raise commands.BadArgument
        if parsed_time < 300 or parsed_time > 15778800:
            await ctx.send("The time until I remind you has to be longer than 5 minutes and "
                           "shorter than 6 months", delete_after=7.0)
            return await delete_message(ctx, 7)
        if len(remind_of) > 1800:
            await ctx.send(
                "The text I'll remind you of must be no more than 1800 characters long",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        formatted_dt = datetime.datetime.fromtimestamp(
            datetime.datetime.utcnow().timestamp() + parsed_time).strftime("%B %-d, %Y at %X UTC")
        await ctx.send(f"Ok {ctx.author.mention}, in **{time}**, on __{formatted_dt}__, I'll "
                       f"remind you of this:```{remind_of}```")

        new_reminder = {
            "author": ctx.author.id,
            "channel": ctx.channel.id,
            "msg": ctx.message.id,
            "started_at": datetime.datetime.utcnow().timestamp(),
            "duration": parsed_time,
            "remind_of": remind_of
        }
        self.bot.botdata["reminders"].append(new_reminder)
        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE botdata
                SET reminders = $1::JSON[]
            ;""", self.bot.botdata["reminders"])

    @commands.command(brief="Invalid formatting. You're supposed to include a color's RGB "
                      "values. Format the command like this:\n`<prefix> rgbtohex <r> <g> <b>`"
                      "\nNote that all 3 numbers must be greater than 0 and less than 256")
    async def rgbtohex(self, ctx, r: int, g: int, b: int):
        """Convert a color's RGB values to its hex value
        Format like this: `<prefix> rgbtohex <r> <g> <b>`
        """
        try:
            color = discord.Color.from_rgb(r, g, b)
            embed = discord.Embed(title="MAT's Color Converter", color=color)
            embed.add_field(name="RGB", value=f"({r}, {g}, {b})")
            embed.add_field(name="Hex", value=color)

            await ctx.send(embed=embed)
        except:
            raise commands.BadArgument

    @commands.command(brief="You need to include a word so I can get ones that rhyme with it")
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def rhymes(self, ctx, *, word):
        """Get words that rhyme with another word"""

        await ctx.channel.trigger_typing()
        async with self.bot.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}/rhymes",
                                        headers=config.WORDS_API) as w:
            try:
                resp = await w.json()
            except:
                if resp["message"] == "word not found":
                    await ctx.send("Word not found. Try again", delete_after=5.0)
                    return await delete_message(ctx, 5)
                else:
                    return await ctx.send(
                        f"An unknown error has occured:```{resp['message']}```If this "
                        f"problem persists, get in touch with my owner, {self.bot.owner}. "
                        "You can reach him at my support server: https://discord.gg/P4Fp3jA")

        rhyming_words = resp["rhymes"]
        if len(rhyming_words) > 1:
            rhyming_words.pop("all", None)

        for words in rhyming_words.values():
            random.shuffle(words)
            for rhyme in words:
                if rhyme == word.lower():
                    words.remove(rhyme)
            #* Remove words from the list until they will all fit in the embed
            while sum(len(i + "`, `") for i in words) > 1022:
                words.pop(-1)

        if not rhyming_words:
            await ctx.send(
                f"I couldn't find any words that rhyme with `{word}`",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        embed = discord.Embed(
            title=f"Words that rhyme with {word.title()}",
            description="Powered by [WordsAPI](https://www.wordsapi.com/)",
            color=find_color(ctx))
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        for title, words in rhyming_words.items():
            embed.add_field(
                name=title.title(), value=f"`{'`, `'.join(sorted(words))}`", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        """Having problems running me on your server and need some customer support? Just use this command and I'll send you a link to my support server"""

        await ctx.send("Here's a link to my support server if you're having any problems running "
                       "me! My owner and the other members will be glad to help!"
                       "\nhttps://discord.gg/P4Fp3jA")

    async def update_db_tags(self, ctx):
        """Update the tags in the database"""

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET tags = $1::JSON
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["tags"])

    @commands.group(invoke_without_command=True, aliases=["tags"])
    @commands.guild_only()
    async def tag(self, ctx, *, name=None):
        """Tag text for later retrieval.
        To get a tag, do `<prefix> tag <tag name>`. To see the other actions you can do, just type `<prefix> tag`.
        """
        if name is None:
            embed = discord.Embed(
                title="MAT's Tag Command | Help", description=f"An easy way to tag text for "
                f"later retrieval!\nTo get a tag, simply do `{ctx.prefix}tag <tag name>`. This "
                "will search the database for the tag requested (Note: Tag names are case-"
                "insensitive)\n\nThere are other actions you can do, which are documented below:",
                color=find_color(ctx))

            embed.add_field(name=f"{ctx.prefix}tag all",
                            value="Lists all the tags for this server", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag create <name> <content>", value="Creates a "
                            "new tag owned by you with the given name and content. If the tag "
                            "name is more than one word, it must be surrounded in \"quotation "
                            "marks\"", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag edit <name> <new content>", value="Edits a "
                            "tag owned by you and gives it the new content. To edit other "
                            "people's tags, you must have the **Manage Messages** perm. If the "
                            "tag name is more than one word, it must be surrounded in "
                            "\"quotation marks\"", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag info <name>",
                            value="Retrives info about a tag", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag list (OPTIONAL)<member>", value="Lists all "
                            "tags owned by the specified member. If you don't include a server "
                            "member, I'll list all tags owned by you", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag purge <member or \"all\">", value="Deletes "
                            "all tags owned by the specified member. You'll need the **Manage "
                            "Messages** perm to purge tags owned by other people. If you don't "
                            "mention a member and instead put the word `all`, I'll remove all "
                            "the tags on this server (This action also requires the **Manage "
                            "Messages** perm)", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag remove <name>", value="Removes the tag with "
                            "the given name. You need the **Manage Messages** perm to delete "
                            "tags owned by other people", inline=False)
            embed.add_field(name=f"{ctx.prefix}tag transfer <name> <new member>",
                            value="Transfer ownership of a tag to a new member. You need the "
                            "**Manage Messages** perm to transfer ownership of tags currently "
                            "owned by other people. If the tag name is more than one word, it "
                            "must be surrounded in \"quotation marks\"", inline=False)
            return await ctx.send(embed=embed)
        else:
            name = name.lower()
            tag_info = self.bot.guilddata[ctx.guild.id]["tags"].get(name, None)
            if tag_info is not None:
                await ctx.send(tag_info["content"])
                self.bot.guilddata[ctx.guild.id]["tags"][name]["uses"] += 1
                return await self.update_db_tags(ctx)
            else:
                await ctx.send(
                    "This tag doesn't exist. You can create it with the `tag create` command",
                    delete_after=5.0)
                return await delete_message(ctx, 5)

    @tag.command()
    async def all(self, ctx):
        if not self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send(f"This server has no tags. Do `{ctx.prefix}tag` to see how to "
                           "make one", delete_after=7.0)
            return await delete_message(ctx, 7)

        tags = self.bot.guilddata[ctx.guild.id]["tags"]
        sorted_tags = sorted(tags.keys(), key=lambda t: tags[t]["uses"], reverse=True)
        all_tags = list(chunks(sorted_tags, 24))

        embeds = []
        for i in all_tags:
            if len(all_tags) > 1:
                description = (f"**Page {all_tags.index(i) + 1}/{len(all_tags)}** "
                               f"({len(tags)} Tags)")
                footer = ("This message will be automatically deleted if left idle for longer "
                          "than 5 minutes")
            else:
                description = ""
                footer = ""

            embed = discord.Embed(description=description,
                                  timestamp=datetime.datetime.utcnow(),
                                  color=find_color(ctx))
            embed.set_author(name=f"{ctx.guild.name}: All Tags", icon_url=ctx.guild.icon_url)
            embed.set_footer(text=footer)
            for t in i:
                embed.add_field(
                    name=f"{sorted_tags.index(t) + 1}. {t}",
                    value=f"**Owner**: {self.bot.get_user(tags[t]['owner']).mention}\n"
                    f"**Uses**: {tags[t]['uses']}")
            embeds.append(embed)

        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        elif len(embeds) <= 4:
            return await send_basic_paginator(ctx, embeds, 5)
        else:
            return await send_advanced_paginator(ctx, embeds, 5)

    @tag.command(aliases=["make", "add"], brief="You didn't format the command correctly. It's "
                 "supposed to look like this: `<prefix> tag create <name> <content>`\n\nThis "
                 "will create a new tag owned by you with the given name and content")
    async def create(self, ctx, name, *, content: commands.clean_content()):
        name = name.lower()
        if name in self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send("There is already a tag with that name", delete_after=6.0)
            return await delete_message(ctx, 6)

        if ctx.command.parent.get_command(name) is not None:
            await ctx.send(f"You aren't allowed to make a tag with the name `{name}`, since "
                           "it shares the same name as one of the subcommands", delete_after=7.0)
            return await delete_message(ctx, 7)

        new_tag = {
            name: {
                "owner": ctx.author.id,
                "content": content,
                "created_at": datetime.datetime.utcnow().timestamp(),
                "uses": 0
            }
        }
        self.bot.guilddata[ctx.guild.id]["tags"].update(new_tag)
        await self.update_db_tags(ctx)
        await ctx.send(
            f"Ok, the `{name}` tag has been created with {ctx.author.mention} as the owner")

    @tag.command(aliases=["update"], brief="You didn't format the command correctly. It's "
                 "supposed to look like this: `<prefix> tag edit <name> <new content>`\n\nThis "
                 "will edit the tag with the specified name and give it new content")
    async def edit(self, ctx, name, *, new_content: commands.clean_content()):
        name = name.lower()
        if name not in self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send(
                "This tag doesn't exist. You can create it with the `tag create` command",
                delete_after=7.0)
            return await delete_message(ctx, 7)

        if (self.bot.guilddata[ctx.guild.id]["tags"][name]["owner"] != ctx.author.id and
                not ctx.author.guild_permissions.manage_messages):
            await ctx.send("You are not the owner of this tag, and you need the **Manage "
                           "Messages** perm to edit other people's tags, so you do not have "
                           "authorization to edit this tag", delete_after=10.0)
            return await delete_message(ctx, 10)

        self.bot.guilddata[ctx.guild.id]["tags"][name]["content"] = new_content
        await self.update_db_tags(ctx)

        owner_id = self.bot.guilddata[ctx.guild.id]["tags"][name]["owner"]
        if ctx.author.id == owner_id:
            await ctx.send(f"Ok, {ctx.author.mention}'s `{name}` tag has been edited/updated")
        else:
            await ctx.send(f"Ok, {self.bot.get_user(owner_id).mention}'s `{name}` tag has been "
                           f"edited/updated by {ctx.author.mention}")

    @tag.command(aliases=["about"], brief="You didn't format the command correctly. It's "
                 "supposed to look like this: `<prefix> tag info <name of tag>`")
    async def info(self, ctx, *, name):
        name = name.lower()
        if name not in self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send(
                "This tag doesn't exist. You can create it with the `tag create` command",
                delete_after=7.0)
            return await delete_message(ctx, 7)

        tags = self.bot.guilddata[ctx.guild.id]["tags"]
        the_tag = tags[name]
        embed = discord.Embed(
            title=f"Info on the \"{name}\" tag",
            timestamp=datetime.datetime.fromtimestamp(the_tag["created_at"]),
            color=find_color(ctx))
        embed.set_author(name=self.bot.get_user(the_tag["owner"]),
                         icon_url=self.bot.get_user(the_tag["owner"]).avatar_url)
        embed.set_footer(text="Tag created")

        embed.add_field(name="Owner", value=self.bot.get_user(the_tag["owner"]).mention)
        embed.add_field(name="Uses", value=the_tag["uses"])
        embed.add_field(
            name="Rank",
            value=sorted(tags, key=lambda t: tags[t]["uses"], reverse=True).index(name) + 1)

        await ctx.send(embed=embed)

    @tag.command(name="list", brief="You didn't format the command correctly. It's supposed "
                 "to look like this: `<prefix> tag list (OPTIONAL)<member>`\n\nThis will list "
                 "all the tags owned by the specified member. If you don't include a server "
                 "member, I'll list all tags owned by you")
    async def list_member(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        if not self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send(f"**{member.display_name}** has no tags. In fact, no one on this "
                           f"server has any tags. Do `{ctx.prefix}tag` to see how to make one",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        tags = self.bot.guilddata[ctx.guild.id]["tags"]
        all_tags = sorted(tags, key=lambda t: tags[t]['uses'], reverse=True)
        member_tags = sorted([k for k, v in tags.items() if v["owner"] == member.id],
                             key=lambda t: tags[t]["uses"], reverse=True)
        chunked_tags = list(chunks(member_tags, 24))

        if not member_tags:
            await ctx.send(f"**{member.display_name}** doesn't own any tags", delete_after=5.0)
            return delete_message(ctx, 5)

        embeds = []
        for i in chunked_tags:
            if len(chunked_tags) > 1:
                description = (f"**Page {chunked_tags.index(i) + 1}/{len(chunked_tags)}** "
                               f"({len(tags)} Tags)")
                footer = ("This message will be automatically deleted if left idle for longer "
                          "than 5 minutes")
            else:
                description = ""
                footer = ""

            embed = discord.Embed(description=description,
                                  timestamp=datetime.datetime.utcnow(),
                                  color=find_color(ctx))
            embed.set_author(name=f"{member.display_name}: All Tags", icon_url=member.avatar_url)
            embed.set_footer(text=footer)
            for t in i:
                embed.add_field(
                    name=f"{member_tags.index(t) + 1}. {t}",
                    value=f"**Uses**: {tags[t]['uses']}\n**Rank**: {all_tags.index(name) + 1}")
            embeds.append(embed)

        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        elif len(embeds) <= 4:
            return await send_basic_paginator(ctx, embeds, 5)
        else:
            return await send_advanced_paginator(ctx, embeds, 5)

    @tag.command(brief="You didn't format the command correctly. It's supposed to look like this:"
                 " `<prefix> tag purge <member or \"all\">`\n\nIf you put a member, I'll remove "
                 "all the tags owned by that person. If you put the word `all` instead, I'll "
                 "remove all the tags on this server")
    async def purge(self, ctx, member: typing.Union[discord.Member, str]):
        if isinstance(member, discord.Member):
            if ctx.author != member and not ctx.author.guild_permissions.manage_messages:
                await ctx.send(f"You are not **{member.display_name}**, and you need the "
                               "**Manage Messages** perm to purge other people's tags, so you do "
                               "not have authorization to perform this command",
                               delete_after=10.0)
                return await delete_message(ctx, 10)

            removed = []
            for name, data, in self.bot.guilddata[ctx.guild.id]["tags"].copy().items():
                if data["owner"] == member.id:
                    self.bot.guilddata[ctx.guild.id]["tags"].pop(name)
                    removed.append(name)

            try:
                temp = await ctx.send("Please wait...")
                with ctx.channel.typing():
                    async with self.bot.session.post(
                        "https://hastebin.com/documents",
                        data="\n".join(removed).encode("utf-8")) as w:

                        #* For whatever reason, "await w.json()" doesn't work, so I'm using this:
                        post = json.loads(await w.read())
                        # post = await w.json()
                        link = f"https://hastebin.com/raw/{post['key']}"
            except:
                #* On the rare occasion that it fails to post to hastebin
                link = None

            await temp.delete()
            if ctx.author == member:
                msg = f"Ok, all **{len(removed)}** of {member.mention}'s tags have been removed."
            else:
                msg = (f"Ok, all **{len(removed)}** of {member.mention}'s tags have been removed "
                       f"by {ctx.author.mention}.")
            if link is not None:
                msg += f"\n\nSee {link} for a list of all the tags that were removed"

        elif member == "all":
            if not ctx.author.guild_permissions.manage_messages:
                await ctx.send("You need the **Manage Messages** perm to purge everyone's tags, "
                               "so you do not have authorization to perform this command",
                               delete_after=10.0)
                return await delete_message(ctx, 10)

            confirm = await ctx.send("React with \U00002705 to confirm that you want to purge "
                                     f"all **{len(self.bot.guilddata[ctx.guild.id]['tags'])}** "
                                     "tags on this server. React with \U0000274c to cancel")
            await confirm.add_reaction("\U00002705")
            await confirm.add_reaction("\U0000274c")

            def check_reaction(message, author):
                def check(reaction, user):
                    if reaction.message.id != message.id or user != author:
                        return False
                    elif reaction.emoji == "\U00002705":
                        return True
                    elif reaction.emoji == "\U0000274c":
                        return True
                    return False
                return check

            try:
                react, user = await self.bot.wait_for(
                    "reaction_add", timeout=15, check=check_reaction(confirm, ctx.author))
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

            msg = (f"All **{len(self.bot.guilddata[ctx.guild.id]['tags'])}** tags on this server "
                   f"were just removed by {ctx.author.mention}")
            self.bot.guilddata[ctx.guild.id]["tags"].clear()
        else:
            raise commands.BadArgument

        await self.update_db_tags(ctx)
        return await ctx.send(msg)

    @tag.command(aliases=["delete"], brief="You didn't format the command correctly. It's "
                 "supposed to look like this: `<prefix> tag remove <name of tag>`")
    async def remove(self, ctx, *, name):
        name = name.lower()
        if name not in self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send(
                "This tag doesn't exist. You can create it with the `tag create` command",
                delete_after=7.0)
            return await delete_message(ctx, 7)

        if (self.bot.guilddata[ctx.guild.id]["tags"][name]["owner"] != ctx.author.id and
                not ctx.author.guild_permissions.manage_messages):
            await ctx.send("You are not the owner of this tag, and you need the **Manage "
                           "Messages** perm to delete other people's tags, so you do not have "
                           "authorization to remove this tag", delete_after=10.0)
            return await delete_message(ctx, 10)

        del_tag = self.bot.guilddata[ctx.guild.id]["tags"].pop(name)
        await self.update_db_tags(ctx)

        owner_id = del_tag["owner"]
        if ctx.author.id == owner_id:
            await ctx.send(f"Ok, {ctx.author.mention}'s `{name}` tag has been removed")
        else:
            await ctx.send(f"Ok, {self.bot.get_user(owner_id).mention}'s `{name}` tag has been "
                           f"removed by {ctx.author.mention}")

    @tag.command(brief="You didn't format the command correctly. It's supposed to look like this:"
                 "`<prefix> tag remove <name of tag> <member>`\nThis will transfer ownership of "
                 "a tag to a new member")
    async def transfer(self, ctx, name, new_owner: discord.Member):
        name = name.lower()
        if name not in self.bot.guilddata[ctx.guild.id]["tags"]:
            await ctx.send(
                "This tag doesn't exist. You can create it with the `tag create` command",
                delete_after=7.0)
            return await delete_message(ctx, 7)

        if (self.bot.guilddata[ctx.guild.id]["tags"][name]["owner"] != ctx.author.id and
                not ctx.author.guild_permissions.manage_messages):
            await ctx.send("You are not the owner of this tag, and you need the **Manage "
                           "Messages** perm to transfer ownership of other people's tags, so you "
                           "do not have authorization to perform this command", delete_after=10.0)
            return await delete_message(ctx, 10)

        if new_owner.bot:
            await ctx.send("Ownership of a tag cannot be transferred to a bot", delete_after=6.0)
            return await delete_message(ctx, 6)

        old_owner = self.bot.get_user(self.bot.guilddata[ctx.guild.id]["tags"][name]["owner"])
        if new_owner == old_owner:
            await ctx.send(f"{new_owner.display_name} already owns this tag", delete_after=5.0)
            return await delete_message(ctx, 5)

        self.bot.guilddata[ctx.guild.id]["tags"][name]["owner"] = new_owner.id
        await self.update_db_tags(ctx)

        msg = (f"Ownership of the `{name}` tag has been transferred from {old_owner.mention} to "
               f"{new_owner.mention}\n\n{new_owner.mention} now has the ability to edit this tag "
               "in any way they so desire")
        if ctx.author != old_owner:
            msg += f"\n\nThis command was performed by {ctx.author.mention}"

        await ctx.send(msg)

    @commands.command(aliases=["timeconvert"], brief="You didn't format the command correctly. "
                      "It's supposed to look like this: `<prefix> tconvert <time> <location> "
                      "<location to convert to>`\n\nDO NOT PUT TIMEZONE ABBREVIATIONS LIKE `EST` "
                      "OR `PST` (The only timzone abbrev. this command supports is `UTC`, or "
                      "Universal Standard Time. Any others won't work). Instead, put names of "
                      "locations, like `washington,dc`, `london,uk`, or `miami,fl` (NO SPACES IN "
                      "THE LOCATION NAME. Use commas instead).\nThe time can be in either "
                      "24-hour form (21:15) or 12-hour form (9:15 PM).\n\n__Example Usage__: "
                      "`<prefix> tconvert 3:30 PM new,york,city,ny sydney,australia` will "
                      "convert 3:30 PM New York time to the time in Sydney, Australia")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def tconvert(self, ctx, time: str, args: commands.Greedy[commands.clean_content]):
        """Convert one timezone to another
        Format like this: `<prefix> tconvert <time> <location> <location to convert to>`
        DO NOT PUT TIMEZONE ABBREVIATIONS LIKE `EST` OR `PST` (The only timzone abbrev. this command supports is `UTC`, or Universal Standard Time. Any others won't work). Instead, put names of locations, like `washington,dc`, `london,uk`, or `miami,fl` (NO SPACES. Use commas instead).
        The time can be in either 24-hour form (21:15) or 12-hour form (9:15 PM).
        __Example Usage__: `tconvert 3:30 PM new,york,city,ny sydney,australia` will convert 3:30 PM New York time to the time in Sydney, Australia
        """
        if len(args) == 3:
            meridiem = args[0].replace(".", "").upper()
            here = args[1]
            there = args[2]
        elif len(args) == 2:
            meridiem = None
            here = args[0]
            there = args[1]
        else:
            raise commands.BadArgument

        with ctx.channel.typing():
            if here.lower() != "utc":
                async with self.bot.session.get("http://www.mapquestapi.com/geocoding/v1/address?"
                                                f"key={config.MAPQUEST}&location={here}&thumbMaps"
                                                "=false&maxResults=1") as w:
                    resp = await w.json()
                    here_latlng = resp["results"][0]["locations"][0]["displayLatLng"]

                async with self.bot.session.get("https://api.darksky.net/forecast/"
                                                f"{config.DARK_SKY}/{here_latlng['lat']},"
                                                f"{here_latlng['lng']}?exclude=currently,minutely"
                                                ",hourly,daily,alerts,flags") as w:
                    resp = await w.json()
                    here_tz = resp["timezone"]
                    here_text = resp["timezone"]
            else:
                here_tz = "UTC"
                here_text = "Universal Standard Time"

            if there.lower() != "utc":
                async with self.bot.session.get("http://www.mapquestapi.com/geocoding/v1/address?"
                                                f"key={config.MAPQUEST}&location={there}&thumb"
                                                "Maps=false&maxResults=1") as w:
                    resp = await w.json()
                    there_latlng = resp["results"][0]["locations"][0]["displayLatLng"]

                async with self.bot.session.get("https://api.darksky.net/forecast/"
                                                f"{config.DARK_SKY}/{there_latlng['lat']},"
                                                f"{there_latlng['lng']}?exclude=currently,"
                                                "minutely,hourly,daily,alerts,flags") as w:
                    resp = await w.json()
                    there_tz = resp["timezone"]
                    there_text = resp["timezone"]
            else:
                there_tz = "UTC"
                there_text = "Universal Standard Time"

        try:
            if meridiem is None:
                current_time = datetime.datetime.strptime(
                    time, "%H:%M") + datetime.timedelta(days=10000)
            else:
                time += f" {meridiem}"
                current_time = datetime.datetime.strptime(
                    time, "%I:%M %p") + datetime.timedelta(days=10000)
                #* Without the "+ datetime.timedelta(days=10000)", the time zones were for some
                #* reason about an hour ahead. I have no idea why adding a bunch of days to the
                #* datetime fixes the issue.
        except:
            raise commands.BadArgument

        current_time = current_time.replace(tzinfo=dateutil.tz.gettz(here_tz))
        converted_time = current_time.astimezone(dateutil.tz.gettz(there_tz))

        embed = discord.Embed(
            title="MAT's Time Zone Converter",
            description="Powered by [MapQuest](https://www.mapquest.com/) and "
                        "[Dark Sky](https://darksky.net/poweredby/)",
            color=find_color(ctx))
        embed.add_field(
            name="FROM: " + here_text,
            value=f"```{current_time.strftime('%-I:%M %p %Z')} "
                  f"({current_time.strftime('%-H:%M')})```",
            inline=False)
        embed.add_field(
            name="TO: " + there_text,
            value=f"```{converted_time.strftime('%-I:%M %p %Z')} "
                  f"({converted_time.strftime('%-H:%M')})```",
            inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["synonyms", "antonyms"], brief="You need to include a word for me "
                      "to get the synonyms and antonyms of")
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def thesaurus(self, ctx, *, word):
        """Get the synonyms and antonyms of a word"""

        await ctx.channel.trigger_typing()
        error = []
        async with self.bot.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}/synonyms",
                                        headers=config.WORDS_API) as w:
            s = await w.json()
            if "message" in s:
                error.append(s["message"])

        async with self.bot.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}/antonyms",
                                        headers=config.WORDS_API) as w:
            a = await w.json()
            if "message" in a:
                error.append(a["message"])

        try:
            embed = discord.Embed(
                title=f"Thesaurus for {word.title()}",
                description="Powered by [WordsAPI](https://www.wordsapi.com/)",
                color=find_color(ctx))

            if not s["synonyms"]:
                s["synonyms"].append("[None found]")
            if not a["antonyms"]:
                a["antonyms"].append("[None found]")

            embed.add_field(
                name="Synonyms", value=f"`{'`, `'.join(sorted(s['synonyms']))}`", inline=False)
            embed.add_field(
                name="Antonyms", value=f"`{'`, `'.join(sorted(a['antonyms']))}`", inline=False)
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
        except:
            if "word not found" in error:
                await ctx.send("Word not found. Try again", delete_after=5.0)
                return await delete_message(ctx, 5)
            else:
                return await ctx.send(
                    "An unknown error has occured:```" + "\n".join(error) + "```If this problem "
                    f"persists, get in touch with my owner, {self.bot.owner}. You can reach him "
                    "at my support server: https://discord.gg/P4Fp3jA")

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> translate <lang to translate into> <text to translate>`\n"
                      "\nThe text you put can be in any language. Google Translate will attempt "
                      "to automatically detect which laungage the text is in.\nFor the language "
                      "to translate into, put something like `english`, `spanish`, `korean`, "
                      "etc. Or if that doesn't work, try using a language code. You can find a "
                      "list of them here: https://ctrlq.org/code/19899-google-translate-languages"
                      "#languages")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def translate(self, ctx, lang: str, *, text: str):
        """Use Google Translate to translate text from one language to another
        Format like this: `<prefix> translate <lang to translate into> <text to translate>`
        The text you put can be in any language. Google Translate will attempt to automatically detect which laungage the text is in.
        For the language to translate into, put something like `english`, `spanish`, `korean`, etc. Or if that doesn't work, put a language code. [See here](https://ctrlq.org/code/19899-google-translate-languages#languages) for a list of language codes that Google Translate supports
        """
        def translate_text():
            translator = googletrans.Translator()
            translation = translator.translate(text, dest=lang)
            return translation

        await ctx.channel.trigger_typing()
        try:
            translated = await self.bot.loop.run_in_executor(None, translate_text)
        except ValueError:
            await ctx.send(
                "Invalid language. Try again. If putting in the name of a language didn't work, "
                "try using the langauge code instead. You can find a list of them here: "
                "https://ctrlq.org/code/19899-google-translate-languages#languages",
                delete_after=15.0)
            return await delete_message(ctx, 15)

        embed = discord.Embed(
            title="MAT's Language Translator",
            description="Powered by [Google Translate](https://translate.google.com/)",
            color=find_color(ctx))
        embed.add_field(name="FROM: " + googletrans.LANGUAGES.get(translated.src).title(),
                        value=f"```{text}```", inline=False)
        embed.add_field(name="TO: " + googletrans.LANGUAGES.get(translated.dest).title(),
                        value=f"```{translated.text}```", inline=False)

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 18, commands.BucketType.user)
    async def weather(self, ctx, *, location):
        """Get weather info for a location.
        Format like this: `<prefix> weather <name of location>`
        I default to showing the data in SI units, like Celsius, kilometers, etc. To see it in U.S. Imperial units, add `-us` before the location, like this: `weather -us new york city, ny`
        To change your default units, do `<prefix> weather setmyunits <\"us\" OR \"si\">`. If you put `us`, I'll always show you U.S. Imperial units. If you put `si`, I'll always show you SI units (this is the default)
        """
        if location.lower().startswith("-us ") or self.bot.userdata[ctx.author.id]["us_units"]:
            units = "us"
            temp = "F"
            dis = "mi"
            dph = "mph"
        else:
            units = "ca"
            temp = "C"
            dis = "km"
            dph = "km/h"
        location = location.lower().replace("-us ", "").replace(", ", ",").replace(" ", ",")
        with ctx.channel.typing():
            async with self.bot.session.get("http://www.mapquestapi.com/geocoding/v1/address?key="
                                            f"{config.MAPQUEST}&location={location}&thumbMaps="
                                            "false&maxResults=1") as w:
                resp = await w.json()
                latlng = resp["results"][0]["locations"][0]["displayLatLng"]

            location_dict = resp["results"][0]["locations"][0]
            location_text = ""
            if location_dict["street"] != "":
                location_text += location_dict["street"] + ", "
            if location_dict["adminArea5"] != "":
                location_text += location_dict["adminArea5"] + ", "
            if location_dict["adminArea3"] != "":
                location_text += location_dict["adminArea3"] + ", "
            if location_dict["adminArea1"] != "":
                location_text += location_dict["adminArea1"] + " "
            if location_dict["postalCode"] != "":
                location_text += location_dict["postalCode"]

            async with self.bot.session.get(f"https://api.darksky.net/forecast/{config.DARK_SKY}/"
                                            f"{latlng['lat']},{latlng['lng']}?exclude="
                                            f"flags,alerts&units={units}") as w:
                resp = await w.json()

            currently = resp["currently"]
            if "minutely" in resp:
                minutely_summary = f"• {resp['minutely']['summary']}\n"
            else:
                minutely_summary = ""
            if "hourly" in resp:
                hourly_summary = f"• {resp['hourly']['summary']}\n\n"
            else:
                hourly_summary = ""
            daily = resp["daily"]
            now = datetime.datetime.fromtimestamp(
                currently["time"], tz=dateutil.tz.gettz(resp["timezone"]))

            frmtd_now = now.strftime("%A, %B %-d, %Y at %-I:%M %p %Z")
            description = ("Powered by [MapQuest](https://www.mapquest.com/) and [Dark Sky]"
                           f"(https://darksky.net/poweredby/)\n\n**__{frmtd_now}__**\n"
                           f"{currently['summary']}, {round(currently['temperature'])}°{temp}\n\n"
                           f"**Feels like**: {round(currently['apparentTemperature'])}°{temp}\n")

            if currently["windSpeed"] != 0:
                def degrees_to_compass(degrees: int):
                    index = int((degrees / 45) + 0.5)
                    compass_rose = ["North", "Northeast", "East", "Southeast", "South",
                                    "Southwest", "West", "Northwest"]
                    return compass_rose[index % 8]

                description += (f"**Wind**: {round(currently['windSpeed'])} {dph} "
                                f"{degrees_to_compass(currently['windBearing'])}\n")

            description += (f"**Visibility**: {round(currently['visibility'])} {dis}\n"
                            f"**Humidity**: {round(currently['humidity'] * 100)}%\n"
                            f"**Cloud Cover**: {round(currently['cloudCover'] * 100)}%\n"
                            f"**Dew Point**: {round(currently['dewPoint'])}°{temp}\n\n"
                            f"{minutely_summary}{hourly_summary}**__Rest of The Week__**:\n"
                            f"{daily['summary']}\n\n*React with \U000027a1 or \U00002b05 to go "
                            "to the next day or the previous one*")

            embeds = []
            for day in daily["data"]:
                day_datetime = datetime.datetime.fromtimestamp(day["time"], tz=now.tzinfo)
                if daily["data"][0] == day:
                    day_name = f"Info for Today"
                elif daily["data"][1] == day:
                    day_name = f"Info for Tomorrow, {day_datetime.strftime('%B %-d')}"
                else:
                    day_name = f"Info for {day_datetime.strftime('%A, %B %-d')}"

                try:
                    if day["precipType"] == "rain":
                        precip_emoji = ":cloud_rain:"
                    elif day["precipType"] == "snow":
                        precip_emoji = ":cloud_snow:"
                    elif day["precipType"] == "sleet":
                        precip_emoji == "<:sleet:567066979324657666>"
                except KeyError:
                    precip_emoji = ":cloud_rain:"

                high_time = datetime.datetime.fromtimestamp(
                    day["temperatureMaxTime"], tz=now.tzinfo).strftime("%-I%p")
                low_time = datetime.datetime.fromtimestamp(
                    day["temperatureMinTime"], tz=now.tzinfo).strftime("%-I%p")

                embed = discord.Embed(title=f"Weather Info for {location_text}",
                                      description=description,
                                      timestamp=datetime.datetime.utcnow(),
                                      color=find_color(ctx))
                embed.set_thumbnail(url=self.weather_icons[currently["icon"]])
                embed.add_field(
                    name=day_name,
                    value=f"**High**: {round(day['temperatureMax'])}° ({high_time.lower()})"
                    f"\n**Low**: {round(day['temperatureMin'])}° ({low_time.lower()})\n"
                    f"{day['summary']}\n{precip_emoji} {round(day['precipProbability'] * 100)}%")
                embed.set_footer(text="This message will be automatically deleted if it's left "
                                 "idle for longer than 5 minutes")
                embeds.append(embed)

        return await send_basic_paginator(ctx, embeds, 5, False)

    @weather.command(brief="Invalid formatting. The command is supposed to look like this: "
                     "`<prefix> weather setmyunits <\"us\" OR \"si\">`\nIf you put `us`, I'll "
                     "always use U.S. Imperial units with you, such as Fahrenheit, miles, etc.\n"
                     "If you put `si`, I'll always use SI, or the International System of Units, "
                     "with you, like Celsius, kilometers, etc.\nMy defualt is SI units")
    async def setmyunits(self, ctx, units):
        units = units.lower()
        if units == "us":
            if self.bot.userdata[ctx.author.id]["us_units"]:
                await ctx.send("You're already using U.S. Imperial units", delete_after=5.0)
                return await delete_message(ctx, 5)
            else:
                with ctx.channel.typing():
                    self.bot.userdata[ctx.author.id]["us_units"] = True
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE userdata
                            SET us_units = TRUE
                            WHERE id = {}
                        ;""".format(ctx.author.id))
                return await ctx.send("Ok, I will now show you data in U.S. Imperial units when "
                                      "you use the `weather` command")
        elif units == "si":
            if not self.bot.userdata[ctx.author.id]["us_units"]:
                await ctx.send("You're already using SI units", delete_after=5.0)
                return await delete_message(ctx, 5)
            else:
                with ctx.channel.typing():
                    self.bot.userdata[ctx.author.id]["us_units"] = False
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE userdata
                            SET us_units = FALSE
                            WHERE id = {}
                        ;""".format(ctx.author.id))
                return await ctx.send("Ok, I will now show you data in the Internation System of "
                                      "Units (SI units) when you use the `weather` command")
        else:
            raise commands.BadArgument


def setup(bot):
    bot.add_cog(Utility(bot))
