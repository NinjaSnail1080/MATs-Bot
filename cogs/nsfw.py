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

from utils import find_color, delete_message, get_reddit, send_nekobot_image, has_voted, ChannelNotNSFW

from discord.ext import commands
import discord
import rapidjson as json

import random

#* MAT's Bot uses the NekoBot API for many of these commands.
#* More info at https://docs.nekobot.xyz/


class NSFW(commands.Cog):
    """NSFW commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.guild is not None:
            if not ctx.channel.is_nsfw() and ctx.command.name != "neko": #* See "neko" command
                raise ChannelNotNSFW
        return True

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def anal(self, ctx):
        """Sends gifs of anal sex"""

        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/image?type=anal") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def artsy(self, ctx):
        """Posts some artsy porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "SexyButNotPorn", "LaBeauteFeminine", "BacklitBeauty", "nsfw_bw")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def asian(self, ctx):
        """Posts pics of hot asians"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "AsianHotties", "Sexy_Asians", "asianbabes", "bustyasians",
                                "juicyasians", "AsianNSFW")

    @commands.command(aliases=["butt", "butts", "booty"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def ass(self, ctx):
        """Posts some ass"""

        try:
            with ctx.channel.typing():
                async with self.bot.session.get(
                    f"http://api.obutts.ru/butts/get/{random.randint(7, 5999)}") as w:

                    resp = await w.json()
                try:
                    resp = resp[0]
                except: pass

                url = "http://media.obutts.ru/" + resp["preview"]
                if resp["model"] is None or resp["model"] == "":
                    model = ""
                else:
                    model = "**Model**: " + resp["model"]

                embed = discord.Embed(color=find_color(ctx), description=model)
                embed.set_image(url=url)
                embed.set_footer(text=f"ass | {ctx.author.display_name}")

                await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def bdsm(self, ctx):
        """Posts some bdsm or bondage porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post", "bdsm", "bondage")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def bigboobs(self, ctx):
        """Big Boobs"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post", "bigboobs", "BigBoobsGW")

    @commands.command(aliases=["tits"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def boobs(self, ctx):
        """Posts some boobs"""

        try:
            with ctx.channel.typing():
                async with self.bot.session.get(
                    f"http://api.oboobs.ru/boobs/get/{random.randint(8, 13013)}") as w:

                    resp = await w.json()
                try:
                    resp = resp[0]
                except: pass

                url = "http://media.oboobs.ru/" + resp["preview"]
                if resp["model"] is None or resp["model"] == "":
                    model = ""
                else:
                    model = "**Model**: " + resp["model"]

                embed = discord.Embed(color=find_color(ctx), description=model)
                embed.set_image(url=url)
                embed.set_footer(text=f"boobs | {ctx.author.display_name}")

                await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command(aliases=["collar"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def collared(self, ctx):
        """Sends pics of girls in collars"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, True, False, "a post", "collared")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def cosplay(self, ctx):
        """Posts some sexy cosplay"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "cosplaygirls", "cosplayonoff", "FictionalBabes", "NSFWCostumes")

    @commands.command()
    @has_voted()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """Sends some pics of cumsluts"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 75, True, False, "a post",
                                "cumsluts", "cumfetish", "before_after_cumsluts", "FacialFun")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def cute(self, ctx):
        """Posts some cute nude girls"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "adorableporn", "TooCuteForPorn", "legalteens", "18_19")

    @commands.command(aliases=["dickpic", "penis", "cock"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def dick(self, ctx):
        """Sends a dick pic"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 200, True, False, "a post",
                                "PenisPics", "penis", "ratemycock", "MassiveCock", "Cock")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def ecchi(self, ctx):
        """Posts some ecchi (basically softcore hentai)"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post", "ecchi")

    @commands.command(name="4k", aliases=["fourk", "hdporn"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def fourk(self, ctx):
        """Sends some 4k/UHD porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(
            ctx, 1, 100, True, False, "a post", "NSFW_Wallpapers", "HighResNSFW", "UHDnsfw")

    @commands.command(aliases=["futanari"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def futa(self, ctx):
        """Posts some futanari"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, True, False, "a post", "futanari")

    @commands.command(aliases=["gayporn"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def gayp(self, ctx):
        """Posts some gay porn"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, True, False, "a post", "gayporn")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def gonewild(self, ctx):
        """Sends a random post from either r/gonewild, r/gonewildcurvy, r/GoneWildSmiles, r/PetiteGoneWild, or r/RealGirls"""

        await ctx.channel.trigger_typing()
        return await get_reddit(
            ctx, 2, 200, True, True, "a post",
            "gonewild", "gonewildcurvy", "GoneWildSmiles", "PetiteGoneWild", "RealGirls")

    @commands.command()
    @has_voted()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def hentai(self, ctx, arg: str=None):
        """Posts some hentai. Add `-gif` after the command for a hentai gif OR add `-irl` for a hentai_irl post. Add nothing extra for a regular hentai pic"""

        await ctx.channel.trigger_typing()
        if arg is None:
            return await get_reddit(ctx, 1, 100, True, False, "a post", "hentai")

        elif arg == "-gif":
            async with self.bot.session.get(
                "https://nekobot.xyz/api/image?type=hentai_anal") as w:

                resp = await w.json()
            return await send_nekobot_image(ctx, resp)

        elif arg == "-irl":
            return await get_reddit(ctx, 1, 75, True, False, "a post", "hentai_irl")

        else:
            await ctx.send("Invalid formatting. You can only add `-gif` after the command for a "
                           "hentai gif OR `-irl` for a hentai_irl post. You can add nothing "
                           "extra for regular hentai", delete_after=10.0)
            return await delete_message(ctx, 10)

    @commands.command(aliases=["lesbians"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def lesbian(self, ctx):
        """Sends pics of lesbians"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 75, True, False, "a post", "lesbians")

    @commands.command(aliases=["stockings", "panties"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def lingerie(self, ctx):
        """Posts pics of hot girls in lingerie"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "lingerie", "stockings", "pantyfetish", "panties")

    @commands.command(aliases=["nekos"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def neko(self, ctx):
        """Posts some lewd nekos if used in an NSFW channel, or nonlewd nekos if used in a regular channel."""

        await ctx.channel.trigger_typing()
        if ctx.channel.is_nsfw():
            url = "https://nekos.life/api/lewd/neko"
        else:
            url = "https://nekos.life/api/neko"

        try:
            async with self.bot.session.get(url) as w:
                resp = await w.json()

            embed = discord.Embed(color=find_color(ctx))
            embed.set_image(url=resp["neko"])
            embed.set_footer(text=f"neko | {ctx.author.display_name}")

            await ctx.send(embed=embed)
        except:
            await ctx.send("Huh, something went wrong. I wasn't able to get the image. Try "
                           "again later", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def oldschool(self, ctx):
        """Posts some old-school NSFW pics"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, True, False, "a post", "OldSchoolCoolNSFW")

    @commands.command(aliases=["porngif"])
    @has_voted()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def pgif(self, ctx):
        """Posts a porn gif"""

        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/image?type=pgif") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(aliases=["vagina"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def pussy(self, ctx):
        """Posts some pussy"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 100, True, False, "a post",
                                "pussy", "rearpussy", "simps", "spreading", "landingstrip")

    @commands.command(aliases=["redhead", "redheads"])
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def red(self, ctx):
        """Hot redheads!"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 75, True, False, "a post", "lesbians")

    @commands.command()
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def rule34(self, ctx, *, tag: str=None):
        """Posts some Rule 34
        Format like this: `<prefix> rule34 (OPTIONAL)<tag>`
        If you don't include a specific tag to search for, I'll just send a random rule 34 pic
        """
        await ctx.channel.trigger_typing()
        if tag is None:
            return await get_reddit(ctx, 1, 100, True, False, "a post", "rule34")
        else:
            tag = tag.lower().replace(" ", "_")
            try:
                async with self.bot.session.get("https://rule34.xxx/index.php?page=dapi&s=post&q="
                                                f"index&json=1&tags={tag}") as w:
                    resp = json.loads(await w.text())

                for p in resp.copy():
                    if "loli" in p["tags"] or "shota" in p["tags"]:
                        resp.remove(p)
                data = random.choice(resp)

                embed = discord.Embed(
                    title=tag,
                    description=f"By [{data['owner']}](https://rule34.xxx/index.php?page=account"
                                f"&s=profile&uname={data['owner']})",
                    color=find_color(ctx))
                embed.set_image(
                    url=f"https://img.rule34.xxx/images/{data['directory']}/{data['image']}")
                embed.set_footer(text=f"rule34 | {ctx.author.display_name}")

                await ctx.send(embed=embed)

            except (json.JSONDecodeError, IndexError):
                await ctx.send(f"No images were found for the `{tag}` tag", delete_after=5.0)
                return await delete_message(ctx, 5)

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def thighs(self, ctx):
        """Sends some thiccccccccc thighs"""

        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://nekobot.xyz/api/image?type=thigh") as w:
            resp = await w.json()
            await send_nekobot_image(ctx, resp)

    @commands.command(brief="You need to include a tag to search with")
    @commands.cooldown(2, 6, commands.BucketType.user)
    async def yandere(self, ctx, *, tag: str):
        """Searches yande.re for a tag
        Format like this: `<prefix> yandere <tag>`
        """
        await ctx.channel.trigger_typing()
        async with self.bot.session.get(f"https://yande.re/post.json?limit=100&tags={tag}") as w:
            resp = await w.json()

        if resp:
            for p in resp.copy():
                if "loli" in p["tags"] or "shota" in p["tags"]:
                    resp.remove(p)
            try:
                data = random.choice(resp)
            except IndexError:
                await ctx.send(f"No posts were found for the `{tag}` tag", delete_after=5.0)
                return await delete_message(ctx, 5)

            embed = discord.Embed(
                title=f"#{data['id']} | " + data["tags"],
                description=f"By [{data['author']}](https://yande.re/user/show/"
                            f"{data['creator_id']})",
                url=f"https://yande.re/post/show/{data['id']}",
                color=find_color(ctx))
            embed.set_image(url=data["jpeg_url"])
            embed.set_footer(text=f"yandere | {ctx.author.display_name}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No posts were found for the `{tag}` tag", delete_after=5.0)
            return await delete_message(ctx, 5)

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def yaoi(self, ctx):
        """Posts some yaoi (gay hentai)"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 25, True, False, "a post", "yaoi")

    @commands.command()
    @commands.cooldown(4, 9, commands.BucketType.user)
    async def yuri(self, ctx):
        """Posts some yuri (lesbian hentai)"""

        await ctx.channel.trigger_typing()
        return await get_reddit(ctx, 1, 50, True, False, "a post", "yuri")


def setup(bot):
    bot.add_cog(NSFW(bot))
