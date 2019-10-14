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

from discord.ext import commands
import discord

import random
import datetime
import re


class Listeners(commands.Cog):
    """Miscellaneous bot listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.joins_and_leaves = self.bot.get_channel(465393762512797696)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channels = [t for t in guild.text_channels if t.permissions_for(guild.me).send_messages]

        for c in channels:
            if re.search("off-topic", c.name) or re.search("chat", c.name) or re.search(
                "general", c.name) or re.search("bot", c.name):

                msg_channel = c
                await msg_channel.send(
                    embed=discord.Embed(description=self.bot.join_new_guild_message,
                                        color=discord.Color.blurple()))
                break
        else:
            #* If it didn't find a channel to send in
            msg_channel = random.choice(channels)
            await msg_channel.send(
                content="~~Damn, you guys must have a really strange system for naming your "
                "channels~~",
                embed=discord.Embed(
                    description=self.bot.join_new_guild_message, color=discord.Color.blurple()))

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO guilddata
                (id)
                VALUES ({})
                ON CONFLICT (id)
                    DO NOTHING
            ;""".format(guild.id))

            await conn.execute("""
                UPDATE guilddata
                SET musicsettings = $1::JSON
                WHERE musicsettings IS NULL
            ;""", self.bot.default_musicsettings)

            await conn.execute("""
                INSERT INTO userdata
                (id)
                VALUES {}
                ON CONFLICT (id)
                    DO NOTHING
            ;""".format(", ".join([f"({m.id})" for m in guild.members if not m.bot])))

            new_guild_query = await conn.fetch(f"SELECT * FROM guilddata WHERE id = {guild.id};")
            user_query = await conn.fetch("SELECT * FROM userdata;")

        self.bot.guilddata.update({new_guild_query[0].get("id"): dict(new_guild_query[0])})
        for i in user_query:
            if i.get("id") not in self.bot.userdata:
                self.bot.userdata.update({i.get("id"): dict(i)})

        bots = [m for m in guild.members if m.bot]
        try:
            invite_url = (await msg_channel.create_invite()).url
            invite = f"\n[Invite]({invite_url})"
        except discord.Forbidden:
            invite = ""

        embed = discord.Embed(
            title=f"Joined {guild.name}", description=f"**ID**: {guild.id}\n**Joined**: "
            f"{guild.me.joined_at.strftime('%b %-d, %Y at %X UTC')}{invite}",
            color=self.joins_and_leaves.guild.me.color)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Text Channels", value=len(guild.text_channels))
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels))
        embed.add_field(name="Categories", value=len(guild.categories))
        embed.add_field(
            name="Custom Emojis", value=f"{len(guild.emojis)} out of {guild.emoji_limit}")
        embed.add_field(name="Bots", value=len(bots))
        try:
            if await guild.webhooks():
                embed.add_field(name="Webhooks", value=len(await guild.webhooks()))
            else:
                embed.add_field(name="Webhooks", value="None")
        except:
            embed.add_field(name="Webhooks", value="Unknown")
        if guild.premium_tier:
            embed.add_field(name="Nitro Server Boost Status", value=f"Level {guild.premium_tier}")
        else:
            embed.add_field(name="Nitro Server Boost Status", value="No Levels Achieved")
        if guild.premium_subscription_count:
            embed.add_field(name="Nitro Server Boosts", value=guild.premium_subscription_count)
        else:
            embed.add_field(name="Nitro Server Boosts", value="None")
        if guild.mfa_level:
            embed.add_field(name="Requires 2FA?", value="Yes")
        else:
            embed.add_field(name="Requires 2FA?", value="No")
        embed.add_field(name="Region", value=str(guild.region).replace(
            "-", " ").replace("south", "south ").replace("hong", "hong ").title().replace(
                "Us", "U.S.").replace("Vip", "V.I.P."))
        embed.add_field(name="Default Notification Level",
                        value=str(guild.default_notifications)[18:].replace("_", " ").title())
        embed.add_field(
            name="Verification Level", value=str(guild.verification_level).capitalize())
        embed.add_field(name="Explicit Content Filter",
                        value=str(guild.explicit_content_filter).replace("_", " ").title())
        embed.add_field(
            name="Server Created", value=guild.created_at.strftime("%b %-d, %Y"))
        if guild.features:
            embed.add_field(
                name="Server Features",
                value="`" + "`, `".join([f.replace("_", " ") for f in guild.features]) + "`",
                inline=False)
        embed.add_field(
            name="Server Owner", value=str(guild.owner) + f" (User ID: {(guild.owner_id)})",
            inline=False)

        await self.joins_and_leaves.send(
            content=f"I am now part of {len(self.bot.guilds)} servers and have "
                    f"{len(self.bot.users)} unique users!",
            embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = discord.Embed(
            title=f"Left {guild.name}", description=f"**ID**: {guild.id}\n**Left**: "
            f"{datetime.datetime.utcnow().strftime('%b %-d, %Y at %X UTC')}",
            color=self.joins_and_leaves.guild.me.color)
        embed.set_thumbnail(url=guild.icon_url)

        await self.joins_and_leaves.send(
            content=f"I am now part of {len(self.bot.guilds)} servers and have "
                    f"{len(self.bot.users)} unique users",
            embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot or member.id in self.bot.userdata:
            return

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO userdata
                (id)
                VALUES ({})
                ON CONFLICT (id)
                    DO NOTHING
            ;""".format(member.id))

            new_user_query = await conn.fetch(f"SELECT * FROM userdata WHERE id = {member.id};")

        self.bot.userdata.update({new_user_query[0].get("id"): dict(new_user_query[0])})


def setup(bot):
    bot.add_cog(Listeners(bot))
