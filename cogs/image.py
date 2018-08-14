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

# from mat import find_color
from mat_experimental import find_color

from discord.ext import commands
import discord
import asyncio
import aiohttp

#* MAT's Bot uses the NekoBot API for most of these commands.
#* More info at https://docs.nekobot.xyz/


class Image:
    """Image Manipulation commands"""
    #TODO: Clean up the code

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def get_image(self, ctx, user: discord.Member=None):
        if user is None and not ctx.message.attachments:
            img = ctx.author.avatar_url_as(format="png")
        elif user is not None:
            img = user.avatar_url_as(format="png")
        elif user is None and ctx.message.attachments:
            img = ctx.message.attachments[0].url
        return img

    async def send_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=6.0)
            await asyncio.sleep(6)
            return await ctx.message.delete()

        await ctx.send(
            embed=discord.Embed(color=find_color(ctx)).set_image(url=resp["message"]))

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> awooify (OPTIONAL)<@mention user OR attach an image>`")
    async def awooify(self, ctx, member: discord.Member=None):
        """Awooify an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member)
            async with self.session.get(
                    f"https://nekobot.xyz/api/imagegen?type=awooify&url={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> blurpify (OPTIONAL)<@mention user OR attach an image>`")
    async def blurpify(self, ctx, member: discord.Member=None):
        """Blurpify an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=blurpify&image={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> deepfry (OPTIONAL)<@mention user OR attach an image>`")
    async def deepfry(self, ctx, member: discord.Member=None):
        """Deepfry an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=deepfry&image={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> iphonex (OPTIONAL)<@mention user OR attach an image>`")
    async def iphonex(self, ctx, member: discord.Member=None):
        """Places a picture inside of an iPhone X. Do what you will with the resulting pic"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=iphonex&url={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)

    @commands.command(aliases=["majik"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> magik (OPTIONAL)<@mention user OR "
                      "attach an image>`")
    async def magik(self, ctx, member: discord.Member=None):
        """Magikify an image or a member's avatar"""

        with ctx.channel.typing():
            img = self.get_image(ctx, member)
            async with self.session.get(
                f"https://nekobot.xyz/api/imagegen?type=magik&image={img}") as w:
                resp = await w.json()
                await self.send_image(ctx, resp)


def setup(bot):
    bot.add_cog(Image(bot))
