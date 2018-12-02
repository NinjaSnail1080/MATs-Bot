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

try:
    from mat_experimental import find_color, delete_message
except ImportError:
    from mat import find_color, delete_message

from discord.ext import commands
import discord
import qrcode
import pyshorteners
import validators
import aiohttp
import typing

import random
import string
import os

import config


def parse_definitions(resp):
    """Parses definitions for the "define" command"""

    sort_defs = {}
    for d in resp["definitions"]:
        if d["partOfSpeech"] not in sort_defs:
            sort_defs[d["partOfSpeech"]] = []
        sort_defs[d["partOfSpeech"]].append(d["definition"])

    return sort_defs


class Utility:
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(aliases=["shorten"], brief="You need to include a link to shorten. Format "
                      "like this: `<prefix> bitly <URL to shorten>`\n\nAlternatively, you can "
                      "also put an existing bit.ly link and I'll expand it back into the "
                      "original URL")
    async def bitly(self, ctx, *, url):
        """Shortens a link with Bitly.
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

    @commands.command(brief="You need to include a word for me to define")
    async def define(self, ctx, *, word):
        """Get the definition for a word"""

        await ctx.channel.trigger_typing()
        async with self.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}/definitions",
                                    headers=config.WORDS_API) as w:
            resp = await w.json()
            try:
                data = parse_definitions(resp)
            except KeyError:
                if resp["message"] == "word not found":
                    await ctx.send("Word not found. Try again", delete_after=5.0)
                    return await delete_message(ctx, 5)
                else:
                    return await ctx.send(
                        f"An unknown error has occured:```{resp['message']}```"
                        "If this problem persists, get in touch with my owner, NinjaSnail1080. "
                        "You can reach him at my support server: https://discord.gg/P4Fp3jA")

        embed = discord.Embed(
            title=f"Definitions of {word.title()}",
            description="Powered by [WordsAPI](https://www.wordsapi.com/)\n\u200b",
            color=find_color(ctx))
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        for part, meanings in data.items():
            embed.add_field(
                name=part, value="*" + "*,\n\n*".join(meanings[:4]) + "*\n\u200b", inline=False)

        await ctx.send(embed=embed)

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

    @commands.command(aliases=["lifeprotip"])
    async def lpt(self, ctx):
        """Posts an LPT, or Life Pro Tip (i.e., a life hack that's actually useful)"""

        try:
            with ctx.channel.typing():
                async with self.session.get(
                    "https://www.reddit.com/r/LifeProTips/hot.json?sort=hot",
                    headers=config.R_USER_AGENT) as w:

                    resp = await w.json()
                    data = random.choice(resp["data"]["children"])["data"]

                    if data["stickied"]:
                        raise Exception

                    if len(data["selftext"]) > 2048:
                        data["selftext"] = ("**Sorry, but this content is too long for me to "
                                            "send here. To see it, just click the title above to "
                                            "go straight to the post**")

                    embed = discord.Embed(
                        title=data["title"], url=data["url"], description=data["selftext"],
                        color=find_color(ctx))
                    embed.set_footer(text=f"👍 - {data['score']}")

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong and I wasn't able to get an LPT. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

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
                url=user.default_avatar_url)
            embed.set_image(url=user.default_avatar_url)
        else:
            embed = discord.Embed(
                title=user.display_name + "'s Profile Pic", color=find_color(ctx),
                url=user.avatar_url)
            embed.set_image(url=user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases=["qrcode"])
    async def qr(self, ctx, *, content=None):
        """Encode text into a QR code.
        Format like this: `<prefix> qr <text to encode>`
        """
        if content is None:
            await ctx.send("You need to include some text to encode. Format like this: "
                           "`<prefix> qr <text to encode>`", delete_after=7.0)
            return await delete_message(ctx, 7)
        else:
            try:
                await ctx.channel.trigger_typing()
                qrcode.make(content).save("qr.png")
                await ctx.send(
                    content=f"```{content}``` as a QR code:", file=discord.File("qr.png"))

            except discord.HTTPException:
                await ctx.send("The text you sent me was too long to encode. I ended up reaching "
                               "Discord's character limit. Try again with a smaller amount of "
                               "text.", delete_after=10.0)
                await delete_message(ctx, 10)

            os.remove("qr.png")

    @commands.command(brief="Invalid formatting. You're supposed to format the command like this:"
                      " `<prefix> random <length (defaults to 64)> <level (defaults to 3)>`\n"
                      "Note: There are 5 levels you can choose from. Do `<prefix> random levels` "
                      "for more info")
    async def random(self, ctx, length="64", level: int=3):
        """Generates a string of random characters.
        Format like this: `<prefix> random <length (defaults to 64)> <level (defaults to 3)>`
        There are 5 levels you can choose from. Do `<prefix> random levels` for more info
        """
        if length == "levels":
            await ctx.send("__Random Command Levels__:\n\n**Level 1**: Lowercase letters\n**Level"
                           " 2**: Lowercase and uppercase letters\n**Level 3**: Letters and "
                           "numbers\n**Level 4**: Letters, numbers, and symbols\n**Level 5**: "
                           "All of the above plus whitespace characters (spaces, tabs, newlines, "
                           "etc.)")
            return
        try:
            await ctx.channel.trigger_typing()
            length = int(length)
            if length > 1500:
                length = 1500

            if level == 1:
                await ctx.send(
                    "```" + "".join(
                        random.choice(string.ascii_lowercase) for _ in range(length + 1)) + "```")
            elif level == 2:
                await ctx.send(
                    "```" + "".join(
                        random.choice(string.ascii_letters) for _ in range(length + 1)) + "```")
            elif level == 3:
                await ctx.send(
                    "```" + "".join(random.choice(
                        string.ascii_letters + string.digits) for _ in range(length + 1)) + "```")
            elif level == 4:
                await ctx.send(
                    "```" + "".join(random.choice(
                        string.ascii_letters + string.digits + string.punctuation) for _ in range(
                            length + 1)) + "```")
            elif level == 5:
                    await ctx.send("```" + "".join(
                        random.choice(string.printable) for _ in range(length + 1)) + "```")
            else:
                raise commands.BadArgument
                return
        except ValueError:
            raise commands.BadArgument
            return
        except discord.HTTPException:
            #* In the unlikely event that the whitespaces in Level 5 cause the message length to
            #* be more than 2000 characters:
            await ctx.send("Huh, something went wrong here. Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(brief="Invalid formatting. You're supposed to include a color's RGB "
                      "values. Format the command like this:\n`<prefix> rgbtohex <r>, <g>, <b>`"
                      "\nNote that all 3 numbers must be greater than 0 and less than 256")
    async def rgbtohex(self, ctx, r: int, g: int, b: int):
        """Convert a color's RGB values to its hex value"""

        try:
            new_color = discord.Color.from_rgb(r, g, b)
            embed = discord.Embed(title="MAT's Color Converter", color=new_color)
            embed.add_field(name="RGB", value=f"({r}, {g}, {b})")
            embed.add_field(name="Hex", value=new_color)

            await ctx.send(embed=embed)
        except:
            raise commands.BadArgument

    @commands.command(aliases=["synonym", "synonyms", "antonym", "antonyms"], brief="You need to "
                      "include a word for me to get the synonyms and antonyms of")
    async def thesaurus(self, ctx, *, word):
        """Get the synonyms and antonyms of a word"""

        await ctx.channel.trigger_typing()
        error = []
        async with self.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}/synonyms",
                                    headers=config.WORDS_API) as w:
            s = await w.json()
            if "message" in s:
                error.append(s["message"])
        async with self.session.get(f"https://wordsapiv1.p.mashape.com/words/{word}/antonyms",
                                    headers=config.WORDS_API) as w:
            a = await w.json()
            if "message" in a:
                error.append(a["message"])

        try:
            embed = discord.Embed(
                title=f"Thesaurus for {word.title()}",
                description="Powered by [WordsAPI](https://www.wordsapi.com/)",
                color=find_color(ctx))

            if not s['synonyms']:
                s['synonyms'].append("(None)")
            if not a['antonyms']:
                a['antonyms'].append("(None)")

            embed.add_field(
                name="Synonyms", value=f"`{'`, `'.join(s['synonyms'])}`", inline=False)
            embed.add_field(
                name="Antonyms", value=f"`{'`, `'.join(a['antonyms'])}`", inline=False)
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
        except KeyError:
            if "word not found" in error:
                await ctx.send("Word not found. Try again", delete_after=5.0)
                return await delete_message(ctx, 5)
            else:
                return await ctx.send(
                    "An unknown error has occured:```" + "\n".join(error) + "```If this problem "
                    "persists, get in touch with my owner, NinjaSnail1080. You can reach him at "
                    "my support server: https://discord.gg/P4Fp3jA")

    @commands.command(brief="(finish this later)", hidden=True)
    async def translate(self, ctx, lang, *, phrase):
        """Translate words from English to another language
        Format like this: `<prefix> translate <language code> <words to translate>`
        Click [here](https://developers.google.com/admin-sdk/directory/v1/languages) to see all the language codes
        """
        return await ctx.send("This command isn't working right now")
        try:
            await ctx.channel.trigger_typing()
            translation = PyDictionary(phrase).translateTo(lang)

            await ctx.send(f"WIP```{translation[0]}```")
        except:
            pass


def setup(bot):
    bot.add_cog(Utility(bot))
