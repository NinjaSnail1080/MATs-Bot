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
from bs4 import BeautifulSoup
import discord
import asyncio
import aiohttp
import ascii
import validators

import random
import re
import os

import config

#* MAT's Bot uses the NekoBot API for many of these commands.
#* More info at https://docs.nekobot.xyz/


class Fun:
    """Fun stuff!"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def send_image(self, ctx, resp):
        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.send(
            embed=discord.Embed(color=find_color(ctx)).set_image(url=resp["message"]))

    @commands.command()
    async def ascii(self, ctx, *, image=None):
        """Converts an image into ascii art. Will work for most images.
        Format like this: `<prefix> ascii <image URL>`
        """
        if image is not None and validators.url(image):
            try:
                with ctx.channel.typing():
                    art = ascii.loadFromUrl(image, 60, False)
                    if len(art) > 1994:
                        art = "".join(art.split())
                        split_art = re.findall(".{1,1920}", art)
                        for a in split_art:
                            art = re.sub("(.{60})", "\\1\n", a, 0, re.DOTALL)
                            await ctx.send(f"```{art}```")
                    else:
                        await ctx.send(f"```{art}```")
            except:
                await ctx.send("Huh, something went wrong. I wasn't able to convert this into "
                               "ascii art. Try again with a different image.", delete_after=7.0)
                return await delete_message(ctx, 7)
        elif image is None:
            await ctx.send("You need to include a link to the image you want to convert.\n\n"
                           "Format like this: `<prefix> ascii <image URL>`", delete_after=10.0)
            return await delete_message(ctx, 10)
        elif not validators.url(image):
            await ctx.send("Invalid url. The link to your image needs to look something like this"
                           ":\n\n`http://www.example.com/something/image.png`", delete_after=10.0)
            return await delete_message(ctx, 10)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> baguette (OPTIONAL)<@mention user>`")
    async def baguette(self, ctx, user: discord.Member=None):
        """Eat a baguette
        Format like this: `<prefix> baguette (OPTIONAL)<@mention user>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        img = user.avatar_url_as(format="png")
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=baguette&url={img}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> bigletter <text>`", aliases=["bigletters"])
    async def bigletter(self, ctx, *, text: str):
        """Turn text into :regional_indicator_b: :regional_indicator_i: :regional_indicator_g:   :regional_indicator_l: :regional_indicator_e: :regional_indicator_t: :regional_indicator_t: :regional_indicator_e: :regional_indicator_r: :regional_indicator_s:
        Format like this: `<prefix> bigletter <text>`
        """
        await ctx.channel.trigger_typing()
        async with self.session.get(
            f"https://nekobot.xyz/api/text?type=bigletter&text={text}") as w:
            resp = await w.json()

        if not resp["success"]:
            await ctx.send("Huh, something went wrong. I wasn't able to get the text. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

        try:
            await ctx.send(resp["message"])
        except discord.HTTPException:
            await ctx.send("The message was too large for me to send. Try again with a shorter "
                           "one", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> captcha (OPTIONAL)<@mention user>`")
    async def captcha(self, ctx, user: discord.Member=None):
        """Turns a user's avatar into a CAPTCHA "I am not a robot" test
        Format like this: `<prefix> captcha (OPTIONAL)<@mention user>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        img = user.avatar_url_as(format="png")
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=captcha&url={img}"
            f"&username={user.display_name}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> changemymind <text>`")
    async def changemymind(self, ctx, *, text: str):
        """Dare people to change your mind
        Format like this: `<prefix> changemymind <text>`
        """
        await ctx.channel.trigger_typing()
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=changemymind&text={text}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(aliases=["clydify"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> clyde <text>`")
    async def clyde(self, ctx, *, text: str):
        """Clydify text (Have Clyde type some text)
        Format like this: `<prefix> clyde <text>`
        """
        await ctx.channel.trigger_typing()
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=clyde&text={text}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command()
    async def coinflip(self, ctx):
        """Flips a coin, pretty self-explanatory"""

        coin = random.choice(["Heads!", "Tails!"])
        temp = await ctx.send("Flipping...")
        with ctx.channel.typing():
            await asyncio.sleep(1)
            await temp.delete()
            await ctx.send(coin)

    @commands.command()
    async def commitstrip(self, ctx):
        """Posts a random CommitStrip comic (Only for programmers)"""

        try:
            with ctx.channel.typing():
                async with self.session.get("http://www.commitstrip.com/?random=1") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    title = soup.find("h1", "entry-title").get_text()
                    date = soup.find("time", "entry-date").get_text()
                    comic = soup.find("div", "entry-content")
                    image = comic.p.img["src"]

            embed = discord.Embed(title=title, color=find_color(ctx), url=url)

            embed.set_author(name="CommitStrip",
                             url="http://www.commitstrip.com/en/?")
            embed.set_image(url=image)
            embed.set_footer(text="Published: " + date)

            await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=6.0)
            return await delete_message(ctx, 6)

    @commands.command(aliases=["shitpost"])
    async def copypasta(self, ctx):
        """Posts a random copypasta/shitpost"""

        try:
            with ctx.channel.typing():
                async with self.session.get(
                    "https://www.reddit.com/r/copypasta/hot.json?sort=hot",
                    headers=config.R_USER_AGENT) as w:

                    resp = await w.json()
                    data = random.choice(resp["data"]["children"])["data"]

                    embed = discord.Embed(
                        title=data["title"], url=data["url"], description=data["selftext"],
                        color=find_color(ctx))
                    embed.set_footer(text=f"👍 - {data['score']}")

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong and I wasn't able to get a copypasta. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(aliases=["ch", "cyha", "cyahap", "c&h"])
    async def cyhap(self, ctx):
        """Posts a random Cyanide & Happiness comic"""

        try:
            with ctx.channel.typing():
                async with self.session.get("http://explosm.net/comics/random") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    number = url.replace("http://explosm.net/comics/", "")[:-1]
                    image = "http:" + soup.find("img", id="main-comic")["src"]
                    info = soup.find("div", id="comic-author").get_text()

                    embed = discord.Embed(
                        title=f"Cyanide and Happiness #{number}", url=url, color=find_color(ctx))
                    embed.set_author(name="Explosm", url="http://explosm.net/")
                    embed.set_image(url=image)
                    embed.set_footer(text=info)

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=6.0)
            return await delete_message(ctx, 6)

    @commands.command(brief="The number of sides must be an **integer above 2**. Try again.")
    async def diceroll(self, ctx, sides: int=6):
        """Rolls a dice. By default a 6-sided one though the number of sides can be specified.
        Format like this: `<prefix> diceroll (OPTIONAL)<# of sides>`
        """
        if sides <= 2:
            await ctx.send("The number of sides must be an **integer above 2**. Try again.",
                           delete_after=5.0)
            return await delete_message(ctx, 5)

        dice = str(random.randint(1, sides))
        temp = await ctx.send(f"Rolling a {sides}-sided dice...")
        with ctx.channel.typing():
            await asyncio.sleep(1.5)
            await temp.delete()
            await ctx.send(dice + "!")

    @commands.command()
    async def f(self, ctx):
        """Pay your respects"""

        msg = await ctx.send(
            f"{ctx.author.mention} has paid their respects. Press F to pay yours.")
        await msg.add_reaction("\U0001f1eb")

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> phcomment <@mention user> <comment>`")
    async def phcomment(self, ctx, user: discord.Member, *, comment: str):
        """Generate a PornHub comment!
        Format like this: `<prefix> phcomment <@mention user> <comment>`
        """
        await ctx.channel.trigger_typing()
        pfp = user.avatar_url_as(format="png")
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=phcomment"
                                    f"&image={pfp}&text={comment}"
                                    f"&username={user.display_name}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(aliases=["kannafy"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> kannagen <text>`")
    async def kannagen(self, ctx, *, text: str):
        """Kannafy some text (Sorry for the poor image quality)
        Format like this: `<prefix> kannagen <text>`
        """
        await ctx.channel.trigger_typing()
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=kannagen&text={text}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> kidnap (OPTIONAL)<@mention user>`")
    async def kidnap(self, ctx, user: discord.Member=None):
        """A group of anime girls kidnap you and you get featured on some YouTube video
        Format like this: `<prefix> kidnap (OPTIONAL)<@mention user>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        img = user.avatar_url_as(format="png")
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=kidnap&image={img}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> kms (OPTIONAL)<user>`")
    async def kms(self, ctx, user: discord.Member=None):
        """KMS
        Format like this: <prefix> kms (OPTIONAL)<user>
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        img = user.avatar_url_as(format="png")
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=kms&url={img}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command()
    async def lenny(self, ctx):
        """A list of Lenny faces for all your copypasting needs"""

        embed = discord.Embed(
            title="A list of Lenny faces for all your copypasting needs",
            color=find_color(ctx), url="https://www.lennyfaces.net/")

        embed.add_field(name="Classic", value="( ͡° ͜ʖ ͡°)")
        embed.add_field(name="Pissed Off", value="( ͠° ͟ʖ ͡°)")
        embed.add_field(name="Winky", value="( ͡~ ͜ʖ ͡°)")
        embed.add_field(name="Wide-Eyed", value="( ͡◉ ͜ʖ ͡◉)")
        embed.add_field(name="Wide-Eyed 2", value="( ͡☉ ͜ʖ ͡☉)")
        embed.add_field(name="Happy", value="( ͡ᵔ ͜ʖ ͡ᵔ )")
        embed.add_field(name="Sad", value="( ͡° ʖ̯ ͡°)")
        embed.add_field(name="With Ears", value="ʕ ͡° ͜ʖ ͡°ʔ")
        embed.add_field(name="Communist", value="(☭ ͜ʖ ☭)")
        embed.set_footer(text="From: https://www.lennyfaces.net/")

        await ctx.send(embed=embed)

    @commands.command()
    async def meirl(self, ctx):
        """Posts that are u irl"""

        try:
            with ctx.channel.typing():
                async with self.session.get(
                    f"https://www.reddit.com/r/{random.choice(['meirl', 'me_irl'])}/hot.json?"
                    "sort=hot", headers=config.R_USER_AGENT) as w:

                    resp = await w.json()
                    data = random.choice(resp["data"]["children"])["data"]

                    embed = discord.Embed(
                        title=data["title"], url="https://www.reddit.com" + data["permalink"],
                        color=find_color(ctx))
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"👍 - {data['score']}")

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong and I wasn't able to get a meme. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    async def meme(self, ctx):
        """Posts a dank meme"""

        try:
            with ctx.channel.typing():
                async with self.session.get(
                    f"https://www.reddit.com/r/{random.choice(['memes', 'dankmemes'])}/hot.json?"
                    "sort=hot", headers=config.R_USER_AGENT) as w:

                    resp = await w.json()
                    data = random.choice(resp["data"]["children"])["data"]

                    embed = discord.Embed(
                        title=data["title"], url="https://www.reddit.com" + data["permalink"],
                        color=find_color(ctx))
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"👍 - {data['score']}")

                    await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong and I wasn't able to get a meme. "
                           "Try again", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(aliases=["weirdspeak"])
    async def mock(self, ctx, *, stuff: str=None):
        """Say something and I'll mock you"""

        if stuff is None:
            await ctx.send("Dude, you need to say something for me to mock", delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.channel.trigger_typing()

        embed = discord.Embed(color=find_color(ctx))
        embed.set_image(url="https://i.imgur.com/8NmOT8w.jpg")
        stuff = list(stuff.lower())
        mock = []
        for i in stuff:
            if i == "c":
                if random.randint(1, 2) == 1:
                    i = "k"
            elif i == "k":
                if random.randint(1, 2) == 1:
                    i = "c"
            elif i == "x":
                if random.randint(1, 2) == 1:
                    i = "ks"
            if random.randint(1, 2) == 1:
                i = i.upper()
            mock.append(i)

        await ctx.send(content="".join(mock), embed=embed)

    @commands.command()
    async def reverse(self, ctx, *, stuff: str=None):
        """Reverse the text you give me!"""

        if stuff is None:
            await ctx.send("Dude, you need to give me some text to reverse", delete_after=5.0)
            return await delete_message(ctx, 5)

        else:
            stuff = stuff[::-1]
            stuff = stuff.replace("@everyone", "`@everyone`")
            stuff = stuff.replace("@here", "`@here`")

            await ctx.send(stuff)

    @commands.command(aliases=["print", "printf", "System.out.println", "echo", "std::cout<<",
                               "puts"])
    async def say(self, ctx, *, stuff: str=None):
        """Make me say something!"""

        if stuff is None:
            await ctx.send("Dude, you need to give me something to say", delete_after=5.0)
            return await delete_message(ctx, 5)

        else:
            stuff = stuff.replace("@everyone", "`@everyone`")
            stuff = stuff.replace("@here", "`@here`")

            await ctx.send(stuff)

    @commands.command(brief="You didn't format the command correctly. You're supposed to include "
                      "some text for the tweet `<prefix> trumptweet <tweet>`")
    async def trumptweet(self, ctx, *, tweet: str):
        """Tweet as Trump!
        Format like this: `<prefix> trumptweet <tweet>`
        """
        await ctx.channel.trigger_typing()
        async with self.session.get(
            f"https://nekobot.xyz/api/imagegen?type=trumptweet&text={tweet}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> tweet <twitter usernamer> <tweet>`")
    async def tweet(self, ctx, user: str, *, tweet: str):
        """Tweet as yourself or another twitter user!
        Format like this: `<prefix> tweet <twitter username> <tweet>`
        """
        await ctx.channel.trigger_typing()
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=tweet"
                                    f"&username={user}&text={tweet}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> whowouldwin <@mention user 1> (OPTIONAL)<@mention user 2>`")
    async def whowouldwin(self, ctx, user1: discord.Member, user2: discord.Member=None):
        """Who would win?
        Format like this: `<prefix> whowouldwin <@mention user 1> (OPTIONAL)<@mention user 2>`
        """
        await ctx.channel.trigger_typing()
        if user2 is None:
            user2 = ctx.author
        img1 = user1.avatar_url_as(format="png")
        img2 = user2.avatar_url_as(format="png")
        async with self.session.get("https://nekobot.xyz/api/imagegen?type=whowouldwin"
                                    f"&user1={img1}&user2={img2}") as w:
            resp = await w.json()
            await self.send_image(ctx, resp)

    @commands.command()
    async def xkcd(self, ctx):
        """Posts a random xkcd comic"""
        try:
            with ctx.channel.typing():
                async with self.session.get("https://c.xkcd.com/random/comic/") as w:
                    soup = BeautifulSoup(await w.text(), "lxml")

                    url = str(w.url)
                    number = url.replace("https://xkcd.com/", "")[:-1]
                    title = soup.find("div", id="ctitle").get_text()
                    comic = soup.find("div", id="comic")
                    image = "https:" + comic.img["src"]
                    caption = comic.img["title"]

            embed = discord.Embed(
                title=f"{title} | #{number}", color=find_color(ctx), url=url)

            embed.set_author(name="xkcd", url="https://xkcd.com/")
            embed.set_image(url=image)
            embed.set_footer(text=caption)

            await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. It looks like servers are down so I wasn't"
                           " able to get a comic. Try again in a little bit.", delete_after=6.0)
            return await delete_message(ctx, 6)


def setup(bot):
    bot.add_cog(Fun(bot))
