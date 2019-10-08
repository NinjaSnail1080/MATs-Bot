"""
    MAT's Bot: An open-source, general purpose Discord bot written in Python.
    Copyright (C) 2018  NinjaSnail1080  (Discord Username: @NinjaSnail1080#8581)

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

from utils import find_color, delete_message, get_reddit, send_nekobot_image, send_dank_memer_img, has_voted, ChannelNotNSFW

from discord.ext import commands
from bs4 import BeautifulSoup
from PIL import Image
from zalgo_text.zalgo import zalgo
from akinator.async_aki import Akinator
import discord
import validators
import akinator as akinator_lib
import wordcloud as wc

import random
import datetime
import asyncio
import os
import io
import re
import functools
import string
import typing
import uuid

import config

#* MAT's Bot uses the NekoBot API and Dank Memer API for many of these commands.
#* More info at https://docs.nekobot.xyz/ for NekoBot and https://dankmemer.services/ for Dank Memer


class Fun(commands.Cog):
    """Fun stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball", aliases=["8", "ask"],
                      brief="You need to ask a question to get an answer")
    async def _8ball(self, ctx, question: str):
        """Ask a question to the Magic 8-Ball!"""

        temp = await ctx.send("Answering...")
        await ctx.channel.trigger_typing()

        affirmative = ["It is certain", "As I see it, yes", "It is decidedly so", "Most likely",
                       "Without a doubt", "Outlook good", "Yes - definitely", "Yes",
                       "You may rely on it", "Signs point to yes"]
        noncommittal = ["Reply hazy, try again", "Ask again later", "Better not tell you now",
                        "Cannot predict now", "Concentrate and ask again"]
        negative = ["Don't count on it", "My reply is no", "My sources say no",
                    "Outlook not so good", "Very doubtful"]

        answer = random.choice(affirmative + noncommittal + negative)

        embed = discord.Embed(color=find_color(ctx))
        if answer in affirmative:
            embed.set_author(name=answer, icon_url="https://i.imgur.com/WcPjzNt.png")
        elif answer in noncommittal:
            embed.set_author(name=answer, icon_url="https://i.imgur.com/UdRIQ2S.png")
        elif answer in negative:
            embed.set_author(name=answer, icon_url="https://i.imgur.com/voWO5qd.png")

        await asyncio.sleep(1)
        await temp.delete()
        await ctx.send(embed=embed)

    @commands.command(brief="You need to include some text for the baby to say",
                      aliases=["abandoned", "disown", "disowned"])
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def abandon(self, ctx, *, text: str):
        """Disowned!
        Format like this: `<prefix> abandon <text for the baby to say>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/abandon?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> aborted (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def aborted(self, ctx, member: discord.Member=None):
        """All the Reasons I Should Have Been Aborted
        Format like this: `<prefix> aborted (OPTIONAL)<member>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(
                f"https://dankmemer.services/api/aborted?avatar1={img}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(aliases=["randface", "randomface"], hidden=True)
    async def aiface(self, ctx):
        """Gets a picture of a randomly generated face from [thispersondoesnotexist.com](https://thispersondoesnotexist.com/)
        __How it works__: This website uses an AI to generate a picture of a realistic human face, so believe it or not, the people you see when you use this command don't actually exist in real life.
        """
        def save_image(read):
            img = Image.open(io.BytesIO(read))
            filename = f"aiface-{uuid.uuid4()}.png"
            img.save(filename)
            return filename

        with ctx.channel.typing():
            async with self.bot.session.get("https://thispersondoesnotexist.com/image") as w:
                resp = await w.read()

            filename = await self.bot.loop.run_in_executor(
                None, functools.partial(save_image, resp))

            embed = discord.Embed(description="Courtesy of [thispersondoesnotexist.com]"
                                  "(https://thispersondoesnotexist.com/)",
                                  color=find_color(ctx))
            await ctx.send("The below image was generated by an AI. It is NOT a picture of "
                           "a real person's face",
                           embed=embed, file=discord.File(filename))
        if os.path.isfile(filename):
            os.remove(filename)

    @commands.command(aliases=["aki"], hidden=True)
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def akinator(self, ctx):
        """Start a game with the legendary Akinator!"""

        aki_up = ["https://i.imgur.com/ACUMdmP.png", "https://i.imgur.com/MV0i5Gn.png",
                  "https://i.imgur.com/RqXE9qK.png", "https://i.imgur.com/Cl9ZRlQ.png"]
        aki_down = ["https://i.imgur.com/9Ye1mO6.png", "https://i.imgur.com/ViH8vlJ.png",
                    "https://i.imgur.com/AKyk283.png", "https://i.imgur.com/Dt75nWE.png",
                    "https://i.imgur.com/myNRsFe.png", "https://i.imgur.com/MLhxgPk.png"]

        yes = "<:Yes:552243795358646282>"
        no = "<:No:552244932669341696>"
        idk = "<:IDontKnow:552251490304131102>"
        p = "<:Probably:552243821958922298>"
        pn = "<:ProbablyNot:552248243145277462>"
        back = "<:BackToPreviousQuestion:552254952744157184>"
        cancel = "<:CancelGame:552255531499126784>"

        reactions_list = [yes, no, idk, p, pn, back, cancel]

        def check_aki_reactions(message, author, in_game=False):
            def check(reaction, user):
                if reaction.message.id != message.id or user != author:
                    return False
                elif reaction.emoji == "\U00002611":
                    return True
                elif reaction.emoji == "\U0000274c":
                    return True
                return False

            def check_game(reaction, user):
                if reaction.message.id != message.id or user != author:
                    return False
                elif str(reaction.emoji) in reactions_list:
                    return True
                return False

            if in_game:
                return check_game
            else:
                return check

        def add_to_embed(embed, in_game=True):
            if in_game:
                embed.set_author(
                    name=f"{ctx.author.name} is playing", icon_url=ctx.author.avatar_url)
            else:
                embed.set_author(
                    name=f"{ctx.author.name}'s game has ended", icon_url=ctx.author.avatar_url)
            embed.set_footer(
                text="Akinator.com\u2000|\u2000Brought to you by MAT's Bot",
                icon_url="https://is4-ssl.mzstatic.com/image/thumb/Purple128/v4/f5/11/6d/f5116d77"
                "-c0cf-3a38-f2fa-e2fa1624d594/source/512x512bb.jpg")

        async def play_akinator(game, player):
            await game.edit(content="***Loading...***")
            aki = Akinator()
            try:
                await aki.start_game()
            except:
                #* If main English server is down
                await aki.start_game("en2")
            target_progress = 85
            previous_progress = aki.progression #* 0 at the start

            while True:
                await game.clear_reactions()
                for react in reactions_list:
                    await game.add_reaction(react)

                while aki.progression <= target_progress:
                    embed = discord.Embed(
                        title=f"{aki.step + 1}. {aki.question}",
                        description="Answer with one of the emojis below. Mouseover them to see "
                        "what each one means", color=find_color(ctx))
                    add_to_embed(embed)
                    if aki.step == 0:
                        embed.set_thumbnail(url="https://i.imgur.com/ACUMdmP.png")
                    else:
                        if aki.progression > previous_progress:
                            embed.set_thumbnail(url=random.choice(aki_up))
                        else:
                            embed.set_thumbnail(url=random.choice(aki_down))

                    await game.edit(content=None, embed=embed)
                    try:
                        react, user = await self.bot.wait_for(
                            "reaction_add", timeout=600,
                            check=check_aki_reactions(game, player, True))
                    except asyncio.TimeoutError:
                        await ctx.send(
                            f"{player.mention} took too long to answer and their "
                            "Akinator game timed out. Next time, don't wait longer than 10 "
                            "minutes to answer each question")
                        await game.delete()
                        return await ctx.message.delete()

                    if str(react.emoji) == cancel:
                        await ctx.send(
                            f"Ok, {ctx.author.mention}'s Akinator game has been cancelled",
                            delete_after=5.0)
                        await delete_message(ctx, 5)
                        return await game.delete()

                    previous_progress = aki.progression
                    await game.edit(content="***Loading...***")
                    try:
                        if str(react.emoji) == yes:
                            await aki.answer(0)
                        elif str(react.emoji) == no:
                            await aki.answer(1)
                        elif str(react.emoji) == idk:
                            await aki.answer(2)
                        elif str(react.emoji) == p:
                            await aki.answer(3)
                        elif str(react.emoji) == pn:
                            await aki.answer(4)
                        elif str(react.emoji) == back:
                            try:
                                await aki.back()
                            except akinator_lib.CantGoBackAnyFurther:
                                pass
                    except akinator_lib.AkiNoQuestions:
                        break
                    await game.remove_reaction(react, user)

                await aki.win()
                embed = discord.Embed(title="I think of...",
                                      description=f"**{aki.name}** ({aki.description})\n\n"
                                      "Was I correct?",
                                      color=find_color(ctx))
                embed.set_image(url=aki.picture)
                embed.set_thumbnail(url=random.choice(aki_up))
                add_to_embed(embed)

                await game.clear_reactions()
                await game.edit(content=None, embed=embed)
                await game_msg.add_reaction("\U00002611")
                await game_msg.add_reaction("\U0000274c")

                try:
                    react, user = await self.bot.wait_for(
                        "reaction_add", timeout=300, check=check_aki_reactions(game, player))
                except asyncio.TimeoutError:
                    await ctx.send(
                        f"{player.mention} took way too long to react after Akinator guessed who "
                        "their character was in the game they started, so the session timed out. "
                        "Sorry, shouldn't have waited so long. There's a time limit of 5 minutes")
                    await game.delete()
                    return ctx.message.delete()

                if react.emoji == "\U00002611":
                    embed = discord.Embed(
                        title="Great, guessed right one more time!",
                        description=f"**{aki.name}** ({aki.description})",
                        color=find_color(ctx))
                    embed.set_image(url="https://i.imgur.com/cb6SLnJ.png")
                    add_to_embed(embed, False)

                    await game.clear_reactions()
                    return await game.edit(content=None, embed=embed)

                #* If the player selected the "no" emoji when Aki guessed their character
                if aki.progression > 99:
                    break
                embed = discord.Embed(title="Would you like to continue?", color=find_color(ctx))
                add_to_embed(embed)

                await game.remove_reaction(react, user)
                await game.edit(content=None, embed=embed)

                try:
                    react, user = await self.bot.wait_for(
                        "reaction_add", timeout=300, check=check_aki_reactions(game, player))
                except asyncio.TimeoutError:
                    await ctx.send(
                        f"{player.mention} took way too long to react after Akinator guessed who "
                        "their character was in the game they started, so the session timed out. "
                        "Sorry, shouldn't have waited so long. There's a time limit of 5 minutes")
                    await game.delete()
                    return ctx.message.delete()

                if react.emoji == "\U00002611": #* Keep asking questions; continues the game loop
                    target_progress = 99
                    await game.edit(content="***Loading...***")
                else:
                    break

            #* If Aki loses
            embed = discord.Embed(
                title="Bravo, you have defeated me!",
                description="I couldn't guess your character",
                color=find_color(ctx))
            embed.set_image(url="https://i.imgur.com/Msmzzii.png")
            add_to_embed(embed, False)

            await game.clear_reactions()
            return await game.edit(content=None, embed=embed)

        #* Start of command
        return await ctx.send(
            "I'm sorry, but this command isn't working right now. My creator is still having "
            "trouble getting it to work. When he finally does, I'll be updated with the new code "
            "and you'll be able to play Akinator with me.\n\nBut for now, you'll have to settle "
            "with the website. Sorry about that")
        embed = discord.Embed(
            title="Hello, I am Akinator",
            description="Think about a real or fictional character. I will ask you questions and "
            "try to guess who it is.\n\nPress \U00002611 to play or \U0000274c to cancel",
            url="https://www.akinator.com", color=find_color(ctx))
        embed.set_image(
            url="https://en.akinator.com/bundles/elokencesite/images/akinator.png?v95")
        add_to_embed(embed)

        game_msg = await ctx.send(embed=embed)
        await game_msg.add_reaction("\U00002611")
        await game_msg.add_reaction("\U0000274c")

        try:
            react, user = await self.bot.wait_for(
                "reaction_add", timeout=120, check=check_aki_reactions(game_msg, ctx.author))
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention} took too long to react to the Akinator game "
                           "they started, so I had to cancel it", delete_after=6.0)
            await delete_message(ctx, 6)
            return await game_msg.delete()

        if react.emoji == "\U0000274c":
            await ctx.send(
                f"Ok, {ctx.author.mention}'s game has been cancelled", delete_after=5.0)
            await delete_message(ctx, 5)
            return await game_msg.delete()

        try:
            return await play_akinator(game_msg, ctx.author)
        except Exception as e:
            await game_msg.delete()
            await ctx.message.delete()
            return await ctx.send(
                f"```{e}```{ctx.author.mention}, due to an unexpected error, the Akinator game "
                "you started was cancelled. This is most likely an isolated incident. Try again "
                "later, and if the problem persists, please notify my creator, "
                f"**{self.bot.owner}**. You can reach him at my support server: "
                "https://discord.gg/khGGxxj")

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> armor <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def armor(self, ctx, *, text: str):
        """Nothing gets through this armor
        Format like this: `<prefix> armor <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/armor?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> bed <member 1> (OPTIONAL)<member 2>`\nIf you leave out "
                      "member 2, I'll just use you")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bed(self, ctx, member1: discord.Member, member2: discord.Member=None):
        """There's a monster under my bed!
        Format like this: `<prefix> bed <member 1> (OPTIONAL)<member 2>`
        """
        with ctx.channel.typing():
            if member2 is None:
                member2 = ctx.author
            img1 = member2.avatar_url_as(format="png")
            img2 = member1.avatar_url_as(format="png")
            #* Yes the above switch was intentional
            async with self.bot.session.get(
                f"https://dankmemer.services/api/bed?avatar1={img1}&avatar2={img2}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> bigletter <text>`", aliases=["bigletters"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bigletter(self, ctx, *, text: str):
        """Turn text into :regional_indicator_b: :regional_indicator_i: :regional_indicator_g:   :regional_indicator_l: :regional_indicator_e: :regional_indicator_t: :regional_indicator_t: :regional_indicator_e: :regional_indicator_r: :regional_indicator_s:
        Format like this: `<prefix> bigletter <text>`
        """
        await ctx.channel.trigger_typing()
        text = list(text.lower())
        bigletters = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱",
                      "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽",
                      "🇾", "🇿"]
        big = []

        for i in text:
            try:
                pos = string.ascii_lowercase.index(i)
                i = bigletters[pos] + " "
            except:
                if i == " ":
                    i = "  "
            big.append(i)

        await ctx.send("".join(big))

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> boo <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def boo(self, ctx, *, text: str):
        """**__BOO!__**
        Format like this: `<prefix> boo <text>`
        """
        with ctx.channel.typing():
            text = "BOO!, " + text.replace(",", "")
            async with self.bot.session.get(f"https://dankmemer.services/api/boo?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> brain <4 strings of text>`\n\nYou can only have 4 strings "
                      "of text. No more, no less. They must be separated by a comma and a space\n"
                      "__Example Usage__: `<prefix> brain This, is, just a, test`")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def brain(self, ctx, *, text: str):
        """Create an expanding brain meme with 4 panels
        Format like this: `<prefix> brain <text>`
        The text must be split into 4 parts for the 4 panels of the meme. Do this by putting a comma and a space between them
        __Example Usage__: `<prefix> brain This, is, just a, test`
        """
        if len(text.split(", ")) != 4:
            raise commands.BadArgument
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/brain?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> byemom (OPTIONAL)<member> <text to Google>`\nIf you don't "
                      "put the member, I'll just use you")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def byemom(self, ctx, member: typing.Optional[discord.Member]=None, *, text: str):
        """What do you Google when Mom leaves the house?
        Format like this: `<prefix> byemom (OPTIONAL)<member> <text to Google>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/byemom?avatar1={img}"
                                            f"&username1={member.display_name}&text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> captcha (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def captcha(self, ctx, user: discord.Member=None):
        """Turns a user's avatar into a CAPTCHA "I am not a robot" test
        Format like this: `<prefix> captcha (OPTIONAL)<@mention user>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        img = user.avatar_url_as(format="png")
        async with self.bot.session.get(f"https://nekobot.xyz/api/imagegen?type=captcha&url={img}"
                                        f"&username={user.display_name}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> changemymind <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def changemymind(self, ctx, *, text: str):
        """Dare people to change your mind
        Format like this: `<prefix> changemymind <text>`
        """
        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=changemymind"
                                        f"&text={text}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(aliases=["clydify"], brief="You didn't format the command correctly. It's "
                      "supposed to look like this: `<prefix> clyde <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def clyde(self, ctx, *, text: str):
        """Make Clyde say something
        Format like this: `<prefix> clyde <text>`
        """
        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=clyde"
                                        f"&text={text}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command()
    async def coinflip(self, ctx):
        """Flips a coin, pretty self-explanatory"""

        coin = random.choice(["Heads!", "Tails!"])
        temp = await ctx.send("Flipping...")
        with ctx.channel.typing():
            await asyncio.sleep(1)
            await temp.delete()
            await ctx.send(coin)

    @commands.command(aliases=["shitpost"])
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def copypasta(self, ctx):
        """Posts a random copypasta (Use in an NSFW channel)"""

        if not ctx.channel.is_nsfw():
            raise ChannelNotNSFW

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, False, False, "a copypasta", "copypasta")

    @commands.command(aliases=["crabrave"], brief="Invalid formatting. The command is supposed "
                      "to look like this: `<prefix> crab <text>`\n\nThe text you put to show up "
                      "in the crab rave video should be split into two parts with 2 dashes (--). "
                      "The first part will appear on top, and the second on the bottom\n__"
                      "Example usage__: `<prefix> crab first part of text--second part of text`")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def crab(self, ctx, *, text: str):
        """Start a crab rave!
        Format like this: `<prefix> crab <text>`
        The text you put to show up in the crab rave video should be split into two parts with 2 dashes (--). The first part will appear on top, and the second on the bottom
        __Example usage__: `<prefix> crab first part of text--second part of text`
        """
        if len(text.split("--")) != 2:
            raise commands.BadArgument

        def write_mp4(resp):
            filename = f"crab_rave-{uuid.uuid4()}.mp4"
            with open(filename, "wb") as f:
                f.write(resp)

            return filename

        try:
            with ctx.channel.typing():
                text = text.replace(",", "").replace("--", ",")

                async with self.bot.session.get(
                    f"https://dankmemer.services/api/crab?text={text}",
                    headers=config.DANK_MEMER_AUTH) as w:

                    resp = await w.read()

                filename = await self.bot.loop.run_in_executor(
                    None, functools.partial(write_mp4, resp))

                f = discord.File(filename, filename="crab_rave.mp4")
                await ctx.send(f"**__Crab Rave__: {text.replace(',', ' ')}**\nMade by "
                               f"{ctx.author.mention}", file=f)
        finally:
            try:
                if os.path.isfile(filename):
                    os.remove(filename)
            except:
                pass

    @commands.command(aliases=["zalgo", "zalgofy"],
                      brief="You need to include some text for me to creepify")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def creepify(self, ctx, *, text: str):
        """Turns text into c̛̜̎ṟ͆̃e̲͛̋e͇̭̐p̮̺ͮy̷ͪ͡ ź͉ͯą͗ͪl̬̦̈g̯̪̊ờ͙ ṯ̸̦e͔̎̀x̡͈ͪṫ͟͞
        Note: Due to an issue with Discord, this command won't work very well on large amounts of text. Use [this generator](https://lingojam.com/ZalgoText) if you want to convert a lot of text
        """
        await ctx.channel.trigger_typing()
        creepified = zalgo().zalgofy(text)
        if len(creepified) > 2000:
            await ctx.send("Sorry, but the creepified text has too many characters for me to "
                           "send here. Try again with less text", delete_after=5.0)
            return await delete_message(ctx, 5)
        else:
            await ctx.send(creepified)

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> cry <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def cry(self, ctx, *, text: str):
        """To survive in the wild, you need a reliable source of water
        Format like this: `<prefix> cry <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/cry?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(aliases=["ch", "cyha", "c&h"])
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def cyhap(self, ctx):
        """Posts a random Cyanide & Happiness comic"""

        try:
            with ctx.channel.typing():
                async with self.bot.session.get("http://explosm.net/comics/random") as w:
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

    @commands.command(aliases=["ddlcgen"],
                      brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> ddlc <character> <background> <pose> <face> <text>`"
                      "\nDo `<prefix> help ddlc` for more info on how to use this command.")
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def ddlc(self, ctx, character, background, pose, face, *, text: commands.clean_content(fix_channel_mentions=True, escape_markdown=True)):
        """Generate a DDLC (Doki Doki Literature Club) custom dialogue
        Format like this: `<prefix> ddlc <character> <background> <pose> <face> <text>`
        **Characters**: "sayori", "yuri", "natsuki", OR "monika"
        **Backgrounds**: "bedroom", "class", "closet", "club", "corridor", "house", "kitchen", "residential", OR "sayori_bedroom"
        See the following links to view the **poses** for [Sayori](https://imgur.com/a/qHzyX2w), [Yuri](https://imgur.com/a/tJ72NmL), [Natsuki](https://imgur.com/a/hk2xSfa), and [Monika](https://imgur.com/a/gHE2spo)
        See the following links to view the **faces** for [Sayori](https://imgur.com/a/AD0WjfI), [Yuri](https://imgur.com/a/TtIv3x9), [Natsuki](https://imgur.com/a/Gl6aZSd), and [Monika](https://imgur.com/a/Akc9xtB)
        Text must be less than 140 characters
        """
        characters = ["sayori", "yuri", "natsuki", "monika"]
        backgrounds = ["bedroom", "class", "closet", "club", "corridor", "house", "kitchen",
                       "residential", "sayori_bedroom"]

        monika_faces = [i for i in "abcdefghijklmnopqr"]
        natsuki_faces = [i for i in "abcdefghijklmnopqrstuvwxyz"]
        natsuki_faces.extend(
            ["1t", "2bt", "2bta", "2btb", "2btc", "2btd", "2bte", "2btf", "2btg", "2bth",
             "2bti", "2t", "2ta", "2tb", "2tc", "2td", "2te", "2tf", "2tg", "2th", "2ti"])
        sayori_faces = [i for i in "abcdefghijklmnopqrstuvwxy"]
        yuri_faces = [i for i in "abcdefghijklmnopqrstuvwx"]
        yuri_faces.extend(["y1", "y2", "y3", "y4", "y5", "y6", "y7"])

        ddlc_items = {
            "pose": {
                "monika": [ "1", "2" ],
                "natsuki": [ "1b", "1", "2b", "2"],
                "yuri": ["1b", "1", "2b", "2"],
                "sayori": ["1b", "1", "2b", "2"]
            },
            "face": {
                "monika": monika_faces,
                "natsuki": natsuki_faces,
                "yuri": yuri_faces,
                "sayori": sayori_faces
            }
        }
        reference_links = {
            "pose": {
                "sayori": "https://imgur.com/a/qHzyX2w",
                "yuri": "https://imgur.com/a/tJ72NmL",
                "natsuki": "https://imgur.com/a/hk2xSfa",
                "monika": "https://imgur.com/a/gHE2spo"
            },
            "face": {
                "sayori": "https://imgur.com/a/AD0WjfI",
                "yuri": "https://imgur.com/a/TtIv3x9",
                "natsuki": "https://imgur.com/a/Gl6aZSd",
                "monika": "https://imgur.com/a/Akc9xtB"
            }
        }
        if len(text) >= 140:
            await ctx.send("Text is too long. Must be under 140 characters", delete_after=5.0)
            return await delete_message(ctx, 5)

        character = character.lower()
        if character not in characters:
            await ctx.send(
                "Not a valid character. Must be either `sayori`, `yuri`, `natsuki`, OR `monika`",
                delete_after=7.0)
            return await delete_message(ctx, 7)

        background = background.lower()
        if background not in backgrounds:
            await ctx.send("Not a valid background. Must be either `bedroom`, `class`, `closet`, "
                           "`club`, `corridor`, `house`, `kitchen`, `residential`, OR "
                           "`sayori_bedroom`", delete_after=10.0)
            return await delete_message(ctx, 10)

        pose = pose.lower()
        if not pose in ddlc_items.get("pose").get(character):
            await ctx.send(
                f"Not a valid pose for {character.capitalize()}. See "
                f"{reference_links.get('pose').get(character)} to view her various poses",
                delete_after=15.0)
            return await delete_message(ctx, 15)

        face = face.lower()
        if not face in ddlc_items.get("face").get(character):
            await ctx.send(
                f"Not a valid face for {character.capitalize()}. See "
                f"{reference_links.get('face').get(character)} to view her various faces",
                delete_after=15.0)
            return await delete_message(ctx, 15)

        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=ddlc"
                                        f"&character={character}"
                                        f"&background={background}"
                                        f"&body={pose}"
                                        f"&face={face}"
                                        f"&text={text}") as w:
            resp = await w.json()
        await send_nekobot_image(ctx, resp)

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

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> excuseme <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def excuseme(self, ctx, *, text: str):
        """excuse me what the fuck
        Format like this: `<prefix> excuseme <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(
                f"https://dankmemer.services/api/excuseme?text={text}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command()
    async def f(self, ctx):
        """Pay your respects"""

        msg = await ctx.send(
            f"{ctx.author.mention} has paid their respects :heart:. Press F to pay yours.")
        await msg.add_reaction("\U0001f1eb")

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> facts <text>`", aliases=["fact"])
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def facts(self, ctx, *, text: str):
        """Book of facts
        Format like this: `<prefix> facts <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/facts?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> floor (OPTIONAL)<@mention member> <text>`\nThe text can't "
                      "be longer than 35 characters")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def floor(self, ctx, member: typing.Optional[discord.Member]=None, *, text: str):
        """The floor is...
        Format like this: `<prefix> floor (OPTIONAL)<member> <text>`
        The text can't be longer than 35 characters
        """
        if len(text) > 35:
            await ctx.send(
                f"The text is {len(text)} characters long. It must be under 35 characters",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(
                f"https://dankmemer.services/api/floor?avatar1={img}&text={text}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> gru <3 strings of text>`\n\nYou can only have 3 strings "
                      "of text. No more, no less. They must be separated by a comma and a space\n"
                      "__Example Usage__: `<prefix> gru This, is a, test`", aliases=["plan"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def gru(self, ctx, *, text: str):
        """Create a Gru's plan meme
        Format like this: `<prefix> gru <text>`
        The text must be split into 3 parts for the meme. Do this by putting a comma and a space between them
        __Example Usage__: `<prefix> gru This, is a, test`
        """
        if len(text.split(", ")) != 3:
            raise commands.BadArgument
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/plan?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command()
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def joke(self, ctx):
        """Sends a joke
        Note: For best results, use in a NSFW channel. Then I'll also be able to send NSFW jokes
        """
        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, False, False, "a joke", "jokes")

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> knowyourlocation <2 strings of text>`\n\nThe 2 strings "
                      "must be separated by 2 dashes (--). The first string will be what you "
                      "Google, and the second string will be who wants to know your location\n"
                      "__Example Usage__: `<prefix> knowyourlocation Discord bots that are "
                      "better than MAT--NinjaSnail1080`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def knowyourlocation(self, ctx, *, text: str):
        """They want to know your location
        Format like this: `<prefix> knowyourlocation <2 strings of text>`
        The 2 strings must be separated by 2 dashes (--). The first string will be what you Google, and the second string will be who wants to know your location
        __Example Usage__: `<prefix> knowyourlocation Discord bots that are better than MAT--NinjaSnail1080`
        """
        if len(text.split("--")) != 2:
            raise commands.BadArgument
        with ctx.channel.typing():
            text = text.replace("--", ", ") + " wants to:"
            async with self.bot.session.get(
                f"https://dankmemer.services/api/knowyourlocation?text={text}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> laid (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def laid(self, ctx, member: discord.Member=None):
        """People who get laid
        Format like this: `<prefix> laid (OPTIONAL)<member>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/laid?avatar1={img}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

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
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def meirl(self, ctx):
        """Sends posts that are u irl"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a meme", "me_irl", "meirl")

    @commands.command()
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def meme(self, ctx):
        """Posts a dank meme"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a meme", "dankmemes")

    @commands.command(aliases=["weirdspeak"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def mock(self, ctx, *, stuff: commands.clean_content()=None):
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
            elif i == "x":
                if random.randint(1, 2) == 1:
                    i = "ks"
            if random.randint(1, 2) == 1:
                i = i.upper()
            mock.append(i)

        await ctx.send(content="".join(mock), embed=embed)

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> ohno <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def ohno(self, ctx, *, text: str):
        """Oh no, it's retarded
        Format like this: `<prefix> ohno <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/ohno?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> phcomment (OPTIONAL)<@mention user> <comment>`")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def phcomment(self, ctx, user: typing.Optional[discord.Member]=None, *, comment: str):
        """Generate a PornHub comment!
        Format like this: `<prefix> phcomment (OPTIONAL)<@mention user> <comment>`
        """
        await ctx.channel.trigger_typing()
        if user is None:
            user = ctx.author
        pfp = user.avatar_url_as(format="png")
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=phcomment"
                                        f"&image={pfp}&text={comment}"
                                        f"&username={user.display_name}") as w:
            resp = await w.json()
        await send_nekobot_image(ctx, resp)

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> presentation <text>`")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def presentation(self, ctx, *, text: str):
        """Create a Lisa Simpson presentation meme
        Format like this: `<prefix> presentation <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(
                f"https://dankmemer.services/api/presentation?text={text}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> quote <@mention user> <message text>`\nText can't be "
                      "longer than 56 characters")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def quote(self, ctx, member: discord.Member, *, text: str):
        """Generate a fake Discord message
        Format like this: `<prefix> quote <member> <message text>`
        Text can't be longer than 56 characters
        """
        if len(text) > 56:
            await ctx.send(
                f"The text is {len(text)} characters long. It must be under 56 characters",
                delete_after=6.0)
            return await delete_message(ctx, 6)

        with ctx.channel.typing():
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/quote?avatar1={img}"
                                            f"&username1={member.display_name}&text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You're supposed to include a subreddit for me to get a random post "
                      "from after the command. Like this: `<prefix> reddit <subreddit>`")
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def reddit(self, ctx, sub):
        """Get a random post from any subreddit
        Format like this: `<prefix> reddit <subreddit>`
        Notes: Capitalization doesn't matter when typing the name of the sub
        """
        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 2, 50, False, True, "a post from this sub", sub)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def reverse(self, ctx, *, stuff: commands.clean_content()=None):
        """Reverse the text you give me!"""

        if stuff is None:
            await ctx.send("Dude, you need to give me some text to reverse", delete_after=5.0)
            return await delete_message(ctx, 5)

        else:
            stuff = stuff[::-1]
            await ctx.send(stuff)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> rip (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rip(self, ctx, member: discord.Member=None):
        """***__RIP__***
        Format like this: `<prefix> rip (OPTIONAL)<member>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/rip?avatar1={img}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> roblox (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roblox(self, ctx, member: discord.Member=None):
        """Become a Roblox character
        Format like this: `<prefix> roblox (OPTIONAL)<member>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(
                f"https://dankmemer.services/api/roblox?avatar1={img}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> salty (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def salty(self, ctx, member: discord.Member=None):
        """Are you salty, bro?
        Format like this: `<prefix> salty (OPTIONAL)<member>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/salty?avatar1={img}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp, True)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> satan (OPTIONAL)<@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def satan(self, ctx, member: discord.Member=None):
        """Become Satan
        Format like this: `<prefix> satan (OPTIONAL)<member>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/satan?avatar1={img}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> savehumanity <text>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def savehumanity(self, ctx, *, text: str):
        """I bring the secret to saving humanity!
        Format like this: `<prefix> savehumanity <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(
                f"https://dankmemer.services/api/savehumanity?text={text}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(aliases=["print", "printf", "System.out.println", "echo", "std::cout<<"])
    async def say(self, ctx, *, stuff: commands.clean_content()=None):
        """Make me say something!"""

        if stuff is None:
            await ctx.send("Dude, you need to give me something to say", delete_after=5.0)
            return await delete_message(ctx, 5)

        else:
            await ctx.send(stuff)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> screams (OPTIONAL)<@mention user> (OPTIONAL)<member 2>`\n"
                      "If you don't include member 2, I'll leave it blank", aliases=["normal"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def screams(self, ctx, member: discord.Member=None, member2: discord.Member=None):
        """Why can't you just be normal?
        Format like this: `<prefix> screams (OPTIONAL)<member> (OPTIONAL)<member 2>`
        If you don't include member 2, I'll leave it blank
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")

            if member2 is None:
                img2 = "https://i.imgur.com/4dic8Bn.png"
            else:
                img2 = member2.avatar_url_as(format="png")

            async with self.bot.session.get(
                f"https://dankmemer.services/api/screams?avatar1={img2}&avatar2={img}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(aliases=["showerthoughts"])
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def showerthought(self, ctx):
        """Posts a random showerthought"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, False, False, "a showerthought", "showerthoughts")

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> slap <user getting slapped> (OPTIONAL)<user doing the "
                      "slapping>`\nIf you don't include the second user, I'll use you")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slap(self, ctx, member1: discord.Member, member2: discord.Member=None):
        """Slap another user
        Format like this: `<prefix> slap <user getting slapped> (OPTIONAL)<user doing the slapping>`
        If you don't include the second user, I'll use you
        """
        with ctx.channel.typing():
            if member2 is None:
                member2 = ctx.author
            img1 = member2.avatar_url_as(format="png")
            img2 = member1.avatar_url_as(format="png")
            #* Yes the above switch was intentional
            async with self.bot.session.get(
                f"https://dankmemer.services/api/slap?avatar1={img1}&avatar2={img2}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> spank <user getting spanked> (OPTIONAL)<user doing the "
                      "spanking>`\nIf you don't include the second user, I'll use you")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def spank(self, ctx, member1: discord.Member, member2: discord.Member=None):
        """Spank another user
        Format like this: `<prefix> slap <user getting spanked> (OPTIONAL)<user doing the spanking>`
        If you don't include the second user, I'll use you
        """
        with ctx.channel.typing():
            if member2 is None:
                member2 = ctx.author
            img1 = member2.avatar_url_as(format="png")
            img2 = member1.avatar_url_as(format="png")
            #* Yes the above switch was intentional
            async with self.bot.session.get(
                f"https://dankmemer.services/api/spank?avatar1={img1}&avatar2={img2}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command()
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def thanos(self, ctx):
        """Thanos did nothing wrong"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, True, False, "a thanos meme", "thanosdidnothingwrong")

    @commands.command(brief="You didn't format the command correctly. You're supposed to "
                      "include some text for me to thiccify")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def thiccify(self, ctx, *, text: commands.clean_content()=None):
        """Turns text into 乇乂丅尺卂 丅卄工匚匚 letters"""

        if text is None:
            await ctx.send("You need to include some text for me to thiccify", delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.channel.trigger_typing()
        text = list(text.lower())
        thicc_letters = "卂乃匚刀乇下厶卄工丁长乚从𠘨口尸㔿尺丂丅凵リ山乂丫乙"
        thicc = []

        for i in text:
            try:
                pos = string.ascii_lowercase.index(i)
                i = thicc_letters[pos]
            except:
                if i == " ":
                    i = "  "
            thicc.append(i)

        await ctx.send("".join(thicc))

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> trap <@mention user>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def trap(self, ctx, member: discord.Member):
        """Trap another user with your trapcard!
        Format like this: `<prefix> trap <@mention user>`
        """
        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=trap"
                                        f"&name={member.display_name}"
                                        f"&author={ctx.author.display_name}"
                                        f"&image={member.avatar_url_as(format='png')}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. You're supposed to include "
                      "some text for the tweet `<prefix> trumptweet <tweet>`")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def trumptweet(self, ctx, *, tweet: str):
        """Tweet as Trump!
        Format like this: `<prefix> trumptweet <tweet>`
        """
        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=trumptweet"
                                        f"&text={tweet}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> tweet <twitter usernamer> <tweet>`")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def tweet(self, ctx, user: str, *, tweet: str):
        """Tweet as yourself or another twitter user!
        Format like this: `<prefix> tweet <twitter username> <tweet>`
        """
        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=tweet"
                                        f"&username={user}&text={tweet}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> unpopular (OPTIONAL)<@mention user> <text for opinion>`\n"
                      "If you don't put a member, I'll just use you")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def unpopular(self, ctx, member: typing.Optional[discord.Member]=None, *, text: str):
        """Do you have an unpopular opinion?
        Format like this: `<prefix> unpopular (OPTIONAL)<member> <opinion>`
        If you don't put a member, I'll just use you
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(
                f"https://dankmemer.services/api/unpopular?avatar1={img}&text={text}",
                headers=config.DANK_MEMER_AUTH) as w:

                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def upsidedown(self, ctx, *, text: commands.clean_content()=None):
        """Turn text ¡uʍop ǝpᴉsdn"""

        if text is None:
            await ctx.send(
                "You need to include some text for me to turn upside down", delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.channel.trigger_typing()
        characters = (string.ascii_letters + string.digits + string.punctuation).replace("\"", "")
        udcharacters = ("ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz∀qƆpƎℲפHIſʞ˥WNOԀQɹS┴∩ΛMX⅄Z0ƖᄅƐㄣϛ9ㄥ86¡#$%⅋,)("
                        "*+'-˙/:;>=<¿@]\\[^‾,}|{~")
        upside_down = []

        for i in text:
            try:
                pos = characters.index(i)
                i = udcharacters[pos]
            except:
                if i == "\"":
                    i = ",,"
            upside_down.append(i)

        await ctx.send("".join(upside_down[::-1]))

    @commands.command(brief="You need to include some text after the command, like this: "
                      "`<prefix> walking <text>`", aliases=["dancing", "theresa"])
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def walking(self, ctx, *, text: str):
        """Create a "Theresa May awkwardly walking/dancing onstage" meme
        Format like this: `<prefix> walking <text>`
        """
        with ctx.channel.typing():
            async with self.bot.session.get(f"https://dankmemer.services/api/walking?text={text}",
                                            headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> whowouldwin <@mention user1> (OPTIONAL)<@mention user2>`")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def whowouldwin(self, ctx, user1: discord.Member, user2: discord.Member=None):
        """Who would win?
        Format like this: `<prefix> whowouldwin <@mention user 1> (OPTIONAL)<@mention user 2>`
        """
        await ctx.channel.trigger_typing()
        if user2 is None:
            user2 = ctx.author
        img1 = user1.avatar_url_as(format="png")
        img2 = user2.avatar_url_as(format="png")
        async with self.bot.session.get("https://nekobot.xyz/api/imagegen?type=whowouldwin"
                                        f"&user1={img1}&user2={img2}") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(aliases=["wc", "tagcloud"])
    @has_voted()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def wordcloud(self, ctx, users: commands.Greedy[discord.Member], channel: typing.Optional[discord.TextChannel]=None, limit: typing.Optional[int]=2000):
        """Generate a word cloud, which is an image that shows the frequencies of various words from messages sent in a channel
        Format like this: `<prefix> wordcloud (OPTIONAL)<@mention user(s)> (OPTIONAL)<channel> (OPTIONAL)<# of msgs to process>`
        If you mention any users, I'll only process their messages. If you don't, I'll process all messages.
        If you leave out the # of msgs to process, I'll default to 2000.
        If you don't mention a channel, I'll use the one the command was performed in
        """
        def create_wc(text):
            WC = wc.WordCloud(width=800, height=500)
            WC.generate(text)
            filepath = f"wc-{uuid.uuid4()}.png"
            WC.to_file(filepath)
            return filepath

        if limit > 10000:
            await ctx.send("The number of messages to process must be **no more than 10000**",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        if channel is None:
            channel = ctx.channel

        temp = await ctx.send("Processing... Please wait...")
        try:
            with ctx.channel.typing():
                if not users:
                    messages = [m.clean_content for m in await channel.history(
                        limit=limit).flatten()]
                    content = ("A word cloud showing the frequencies of various words from "
                               f"messages sent in {channel.mention}. Bigger words are more "
                               "frequent, smaller words are less")
                else:
                    messages = [m.clean_content for m in await channel.history(
                        limit=limit).flatten() if m.author in users]
                    content = ("A word cloud showing the frequencies of various words from "
                               f"messages sent in {channel.mention} by "
                               f"{', '.join(u.mention for u in users)}. Bigger words are more "
                               "frequent, smaller words are less")

            if len(messages) == 0:
                await temp.delete()
                await ctx.send("I was unable to process enough messages in that channel to make "
                               "a word cloud", delete_after=7.0)
                return await delete_message(ctx, 7)

            with ctx.channel.typing():
                await temp.edit(content="Making wordcloud...")
                filepath = await self.bot.loop.run_in_executor(
                    None, functools.partial(create_wc, ".\n".join(messages)))

                f = discord.File(filepath, filename="wc.png")
                embed = discord.Embed(color=find_color(ctx))
                embed.set_image(url="attachment://wc.png")
                embed.set_footer(text=f"Messages processed: {len(messages)}")

            await temp.delete()
            await ctx.send(content, file=f, embed=embed)
        except discord.Forbidden:
            await temp.delete()
            await ctx.send(
                f"I don't have permission to view the message history of {channel.mention}",
                delete_after=5.0)
            await delete_message(ctx, 5)
        finally:
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            except:
                pass

    @commands.command()
    @commands.cooldown(3, 9, commands.BucketType.user)
    async def xkcd(self, ctx):
        """Posts a random xkcd comic"""
        try:
            with ctx.channel.typing():
                async with self.bot.session.get("https://c.xkcd.com/random/comic/") as w:
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

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                      "this: `<prefix> youtube (OPTIONAL)<@mention user> <text for comment>`\n"
                      "If you don't put a member, I'll just use you", aliases=["ytcomment"])
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def youtube(self, ctx, member: typing.Optional[discord.Member]=None, *, text: str):
        """Generate a Youtube comment!
        Format like this: `<prefix> youtube (OPTIONAL)<@mention user> <comment>`
        """
        with ctx.channel.typing():
            if member is None:
                member = ctx.author
            img = member.avatar_url_as(format="png")
            async with self.bot.session.get(f"https://dankmemer.services/api/youtube?"
                                            f"avatar1={img}&username1={member.display_name}"
                                            f"&text={text}", headers=config.DANK_MEMER_AUTH) as w:
                resp = await w.read()
                await send_dank_memer_img(ctx, resp)


def setup(bot):
    bot.add_cog(Fun(bot))
