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

from utils import delete_message

from discord.ext import commands, tasks
import discord
import asyncpg
import rapidjson as json

import collections
import random
import asyncio

import config


class Database(commands.Cog, command_attrs={"hidden": True}):
    """Database handling for the bot"""

    def __init__(self, bot):
        self.bot = bot

        self.bot.pool = self.bot.loop.run_until_complete(self.init_postgres())
        self.bot.default_musicsettings = {
            "max_size": 0,
            "dj_role": None,
            "strict": False
        }

        self.update_db_msg_cmd_count.start()

    def cog_unload(self):
        self.update_db_msg_cmd_count.cancel()
        self.bot.ready_for_commands = False
        self.bot.loop.run_until_complete(
            self.bot.change_presence(status=discord.Status.invisible))

    async def cog_check(self, ctx):
        if not await self.bot.is_owner(ctx.author):
            raise commands.NotOwner
        return True

    async def init_postgres(self):
        """Initialize connection to postgres"""

        async def init_connection(conn):
            await conn.set_type_codec("json", encoder=json.dumps, decoder=json.loads,
                                      schema="pg_catalog")

        pool = await asyncpg.create_pool(config.POSTGRES, init=init_connection)
        return pool

    async def init_data(self, pool):
        """Initialize tables in postgres database and get data"""

        async with pool.acquire() as conn:

            #* Create botdata table if it doesn't already exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS botdata (
                    messages_read JSON,
                    commands_used JSON,
                    giveaways JSON[] NOT NULL DEFAULT '{}',
                    reminders JSON[] NOT NULL DEFAULT '{}'
                )
            ;""")

            #* Create guilddata table if it doesn't already exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS guilddata (
                    id BIGINT PRIMARY KEY,
                    prefixes TEXT[] NOT NULL DEFAULT '{}',
                    logs BIGINT,
                    commands_used JSON,
                    disabled TEXT[] NOT NULL DEFAULT '{}',
                    custom_roles BIGINT[] NOT NULL DEFAULT '{}',
                    mute_role BIGINT,
                    autorole BIGINT,
                    starboard JSON,
                    welcome JSON,
                    goodbye JSON,
                    last_delete JSON,
                    musicsettings JSON,
                    tags JSON NOT NULL DEFAULT '{}'
                )
            ;""")

            #* Create userdata table if it doesn't already exist
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS userdata (
                    id BIGINT PRIMARY KEY,
                    commands_used JSON,
                    us_units BOOLEAN NOT NULL DEFAULT FALSE
                )
            ;""")

            #* Insert row into botdata only if the table is empty
            await conn.execute("""
                INSERT INTO botdata
                (messages_read, commands_used)
                SELECT NULL, NULL
                WHERE NOT EXISTS (SELECT * FROM botdata)
            ;""")

            #* Add all guild ids to guilddata if they aren't already there
            await conn.execute("""
                INSERT INTO guilddata
                (id)
                VALUES {}
                ON CONFLICT (id)
                    DO NOTHING
            ;""".format(", ".join([f"({g.id})" for g in self.bot.guilds])))

            #* Update musicsettings to the default ones if they're NULL
            await conn.execute("""
                UPDATE guilddata
                SET musicsettings = $1::JSON
                WHERE musicsettings IS NULL
            ;""", self.bot.default_musicsettings)

            #* Add all user ids to userdata if they aren't already there
            await conn.execute("""
                INSERT INTO userdata
                (id)
                VALUES {}
                ON CONFLICT (id)
                    DO NOTHING
            ;""".format(", ".join([f"({u.id})" for u in self.bot.users if not u.bot])))

            bot_query = await conn.fetch("SELECT * FROM botdata;")
            guild_query = await conn.fetch("SELECT * FROM guilddata;")
            user_query = await conn.fetch("SELECT * FROM userdata;")

        self.bot.botdata = dict(bot_query[0])

        self.bot.guilddata = {}
        for i in guild_query:
            self.bot.guilddata.update({i.get("id"): dict(i)})

        self.bot.userdata = {}
        for i in user_query:
            self.bot.userdata.update({i.get("id"): dict(i)})

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init_data(self.bot.pool)
        self.bot.commands_used = collections.Counter(self.bot.botdata["commands_used"])
        self.bot.messages_read = collections.Counter(self.bot.botdata["messages_read"])
        self.bot.ready_for_commands = True

    @tasks.loop(minutes=30)
    async def update_db_msg_cmd_count(self):
        """Update the db with message and command counts"""

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE botdata
                SET messages_read = $1::JSON,
                    commands_used = $2::JSON
            ;""", self.bot.botdata["messages_read"], self.bot.botdata["commands_used"])

            for data in self.bot.guilddata.copy().values():
                await conn.execute("""
                    UPDATE guilddata
                    SET commands_used = $1::JSON
                    WHERE id = {}
                ;""".format(data["id"]), data["commands_used"])

            for data in self.bot.userdata.copy().values():
                await conn.execute("""
                    UPDATE userdata
                    SET commands_used = $1::JSON
                    WHERE id = {}
                ;""".format(data["id"]), data["commands_used"])

    @update_db_msg_cmd_count.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(30) #* To ensure that the database is fully set up before it starts

    @commands.command()
    async def reloadpg(self, ctx):
        """Reinitialize connection to postgres"""

        self.bot.pool = await self.init_postgres()
        await ctx.send("Reinitialized connection to PostgreSQL", delete_after=5.0)
        return await delete_message(ctx, 5)

    @commands.command()
    async def reloaddata(self, ctx):
        """Reinitialize tables in postgres database"""

        await self.init_data(self.bot.pool)
        await ctx.send("Reinitialized tables in PostgreSQL database", delete_after=5.0)
        return await delete_message(ctx, 5)


def setup(bot):
    bot.add_cog(Database(bot))
