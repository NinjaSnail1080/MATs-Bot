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
from PIL import Image as IMG
from PIL import ImageEnhance, ImageFilter
import discord
import aiohttp
import validators
import pytesseract
import typing

import io
import os

import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

#* MAT's Bot uses the NekoBot API for most of these commands.
#* More info at https://docs.nekobot.xyz/


class Image:
    """Image Manipulation commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def get_image(self, ctx, user_url: typing.Union[discord.Member, str]=None):
        if user_url is None and not ctx.message.attachments:
            img = ctx.author.avatar_url_as(format="png")
        elif user_url is not None:
            if isinstance(user_url, discord.Member):
                img = user_url.avatar_url_as(format="png")
            elif validators.url(user_url):
                img = user_url
            else:
                raise commands.BadArgument
        elif user_url is None and ctx.message.attachments:
            img = ctx.message.attachments[0].url
        return img

    async def send_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url=resp["message"])
        embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> awooify (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def awooify(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Awooify an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=awooify&url={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> blurpify (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def blurpify(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Blurpify an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=blurpify&image={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> deepfry (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def deepfry(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Deepfry an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=deepfry&image={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> gettext <attach an image OR image url>`")
    async def gettext(self, ctx, url=None):
        """Attempts to read text from an image.
        Format like this: `<prefix> gettext <attach an image OR image url>`
        Note: Works best with black text on a white background or vice versa
        """
        #* Aiohttp is being used here in this admittedly ugly block of code because for the life
        #* of me I can't get the requests library to work for this
        try:
            if url is None:
                if not ctx.message.attachments:
                    raise commands.BadArgument
                async with self.session.get(ctx.message.attachments[0].url) as resp:
                    img = IMG.open(io.BytesIO(await resp.read()))
            else:
                if validators.url(url):
                    async with self.session.get(url) as resp:
                        img = IMG.open(io.BytesIO(await resp.read()))
                else:
                    raise commands.BadArgument
        except OSError:
            await ctx.send("That's not an image file", delete_after=5.0)
            return await delete_message(ctx, 5)
        try:
            async with ctx.channel.typing():
                img = img.filter(ImageFilter.MedianFilter())
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2)
                img = img.convert("1")
                img.save("image.png")

                text = pytesseract.image_to_string(IMG.open("image.png"))
                os.remove("image.png")
                if text == "":
                    await ctx.send(
                        "I wasn't able to read any text from that image", delete_after=5.0)
                    return await delete_message(ctx, 5)
                elif len(text) > 1941:
                    await ctx.send("This text is too long for me to send here. Try an image "
                                    "that doesn't have so many words in it", delete_after=6.0)
                    return await delete_message(ctx, 6)
                else:
                    return await ctx.send(
                        f"Here's the text I was able to read from that image:\n```\n{text}```")
        except:
            await ctx.send("Hmm, something went wrong while I was trying to read the text from "
                           "this image. Try again", delete_after=6.0)
            return await delete_message(ctx, 6)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> iphonex (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def iphonex(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Places a picture inside of an iPhone X. Do what you will with the resulting pic"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=iphonex&url={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(aliases=["majik"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> magik (OPTIONAL)<@mention user OR "
                      "attach an image OR image url>`")
    async def magik(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Magikify an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=magik&image={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(aliases=["threat"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> threats (OPTIONAL)<@mention user "
                      "OR attach an image OR image url>`")
    async def threats(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Identify a threat to society"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=threats&url={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)


def setup(bot):
    bot.add_cog(Image(bot))
