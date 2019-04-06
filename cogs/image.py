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

from utils import find_color, delete_message, send_nekobot_image, send_dank_memer_img

from discord.ext import commands
from PIL import Image as IMG
from PIL import ImageEnhance, ImageFilter
import discord
import aiohttp
import validators
import pytesseract
import ascii
import urllib3
import rapidjson as json

import typing
import functools
import io
import os
import re
import uuid

import config

#* MAT's Bot uses the NekoBot API for most of these commands.
#* More info at https://docs.nekobot.xyz/


class Image(commands.Cog):
    """Image Manipulation commands"""

    def __init__(self, bot):
        self.bot = bot

        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

        #* Disables warnings that show up when the "ascii" command is used
        urllib3.disable_warnings()

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

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> affect (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def affect(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """How does it affect your baby?"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/affect?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> america (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def america(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Overlay the American flag over an image"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/america?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> ascii (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def ascii(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Converts an image or a member's avatar into ascii art. Will work for most images
        __Note__: For some images, you might want to zoom out to see the full ascii art (Ctrl – OR ⌘ –)
        ~~Rip mobile users~~
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
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://nekobot.xyz/api/imagegen?type=awooify&url={img}") as w:
                    resp = await w.json()
                    await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> blurpify (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def blurpify(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Blurpify an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://nekobot.xyz/api/imagegen?type=blurpify&image={img}") as w:
                    resp = await w.json()
                    await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> brazzers (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def brazzers(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Add the Brazzers logo to an image"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/brazzers?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> cancer (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def cancer(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """What is cancer?"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/cancer?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

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
                async with aiohttp.ClientSession() as session:
                    async with session.post("https://captionbot.azurewebsites.net/api/messages",
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
                      "this: `<prefix> america (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def communism(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Overlay the Communist flag over an image"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/communism?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> corporate <picture 1> <picture 2>`\n\nFor the pictures, "
                      "use image urls or @mention members instead of attaching pictures")
    async def corporate(self, ctx, member_url_1: typing.Union[discord.Member, str], member_url_2: typing.Union[discord.Member, str]):
        """Corporate needs you to find the differences between this picture and this picture
        Format like this: `<prefix> corporate <picture 1> <picture 2>`
        __Note__: For this command, use image urls or @mention members instead of attaching pictures
        """
        with ctx.channel.typing():
            img1 = await self.get_image(ctx, member_url_1)
            img2 = await self.get_image(ctx, member_url_2)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://dankmemer.services/api/corporate?avatar1={img1}&avatar2={img2}",
                    headers=config.DANK_MEMER_AUTH) as w:

                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> deepfry (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def deepfry(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Deepfry an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/deepfry?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> delete (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def delete(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Delete this garbage"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/delete?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> disability (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def disability(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Not all disabilities look like this: :wheelchair:"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/disability?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> door (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def door(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """\\*Enters\\* \\*Immediately leaves\\*"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/door?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> failure (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def failure(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Today's class is about failures..."""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/failure?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> fakenews (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def fakenews(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """TURN OFF THE FAKE NEWS"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/fakenews?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> gay (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def gay(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Overlay the gay pride flag over an image"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/gay?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

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
            filename = f"image-{uuid.uuid4()}.png"
            img.save(filename)
            text = pytesseract.image_to_string(IMG.open(filename))
            os.remove(filename)

            return text

        try:
            with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(await self.get_image(ctx, member_url)) as resp:
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
                      "this: `<prefix> hitler (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`", aliases=["wth"])
    async def hitler(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Worse than Hitler!"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/hitler?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> invert (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def invert(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Invert the colors of an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/invert?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> iphonex (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def iphonex(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Places a picture inside of an iPhone X. Do what you will with the resulting pic"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://nekobot.xyz/api/imagegen?type=iphonex&url={img}") as w:
                    resp = await w.json()
                    await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> jail (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def jail(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Put someone or something in jail"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/jail?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(aliases=["magikify"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> magik (OPTIONAL)<@mention user OR "
                      "attach an image OR image url>`")
    async def magik(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Magikify an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://nekobot.xyz/api/imagegen?type=magik&image={img}") as w:
                    resp = await w.json()
                    await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> radialblur (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def radialblur(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Radially blur an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/radialblur?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> sickban (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def sickban(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """BAN THIS SICK FILTH"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/sickban?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> tablet (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`", aliases=["airpods"])
    async def tablet(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Drawing an image on a tablet"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/airpods?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(aliases=["threat"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> threats (OPTIONAL)<@mention user "
                      "OR attach an image OR image url>`")
    async def threats(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Identify a threat to society"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://nekobot.xyz/api/imagegen?type=threats&url={img}") as w:
                    resp = await w.json()
                    await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> trash (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def trash(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Turn someone or something into trash"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/trash?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> triggered (OPTIONAL)<@mention user>`")
    async def triggered(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """TRIGGERED"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/trigger?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp, True)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> ugly (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def ugly(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """It's even uglier up close"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/ugly?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> wanted (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def wanted(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """WANTED: Dead or Alive"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/wanted?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> warp (OPTIONAL)<@mention user OR attach an image OR "
                      "image url>`")
    async def warp(self, ctx, member_url: typing.Union[discord.Member, str]=None):
        """Heavily warp an image or a member's avatar"""

        with ctx.channel.typing():
            img = await self.get_image(ctx, member_url)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://dankmemer.services/api/warp?avatar1={img}",
                                       headers=config.DANK_MEMER_AUTH) as w:
                    resp = await w.read()
                    await send_dank_memer_img(self.bot.loop, ctx, resp)


def setup(bot):
    bot.add_cog(Image(bot))
