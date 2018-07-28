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

from mat import find_color
from discord.ext import commands
import discord
import asyncio
import qrcode
import pyshorteners
import validators

import random
import string
import os

import config


class Utility:
    """Utility commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["shorten"])
    async def bitly(self, ctx, *, url=None):
        """Shortens a link with Bitly.
        Format like this: `<prefix> bitly <URL to shorten>`
        You can also put an existing bit.ly link and I'll expand it into the original URL!
        """
        if url is None:
            await ctx.send("You need to include a link to shorten. Format like this: `<prefix> "
                           "bitly <URL to shorten>`\n\nAlternatively, you can also put an "
                           "existing bit.ly link and I'll expand it back into the original URL",
                           delete_after=10.0)
            await asyncio.sleep(10)
            await ctx.message.delete()
        else:
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
                        title=title, description="Powered by Bitly", color=find_color(ctx))
                    embed.add_field(name="Before", value=url, inline=False)
                    embed.add_field(name="After", value=link, inline=False)

                    await ctx.send(embed=embed)
                except:
                    await ctx.send("Oh, something went wrong trying to shorten this URL. "
                                   "Try again", delete_after=5.0)
                    await asyncio.sleep(5)
                    await ctx.message.delete()
            else:
                await ctx.send("Invalid URL. The link must look something like this: `http://www."
                               "example.com/something.html`.\nTry again", delete_after=6.0)
                await asyncio.sleep(6)
                await ctx.message.delete()

    @commands.command(hidden=True)
    @commands.is_owner()  #* Temporary
    async def invite(self, ctx):
        """Generates an invite link so you can add me to your own server!"""

        await ctx.send(
            "Here's my invite link so you can add me to your own server!\nhttps://discordapp.com/"
            "oauth2/authorize?client_id=459559711210078209&scope=bot&permissions=2146958591")

    @commands.command(aliases=["avatar"], brief="Invalid formatting. The command is supposed to "
                      "look like this: `<prefix> pfp (OPTIONAL)<@mention user or user's name/id>"
                      "`\n\nNote: If you used `-d`, then you must provide a user for it to work")
    async def pfp(self, ctx, user: discord.Member=None, default=None):
        """Get a user's profile pic. By default it retrieves your own but you can specify a different user.
        Format like this: `<prefix> pfp (OPTIONAL)<user>`
        Add "-d" to the end of the command to get the user's default pfp (Only works if user is provided)
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
                           "`<prefix> qr <text to encode>`", delete_after=5.0)
            await asyncio.sleep(5)
            await ctx.message.delete()
        else:
            qrcode.make(content).save("qr.png")
            await ctx.send(
                content="```%s``` as a QR code:" % content, file=discord.File("qr.png"))
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
            await asyncio.sleep(5)
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(Utility(bot))
