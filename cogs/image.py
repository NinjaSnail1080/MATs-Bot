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
import ascii

import typing
import functools
import io
import os
import re

import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

#* MAT's Bot uses the NekoBot API for most of these commands.
#* More info at https://docs.nekobot.xyz/


class Image:
    """Image Manipulation commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def get_image(self, ctx, user_url: typing.Union[discord.Member, str]=None):
        if user_url is None and not ctx.message.attachments:
            found = False
            async for m in ctx.channel.history(limit=10):
                if m.embeds:
                    img = m.embeds[0].image.url
                    if img is not discord.Embed.Empty:
                        found = True
                        break
                if m.attachments:
                    img = m.attachments[0].url
                    found = True
                    break
            if not found:
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

    async def send_nekobot_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url=resp["message"])
        embed.set_footer(text=f"{ctx.command.name} | {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> ascii (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def ascii(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Converts an image or a member's avatar into ascii art. Will work for most images
        __Note__: For some images, you might want to zoom out to see the full ascii art (Ctrl – OR ⌘ –)
        """

        def make_ascii(url: str, columns: int, color: bool):
            ascii_art = ascii.loadFromUrl(url, columns, color)
            return ascii_art

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            art = await self.bot.loop.run_in_executor(
                None, functools.partial(make_ascii, img, 60, False))
            if len(art) > 1994:
                art = "".join(art.split())
                split_art = re.findall(".{1,1920}", art)
                for a in split_art:
                    art_portion = re.sub("(.{60})", "\\1\n", a, 0, re.DOTALL)
                    await ctx.send(f"```{art_portion}```")
            else:
                await ctx.send(f"```{art}```")

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> awooify (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def awooify(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Awooify an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=awooify&url={img}") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> blurpify (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def blurpify(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Blurpify an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=blurpify&image={img}") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command(aliases=["caption"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> caption (OPTIONAL)<@mention user OR "
                      "attach an image OR image url>`")
    async def captionbot(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """The CaptionBot AI will attempt to understand the content of an image and describe it"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            headers = {"Content-Type": "application/json; charset=utf-8"}
            payload = {"Content": img, "Type": "CaptionRequest"}
            try:
                async with self.session.post("https://captionbot.azurewebsites.net/api/messages",
                                             headers=headers, json=payload) as w:
                    caption = await w.text()
                embed = discord.Embed(
                    title=str(caption),
                    description="*Powered by [CaptionBot](https://www.captionbot.ai/)*",
                    color=find_color(ctx))
                embed.set_image(url=img)
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("\U00002705")
                await msg.add_reaction("\U0000274c")
                await msg.add_reaction("\U0001f602")
            except:
                await ctx.send("Huh, something went wrong. I wasn't able to get the data. Try "
                               "again later", delete_after=5.0)
                return await delete_message(ctx, 5)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> deepfry (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def deepfry(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Deepfry an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=deepfry&image={img}") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> gettext (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def gettext(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """*Attempts* to read text from an image.
        Note: Works best with black text on a white background or vice versa
        """
        def read_image(read):
            try:
                img = IMG.open(io.BytesIO(read))
            except OSError:
                return None

            img = img.filter(ImageFilter.MedianFilter())
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2)
            img = img.convert("1")
            img.save("image.png")
            text = pytesseract.image_to_string(IMG.open("image.png"))
            os.remove("image.png")

            return text

        try:
            with ctx.channel.typing():
                async with self.session.get(await self.get_image(ctx, member_url)) as resp:
                    bytes = await resp.read()

                text = await self.bot.loop.run_in_executor(
                     None, functools.partial(read_image, bytes))
                if text is None:
                    await ctx.send("That's not an image file", delete_after=5.0)
                    return await delete_message(ctx, 5)
                elif text == "":
                    await ctx.send(
                        "I wasn't able to read any text from that image", delete_after=5.0)
                    return await delete_message(ctx, 5)
                elif len(text) > 1941:
                    await ctx.send("This text is too long for me to send here. Try an image that "
                                   "doesn't have so many words in it", delete_after=6.0)
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
            img = await self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=iphonex&url={img}") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command(aliases=["magikify"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> magik (OPTIONAL)<@mention user OR "
                      "attach an image OR image url>`")
    async def magik(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Magikify an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=magik&image={img}") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)

    @commands.command(aliases=["threat"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> threats (OPTIONAL)<@mention user "
                      "OR attach an image OR image url>`")
    async def threats(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Identify a threat to society"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=threats&url={img}") as w:
                resp = await w.json()
                await self.send_nekobot_image(ctx, resp)


def setup(bot):
    bot.add_cog(Image(bot))
