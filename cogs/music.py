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

from utils import find_color, delete_message, has_voted, parse_duration, chunks, send_basic_paginator, send_advanced_paginator, MusicCheckFailure

from discord.ext import commands, tasks
import discord
import async_timeout
import youtube_dl
import validators
import lyricsgenius

import asyncio
import functools
import random
import datetime
import time
import typing
import collections

import config

ytdl_options = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": False,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0"
}

default_ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


class YTDLSource(discord.PCMVolumeTransformer):
    """Creates audio sources with a PCMVolumeTransformer using youtube_dl"""

    def __init__(self, source, data):
        super().__init__(source)
        self.data = data

    @classmethod
    async def create_source(cls, ctx, search: str, seek: int=None, gain: int=None, as_list: bool=True):
        """Extracts info from a video and returns it as a dict"""

        data = await ctx.bot.loop.run_in_executor(None, functools.partial(
            ctx.bot.ytdl.extract_info,
            url=search,
            download=False,
            extra_info={"requester": ctx.author, "seek": seek, "gain": gain}))

        if "entries" in data:
            if len(data["entries"]) == 1:
                data = data["entries"][0]
                data.update({"requester": ctx.author, "seek": seek, "gain": gain})
            else:
                list_data = []
                for d in data["entries"]:
                    d.update({"requester": ctx.author, "seek": seek, "gain": gain})
                    list_data.append(d)
                return list_data

        if as_list:
            return [data]
        else:
            return data

    @classmethod
    async def regather_stream(cls, bot, data):
        """Prepares a stream since YouTube streaming links expire"""

        data = await bot.loop.run_in_executor(None, functools.partial(
            bot.ytdl.extract_info,
            url=data["webpage_url"],
            download=False,
            extra_info={"requester": data["requester"],
                        "seek": data["seek"],
                        "gain": data["gain"]}))

        ffmpeg_options = default_ffmpeg_options.copy()
        if data["seek"]:
            ffmpeg_options["before_options"] += " -ss " + parse_duration(data["seek"])
        if data["gain"]:
            ffmpeg_options["options"] += " -af bass=g=" + data["gain"]

        return cls(discord.FFmpegPCMAudio(data["url"], **ffmpeg_options), data)


class Player():
    """A class assigned to each guild that's playing music. Destroyed when the bot disconnects"""

    def __init__(self, ctx):
        self.bot = ctx.bot
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.queue = asyncio.Queue(loop=self.bot.loop)
        self.next = asyncio.Event(loop=self.bot.loop)

        self.np_msg = None
        self.np_invoker = None
        self.volume = 0.5
        self.looping = False
        self.queue_looping = False
        self.timestamp = None
        self.time_paused = 0
        self.current = None

        self.playing = True
        self.player_task = self.bot.loop.create_task(self.player_loop())

        self.paused = False
        self.paused_task = self.bot.loop.create_task(self.update_time_paused())

    async def player_loop(self):
        await self.bot.wait_until_ready()
        while self.playing:
            self.next.clear()

            try:
                async with async_timeout.timeout(300): #* 5 minutes without playing something
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return await self.channel.guild.voice_client.disconnect()

            if self.queue_looping:
                source["seek"] = None
                self.queue.put_nowait(source)

            try:
                source = await YTDLSource.regather_stream(self.bot, source)
            except asyncio.CancelledError:
                return
            except Exception as e:
                if e:
                    await self.channel.send(f"```{e}```An unknown error occured while processing "
                                            f"**{source['title']}**")
                continue

            source.volume = self.volume
            self.current = source

            self.channel.guild.voice_client.play(
                source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            self.timestamp = time.time()
            if self.current.data["seek"]:
                self.timestamp -= self.current.data["seek"]

            self.np_msg = await self.cog.create_np_msg(self.channel, self)

            await self.next.wait()

            if self.looping:
                self.current.data["seek"] = None
                self.queue._queue.appendleft(self.current.data)

            source.cleanup()
            self.current = None
            self.paused = False
            self.time_paused = 0
            try:
                await self.np_msg.delete()
            except (AttributeError, discord.HTTPException):
                pass
            try:
                await self.np_invoker.delete()
            except (AttributeError, discord.HTTPException):
                pass

    async def update_time_paused(self):
        await self.bot.wait_until_ready()
        while self.playing:
            if self.paused:
                self.time_paused += 1
            await asyncio.sleep(1)


def check_voice():
    """Checks if the user and bot are in the same voice channel"""

    async def predicate(ctx):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.author.voice.channel == ctx.voice_client.channel:
                    return True
            await ctx.send("You're not in my voice channel. Join \U0001f509"
                           f"{ctx.voice_client.channel.name}, then call this command",
                           delete_after=6.0)
            await delete_message(ctx, 6)
        else:
            await ctx.send("I'm not currently playing anything. Use the `play` command for "
                           "me to play a song in a voice channel",
                           delete_after=7.0)
            await delete_message(ctx, 7)
        raise MusicCheckFailure

    return commands.check(predicate)


def is_dj(requester_allowed=False, strict_perm=False):
    """Checks if the user has the Manage Messages perm OR the DJ role if it exists. If requester_allowed is True, it'll also check if the user requested the current song. If strict_perm is True, it'll check for the Strict Perms setting"""

    async def predicate(ctx):
        dj_role = ctx.bot.guilddata[ctx.guild.id]["musicsettings"]["dj_role"]

        if strict_perm:
            if not ctx.bot.guilddata[ctx.guild.id]["musicsettings"]["strict"]:
                return True

        if requester_allowed:
            player = ctx.cog.get_player(ctx)
            if player.current:
                if player.current.data["requester"] == ctx.author:
                    return True
        if ctx.author.guild_permissions.manage_messages:
            return True
        elif dj_role:
            if ctx.guild.get_role(dj_role) in ctx.author.roles:
                return True

        if dj_role:
            await ctx.send(
                "You must have the **Manage Messages** perm or the "
                f"`{ctx.guild.get_role(dj_role).name}` role in order to use this command",
                delete_after=8.0)
            await delete_message(ctx, 8)
        else:
            await ctx.send(
                f"You must have the **Manage Messages** perm in order to use this command",
                delete_after=6.0)
            await delete_message(ctx, 6)
        raise MusicCheckFailure

    return commands.check(predicate)


def check_queue(empty=False, current=False):
    """Checks if the queue is empty OR if there's a current song playing"""

    async def predicate(ctx):
        player = ctx.cog.get_player(ctx)

        if empty:
            if player.queue.empty():
                await ctx.send(
                    "There are no songs in the queue. Use the `play` command to add some",
                    delete_after=6.0)
                await delete_message(ctx, 6)
                raise MusicCheckFailure
        elif current:
            if not player.current:
                await ctx.send("I'm not currently playing anything. Use the `play` command for "
                               "me to play a song", delete_after=7.0)
                return await delete_message(ctx, 7)
        return True

    return commands.check(predicate)


class Music(commands.Cog):
    """Music/Audio commands"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.ytdl = youtube_dl.YoutubeDL(ytdl_options)
        self.players = {}

    def cog_unload(self):
        for p in self.players.values():
            p.playing = False
            p.player_task.cancel()
            p.paused_task.cancel()

        self.players.clear()

        for v in self.bot.voice_clients:
            self.bot.loop.run_until_complete(v.disconnect())

    async def cog_check(self, ctx):
        if ctx.guild is None and ctx.command.name != "lyrics":
            raise commands.NoPrivateMessage
        return True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user:
            if after.channel is None:
                await self.cleanup(member.guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if role.id == self.bot.guilddata[role.guild.id]["musicsettings"]["dj_role"]:
            self.bot.guilddata[role.guild.id]["musicsettings"]["dj_role"] = None
            async with self.bot.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE guilddata
                    SET musicsettings = $1::JSON
                    WHERE id = {}
                ;""".format(role.guild.id), self.bot.guilddata[role.guild.id]["musicsettings"])

    def get_player(self, ctx):
        """Returns the guild's instance of Player, or creates a new one if it doesn't exist"""

        if ctx.guild.id in self.players:
            player = self.players[ctx.guild.id]
        else:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def cleanup(self, guild):
        """Disconnects from voice and destroys the guild's instance of Player"""

        try:
            try:
                await self.players[guild.id].np_msg.delete()
            except:
                pass
            try:
                await self.players[guild.id].np_invoker.delete()
            except:
                pass

            self.players[guild.id].queue._queue.clear()
            self.players[guild.id].playing = False
            self.players[guild.id].player_task.cancel()
            self.players[guild.id].paused_task.cancel()
            self.players.pop(guild.id)
        except KeyError:
            pass

    async def create_np_msg(self, channel, player):
        """Creates a "Now Playing" message"""

        data = player.current.data.copy()
        for k, v in data.items():
            if v is None:
                data[k] = 0

        current_time = round(time.time() - player.timestamp - player.time_paused)
        description = (f"**Requested by {data['requester'].mention}**\n\n"
                       f"`|{parse_duration(current_time)} / ")

        if data["duration"]:
            description += f"{parse_duration(data['duration'])}|`\n\n"
        else:
            description += "LIVE|`\n\n"

        if "view_count" in data:
            description += f":eyes: – {data['view_count']:,}\u3000"
        if "like_count" in data:
            description += f":thumbsup: – {data['like_count']:,}\u3000"
        if "dislike_count" in data:
            description += f":thumbsdown: – {data['dislike_count']:,}\u3000"
        if "comment_count" in data:
            description += f":speech_balloon: – {data['comment_count']:,}"

        embed = discord.Embed(title=data["title"], description=description,
                              timestamp=datetime.datetime.strptime(data["upload_date"], "%Y%m%d"),
                              url=data["webpage_url"], color=find_color(channel))
        if player.paused:
            embed.set_author(name="\U000023f8 Paused")
        elif player.looping:
            embed.set_author(name="\U0001f50a Now Playing\u2000|\u2000\U0001f501 Looping")
        else:
            embed.set_author(name="\U0001f50a Now Playing")
        if data["thumbnail"]:
            embed.set_thumbnail(url=data["thumbnail"])
        embed.set_footer(text="Uploaded:")

        return await channel.send(embed=embed)

    async def interactive_np_msg(self, msg):
        """Makes the "Now Playing" message interactive with reactions"""

        #TODO: Make this one day
        raise NotImplementedError

    # @commands.command()
    # @check_queue(current=True)
    # @has_voted()
    # @check_voice()
    # async def bassboost(self, ctx, level: int=3):
    #     """Bassboost the currently playing song!
    #     WIP
    #     """

    @commands.command(aliases=["leftcleanup"])
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def cleanleft(self, ctx):
        """`DJ` Delete all songs from the queue that were requested by users who are no longer in the voice channel"""

        player = self.get_player(ctx)
        rmvd_songs, left_users = [], []

        for song in player.queue._queue.copy():
            if song["requester"] not in ctx.voice_client.channel.members:
                player.queue._queue.remove(song)
                rmvd_songs.append(song)
                left_users.append(song["requester"])
        left_users = list(set(left_users))

        if len(left_users) == 1:
            w = "who has"
        else:
            w = "who've"

        await ctx.send(
            f"**{len(rmvd_songs)} song{'' if len(rmvd_songs) == 1 else 's'}** requested by "
            f"**{len(left_users)} user{'' if len(left_users) == 1 else 's'}** {w} since left "
            f"this voice channel {'was' if len(rmvd_songs) == 1 else 'were'} removed from the "
            f"queue by {ctx.author.mention}",
            delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(aliases=["rmall", "removeall", "clearqueue"])
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def clear(self, ctx):
        """`DJ` Completely clear the queue"""

        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.send(f"{ctx.author.mention} completely cleared the queue!",
                       delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(aliases=["ffw"], brief="Invalid formatting. The command is supposed to "
                      "look like this:\n`<prefix> forward <seconds to rewind>`")
    @check_queue(current=True)
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def forward(self, ctx, sec: int):
        """Fast-forward the currently playing song
        Format like this: `<prefix> forward <seconds to ffw>`
        """
        player = self.get_player(ctx)
        if not player.current.data["duration"]:
            await ctx.send(f"*{player.current.data['title']}* is playing LIVE, so you can't use "
                           "the forward command on it",
                           delete_after=10.0)
            return await delete_message(ctx, 10)

        if sec <= 0:
            await ctx.send("The number of seconds to fast-forward must be greater than 0",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        current_time = int(time.time() - player.timestamp - player.time_paused)
        if current_time + sec > player.current.data["duration"]:
            await ctx.send(f"That's too far to fast-forward. The song is only "
                           f"`{parse_duration(player.current.data['duration'])}` long",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        return await ctx.invoke(self.seek, parse_duration(current_time + sec))

    @commands.command(aliases=["connect"])
    async def join(self, ctx):
        """Get me to join the voice channel you're in.
        This command can also be used to move me to different channels.
        Note that you don't need to call this command before `play`
        """
        await ctx.channel.trigger_typing()
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("You're not in a voice channel. Join one, then call this command",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                await ctx.send(f"I'm already in \U0001f509{channel.name}", delete_after=5.0)
                return await delete_message(ctx, 5)
            else:
                if ctx.voice_client.is_playing():
                    await ctx.send("I can't switch voice channels while I'm playing something",
                                   delete_after=6.0)
                    return await delete_message(ctx, 6)
                else:
                    await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f"\U00002705  —  Connected to \U0001f509{channel.name}",
                       delete_after=5.0)
        if ctx.command.name == "join":
            return await delete_message(ctx, 5)
        return

    @commands.command(name="loop", aliases=["repeat"])
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def loop_(self, ctx, param: str=""):
        """Loop the currently playing song. Do `loop queue` to loop the entire queue. If a song or the queue is already looping, running this command again will stop the loop"""

        player = self.get_player(ctx)
        if player.looping:
            if not player.paused:
                embed = player.np_msg.embeds[0]
                await player.np_msg.edit(embed=embed.set_author(name="\U0001f50a Now Playing"))
            player.looping = False
            await ctx.send(f"{ctx.author.mention} stopped the song from looping",
                           delete_after=15.0)
            return await delete_message(ctx, 15)
        elif player.queue_looping:
            player.queue_looping = False
            await ctx.send(f"{ctx.author.mention} stopped the queue from looping",
                           delete_after=15.0)
            return await delete_message(ctx, 15)

        param = param.lower()
        if param == "queue":
            if player.queue.empty():
                await ctx.send(
                    "There are no songs in the queue. Use the `play` command to add some",
                    delete_after=6.0)
                return await delete_message(ctx, 6)

            player.queue_looping = True
            data = player.current.data.copy()
            data["seek"] = None
            if player.queue._queue[-1] != data:
                player.queue.put_nowait(data)
            await ctx.send(f"{ctx.author.mention} set the queue to loop continuously",
                           delete_after=15.0)
            return await delete_message(ctx, 15)

        if not player.current:
            await ctx.send("I'm not currently playing anything. Use the `play` command for "
                           "me to play a song", delete_after=7.0)
            return await delete_message(ctx, 7)
        else:
            if not player.paused:
                embed = player.np_msg.embeds[0]
                await player.np_msg.edit(embed=embed.set_author(
                    name="\U0001f50a Now Playing\u2000|\u2000\U0001f501 Looping"))
            player.looping = True
            await ctx.send(f"{ctx.author.mention} set the song to play on a loop",
                            delete_after=15.0)
            return await delete_message(ctx, 15)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def lyrics(self, ctx, *, keywords: str = None):
        """Get the lyrics to a song!
        Format like this: `<prefix> lyrics (OPTIONAL)<song title>`
        If you don't put a song title AND I'm currently playing a song in the voice channel, I'll try to get the lyrics to that song
        """
        if keywords is None and ctx.voice_client:
            player = self.get_player(ctx)
            if player.current:
                keywords = player.current.data["title"]

        if keywords is None:
            await ctx.send("I'm not playing any music in a voice channel right now, so you need "
                           "to put the name of a song for me to get its lyrics",
                           delete_after=10.0)
            return await delete_message(ctx, 10)

        def find_lyrics():
            genius = lyricsgenius.Genius(config.GENIUS, verbose=False)
            song = genius.search_song(keywords)
            return song

        with ctx.channel.typing():
            song = await self.bot.loop.run_in_executor(None, find_lyrics)

        if song is None:
            await ctx.send(f"Sorry, but I couldn't find the song, `{keywords}`", delete_after=6.0)
            return await delete_message(ctx, 6)

        desc = f"__**{song.artist}**__\n"
        if song.featured_artists:
            desc += f"**Featuring**: {', '.join([a['name'] for a in song.featured_artists])}\n"
        if song.album:
            desc += f"**Album**: *{song.album}*\n"
        desc += "\n__**Lyrics**__:\n\n"

        song_lyrics = song.lyrics
        if len(song_lyrics) > 2048 - len(desc):
            song_lyrics = song_lyrics[:2048 - len(desc) - 3] + "..."
        desc += song_lyrics

        if song.year:
            embed = discord.Embed(title=song.title, description=desc,
                                  url=song.url, color=find_color(ctx),
                                  timestamp=datetime.datetime.fromisoformat(song.year))
        else:
            embed = discord.Embed(title=song.title, description=desc,
                                  url=song.url, color=find_color(ctx))

        if song.song_art_image_url:
            embed.set_thumbnail(url=song.song_art_image_url)

        embed.set_author(name="MAT's Bot: Lyric Finder")
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                            "this: `<prefix> move <position of song> (OPTIONAL)<new position>`"
                            "\n\nIf you don't include the new position, the song will be moved "
                            "to first place by default. If the new position is `-1`, the song "
                            "will be moved to the end of the queue")
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def move(self, ctx, song_pos: int, new_pos: int=1):
        """`DJ` Move a song to another position in the queue
        Format like this: `<prefix> move <position of song> (OPTIONAL)<new position>`
        If you don't include the new position, the song will be moved to first place by default
        If the new position is `-1`, the song will be moved to the end of the queue
        """
        if song_pos <= 0:
            await ctx.send("The song position must be the position of a song in the queue "
                           "(use the `queue` command to view it). This isn't like indexing in "
                           "programming (even though I had to use it in the bot's code for this "
                           "command)", delete_after=15.0)
            return await delete_message(ctx, 15)

        if new_pos == 0 or new_pos < -1:
            await ctx.send("The new pos must be the position to move the song to in the queue "
                           "(use the `queue` command to view it) in the queue OR `-1` to move "
                           "it to the end",
                           delete_after=15.0)
            return await delete_message(ctx, 15)

        player = self.get_player(ctx)
        try:
            song = player.queue._queue[song_pos - 1]
        except IndexError:
            await ctx.send(f"The queue only has {player.queue.qsize()} songs in it",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        player.queue._queue.remove(song)
        if new_pos == -1:
            player.queue._queue.append(song)
            new_pos = player.queue.qsize()
        elif new_pos == 1:
            player.queue._queue.appendleft(song)
        else:
            player.queue._queue.insert(new_pos - 1, song)
        if new_pos > player.queue.qsize():
            new_pos = player.queue.qsize()

        await ctx.send(f"Song #{song_pos} in the queue, __*{song['title']}__*, has been moved to "
                       f"position #{new_pos} by {ctx.author.mention}",
                       delete_after=15.0)
        return await delete_message(ctx, 15)

    async def update_db_musicsettings(self, ctx):
        """Update the music settings in the database"""

        async with self.bot.pool.acquire() as conn:
            await conn.execute("""
                UPDATE guilddata
                SET musicsettings = $1::JSON
                WHERE id = {}
            ;""".format(ctx.guild.id), self.bot.guilddata[ctx.guild.id]["musicsettings"])

    @commands.group(invoke_without_command=True)
    async def musicsettings(self, ctx):
        """**Must have the "Manage Server" perm**
        Change the music settings for this server. Running this command will bring up a list of the subcommands and help on how to change the settings
        """
        embed = discord.Embed(
            title="MAT | Music Settings: Help",
            description="**Must have the `Manage Server` perm** for these commands",
            color=find_color(ctx))
        embed.add_field(name=f"{ctx.prefix}musicsettings maxsize <size>",
                        value="Set the maximum number of songs that can be in the queue. To set "
                              "it so that there is no maximum, put `0` for the size",
                        inline=False)
        embed.add_field(name=f"{ctx.prefix}musicsettings setdjrole <role name>",
                        value="Set a role as the server's DJ role. Anyone with this role will be "
                              "able to perform DJ commands, without needing to have the **Manage "
                              "Messages** perm",
                        inline=False)
        embed.add_field(name=f"{ctx.prefix}musicsettings rmdjrole",
                        value="Remove the DJ role if there is one",
                        inline=False)
        embed.add_field(name=f"{ctx.prefix}musicsettings strict",
                        value="Toggle the Strict Perms setting. If it's **off**, the `pause`, "
                              "`resume`, `seek`, `forward`, `rewind`, `replay`, `loop`, and "
                              "`shuffle` commands can be used by anyone. If it's **on**, only "
                              "people with the **Manage Messages** perm or the DJ role (if there "
                              "is one) can use those 8 commands",
                        inline=False)
        await ctx.send(embed=embed)

    @musicsettings.command(brief="Invalid formatting. The command is supposed to look like this: "
                                 "`<prefix> musicsettings maxsize <max size of queue>`\nTo set it "
                                 "so that there is no maximum, put `0` for the size")
    @commands.has_permissions(manage_guild=True)
    async def maxsize(self, ctx, size: int):
        if size == self.bot.guilddata[ctx.guild.id]["musicsettings"]["max_size"]:
            if size:
                await ctx.send(f"The max size of the queue is already {size}", delete_after=5.0)
            else:
                await ctx.send(f"The queue already has no max size", delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.channel.trigger_typing()
        self.bot.guilddata[ctx.guild.id]["musicsettings"]["max_size"] = size
        await self.update_db_musicsettings(ctx)

        if size:
            await ctx.send("The maximum size of the queue has been set to "
                           f"**{size}** songs by {ctx.author.mention}")
        else:
            await ctx.send(f"{ctx.author.mention} set the queue to no longer have a maximum size. "
                           "You can now add all the songs you want!")

    @musicsettings.command()
    @commands.has_permissions(manage_guild=True)
    async def rmdjrole(self, ctx):
        if not self.bot.guilddata[ctx.guild.id]["musicsettings"]["dj_role"]:
            await ctx.send("This server doesn't have a DJ role. Use the `musicsettings setdjrole` "
                           "command to set one", delete_after=8.0)

        await ctx.channel.trigger_typing()
        self.bot.guilddata[ctx.guild.id]["musicsettings"]["dj_role"] = None
        await self.update_db_musicsettings(ctx)

        await ctx.send(f"{ctx.author.mention} removed the DJ role on this server. Now you must "
                       "have the **Manage Messages** perm in order to use the DJ commands")

    @musicsettings.command(brief="Role not found. Try again (Role name is case-sensitive)")
    @commands.has_permissions(manage_guild=True)
    async def setdjrole(self, ctx, *, role: discord.Role):
        if role.id == self.bot.guilddata[ctx.guild.id]["musicsettings"]["dj_role"]:
            await ctx.send(f"**{role.name}** is already set as this server's DJ role",
                           delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.channel.trigger_typing()
        self.bot.guilddata[ctx.guild.id]["musicsettings"]["dj_role"] = role.id
        await self.update_db_musicsettings(ctx)

        await ctx.send(f"**{role.name}** has been set as this server's DJ role by "
                       f"{ctx.author.mention}. Now anyone with this role can use the DJ commands "
                       "without needing to have the **Manage Messages** perm")

    @musicsettings.command()
    @commands.has_permissions(manage_guild=True)
    async def strict(self, ctx):
        await ctx.channel.trigger_typing()

        if self.bot.guilddata[ctx.guild.id]["musicsettings"]["strict"]:
            self.bot.guilddata[ctx.guild.id]["musicsettings"]["strict"] = False
            await self.update_db_musicsettings(ctx)

            await ctx.send(
                f"The Strict Perms setting has been turned **off** for this server by "
                f"{ctx.author.mention}. Now, anyone can use the commands: "
                "`pause`, `resume`, `seek`, `forward`, `rewind`, `replay`, `loop`, and `shuffle`")

        else:
            self.bot.guilddata[ctx.guild.id]["musicsettings"]["strict"] = True
            await self.update_db_musicsettings(ctx)

            await ctx.send(f"The Strict Perms setting has been turned **on** for this server by "
                           f"{ctx.author.mention}. Now, only users with the **Manage Messages** "
                           "perm or the DJ role (if there is one) can use the commands: "
                           "`pause`, `resume`, `seek`, `forward`, `rewind`, `replay`, `loop`, "
                           "and `shuffle`")

    @commands.command()
    @check_queue(current=True)
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def pause(self, ctx):
        """Pause the currently playing song"""

        player = self.get_player(ctx)
        if ctx.voice_client.is_paused():
            await ctx.send("I'm already paused! Use the `resume` command to continue playing",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        ctx.voice_client.pause()
        player.paused = True

        embed = player.np_msg.embeds[0]
        await player.np_msg.edit(embed=embed.set_author(name="\U000023f8 Paused"))

        await ctx.send(f"{ctx.author.mention} **paused** the song!", delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                            "this: `<prefix> play <url OR search term>`\nYou can either put a "
                            "YouTube, Soundcloud, etc. URL OR the title of a song to search for. "
                            "Playlist URLs also work")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def play(self, ctx, *, search):
        """Request a song and add it to the queue
        Format like this: `<prefix> play <url OR search term>`
        You can either put a YouTube, Soundcloud, etc. URL OR the title of a song to search for. Playlist URLs also work
        """
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        if not ctx.author.voice:
            return

        player = self.get_player(ctx)
        max_size = self.bot.guilddata[ctx.guild.id]["musicsettings"]["max_size"]

        temp = await ctx.send("Please wait...")
        with ctx.channel.typing():
            try:
                sources = await YTDLSource.create_source(ctx, search)
            except Exception as e:
                await temp.delete()
                return await ctx.send(
                    f"```{e}```An unknown error occured and I couldn't find that song. Sorry!")

        if len(sources) > 1:
            await ctx.send(f"Attempting to add {len(sources)} songs to the queue...",
                           delete_after=5.0)

        added_songs = []
        for s in sources:
            if max_size:
                if player.queue.qsize() >= max_size:
                    await ctx.send(
                        f"You have reached the maximum queue size for this server, **{max_size}**."
                        " You can't add another song until the queue becomes smaller",
                        delete_after=15.0)
                    await delete_message(ctx, 15)
                    break

            await player.queue.put(s)
            added_songs.append(s)

            embed = discord.Embed(
                title=s["title"],
                description=f"Duration: `{parse_duration(s['duration'])}`",
                url=s["webpage_url"],
                color=find_color(ctx))

            await ctx.send(f"{ctx.author.mention} ADDED a song to the queue",
                           embed=embed, delete_after=30.0)
            await delete_message(ctx, 30)

        if len(added_songs) > 1:
            await ctx.send(f"{len(added_songs) - 1} new songs were added to the queue",
                           delete_after=5.0)
        await temp.delete()

    @commands.command(aliases=["np", "current", "nowplaying"])
    @check_queue(current=True)
    @check_voice()
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def playing(self, ctx):
        """Show the currently playing song"""

        player = self.get_player(ctx)
        try:
            await player.np_msg.delete()
        except (AttributeError, discord.HTTPException):
            pass
        try:
            await player.np_invoker.delete()
        except (AttributeError, discord.HTTPException):
            pass

        player.np_invoker = ctx.message
        player.np_msg = await self.create_np_msg(ctx.channel, player)

    @commands.command(name="queue")
    @check_queue(empty=True)
    @check_voice()
    async def queue_info(self, ctx):
        """See the upcoming songs in the queue"""

        player = self.get_player(ctx)
        queue = list(player.queue._queue)
        chunked_queue = list(chunks(queue, 5))
        embeds = []
        for i in chunked_queue:
            if len(chunked_queue) > 1:
                desc = (f"**Page {chunked_queue.index(i) + 1}/{len(chunked_queue)}**\n\n")
                footer = ("This message will be automatically deleted if left idle for longer "
                          "than 5 minutes")
            else:
                desc = ""
                footer = ""

            desc += (f"**The queue currently has __{len(queue)} "
                     f"song{'' if len(queue) == 1 else 's'}__**")
            if player.queue_looping:
                desc += " **AND is playing on a loop \U0001f501**"

            embed = discord.Embed(title="\U0001f509 Queue | Upcoming Songs",
                                  description=desc,
                                  timestamp=datetime.datetime.utcnow(),
                                  color=find_color(ctx))
            embed.set_footer(text=footer)
            for s in i:
                embed.add_field(
                    name=f"{queue.index(s) + 1}. {s['title']}",
                    value=f"Requested by {s['requester'].mention}\n"
                          f"Duration: `{parse_duration(s['duration'])}`",
                    inline=False)
            embeds.append(embed)

        if len(embeds) == 1:
            return await ctx.send(embed=embeds[0])
        elif len(embeds) <= 4:
            return await send_basic_paginator(ctx, embeds, 5)
        else:
            return await send_advanced_paginator(ctx, embeds, 5)

    @commands.command(name="remove", brief="Invalid formatting. The command is supposed to look "
                      "like this: `<prefix> remove <position in queue>`\n\nIf you don't include a "
                      "position, I'll default to `1` and delete the first song in the queue. You "
                      "can also put `-1` for the position to delete the last song in the queue")
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def remove_from_queue(self, ctx, pos: int=1):
        """`DJ` Remove a song from the queue
        Format like this: `<prefix> remove <position in queue>`
        If you don't include a position, I'll default to `1` and delete the first song in the queue. You can also put `-1` for the position to delete the last song in the queue
        """
        player = self.get_player(ctx)
        try:
            if pos > 0:
                rmvd = player.queue._queue[pos - 1]
            elif pos == -1:
                rmvd = player.queue._queue[pos]
            else:
                raise commands.BadArgument
            player.queue._queue.remove(rmvd)

            embed = discord.Embed(
                title=rmvd["title"],
                description=f"Requested by {rmvd['requester'].mention}\n\n"
                            f"Duration: `{parse_duration(rmvd['duration'])}`",
                url=rmvd["webpage_url"],
                color=find_color(ctx))

            if pos == -1:
                await ctx.send(
                    f"{ctx.author.mention} REMOVED song #{player.queue.qsize()+1} from the queue",
                    embed=embed, delete_after=30.0)
            else:
                await ctx.send(f"{ctx.author.mention} REMOVED song #{pos} from the queue",
                               embed=embed, delete_after=30.0)
            return await delete_message(ctx, 30)
        except IndexError:
            await ctx.send(f"The queue only has {player.queue.qsize()} songs in it",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

    @commands.command()
    @check_queue(current=True)
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def replay(self, ctx):
        """Play the current song from the beginning"""

        await ctx.invoke(self.seek, "0:00")

    @commands.command()
    @check_queue(current=True)
    @is_dj(strict_perm=True)
    @check_voice()
    async def resume(self, ctx):
        """Resume the currently paused song"""

        player = self.get_player(ctx)
        if not ctx.voice_client.is_paused():
            await ctx.send("I'm already unpaused! Use the `pause` command to pause the song",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        ctx.voice_client.resume()
        player.paused = False

        embed = player.np_msg.embeds[0]
        if player.looping:
            embed.set_author(name="\U0001f50a Now Playing\u2000|\u2000\U0001f501 Looping")
        else:
            embed.set_author(name="\U0001f50a Now Playing")
        await player.np_msg.edit(embed=embed)

        await ctx.send(f"{ctx.author.mention} **resumed** the song!", delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(aliases=["back"], brief="Invalid formatting. The command is supposed to "
                      "look like this:\n`<prefix> rewind <seconds to rewind>`")
    @check_queue(current=True)
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def rewind(self, ctx, sec: int):
        """Rewind the currently playing song
        Format like this: `<prefix> rewind <seconds to rewind>`
        """
        player = self.get_player(ctx)
        if not player.current.data["duration"]:
            await ctx.send(f"*{player.current.data['title']}* is playing LIVE, so you can't use "
                           "the rewind command on it",
                           delete_after=10.0)
            return await delete_message(ctx, 10)

        if sec <= 0:
            await ctx.send("The number of seconds to rewind must be greater than 0",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        current_time = int(time.time() - player.timestamp - player.time_paused)
        if current_time - sec < 0:
            await ctx.send("That's too far to rewind. The current position in the song is "
                           f"`{parse_duration(current_time)}`",
                           delete_after=7.0)
            return await delete_message(ctx, 7)

        return await ctx.invoke(self.seek, parse_duration(current_time - sec))

    @commands.command(aliases=["removedupes"])
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def rmdupes(self, ctx):
        """`DJ` Remove duplicate songs from the queue"""

        player = self.get_player(ctx)
        old_queue = player.queue._queue.copy()
        player.queue._queue = collections.deque(
            list({s["title"]:s for s in player.queue._queue}.values())) #* Gets rid of dupes
        rmvd_songs = len(old_queue) - len(player.queue._queue)

        if not rmvd_songs:
            await ctx.send("There are no duplicate songs in the queue", delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.send(f"{rmvd_songs} duplicate song{' was' if rmvd_songs == 1 else 's were'} "
                       f"removed from the queue by {ctx.author.mention}",
                       delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(aliases=["rmmember"], brief="Member not found. Try again")
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def rmuser(self, ctx, user: discord.Member):
        """`DJ` Remove all songs from the queue that were requested by a certain user
        Format like this: `<prefix> rmuser <@mention user>`
        """
        player = self.get_player(ctx)
        rmvd_songs = []

        for song in player.queue._queue.copy():
            if song["requester"] == user:
                player.queue._queue.remove(song)
                rmvd_songs.append(song)

        await ctx.send(
            f"**{len(rmvd_songs)} song{'' if len(rmvd_songs) == 1 else 's'}** requested by "
            f"{user.mention} were removed from the queue by {ctx.author.mention}",
            delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(brief="You didn't format the command correctly. It's supposed to look like "
                            "this: `<prefix> seek <position>`\nThe position should look something "
                            "like this: `1:30`, `10:45`, `1:04:15`, `50` or `0:50`, etc.")
    @check_queue(current=True)
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def seek(self, ctx, pos):
        """Seek to a certain point in the currently playing song
        Format like this: `<prefix> seek <position>`
        The position should look something like this: `1:30`, `10:45`, `1:04:15`, `50` or `0:50`, etc.
        """
        player = self.get_player(ctx)
        if not player.current.data["duration"]:
            await ctx.send(f"*{player.current.data['title']}* is playing LIVE, so you can't use "
                           "the seek command on it",
                           delete_after=10.0)
            return await delete_message(ctx, 10)

        if "-" in pos:
            await ctx.send("You used a negative number in the position. Since negative durations "
                           "don't exist, you have to use positive numbers",
                           delete_after=8.0)
            return await delete_message(ctx, 8)

        try:
            pos = pos.split(":")
            if len(pos) == 1:
                position = int(pos[0])
            elif len(pos) == 2:
                position = (int(pos[0]) * 60) + int(pos[1])
            elif len(pos) == 3:
                position = (int(pos[0]) * 60 * 60) + (int(pos[1]) * 60) + int(pos[2])
            else:
                raise commands.BadArgument
        except:
            raise commands.BadArgument

        if position > player.current.data["duration"]:
            await ctx.send(
                f"The song is only `{parse_duration(player.current.data['duration'])}` long",
                delete_after=5.0)
            return await delete_message(ctx, 5)

        await ctx.channel.trigger_typing()
        data = player.current.data
        source = await YTDLSource.create_source(
            ctx, data["webpage_url"], seek=position, as_list=False)
        player.queue._queue.appendleft(source)

        if player.looping:
            player.looping = False
            ctx.voice_client.stop()
            await asyncio.sleep(0.1)
            player.looping = True
        elif player.queue_looping:
            player.queue_looping = False
            ctx.voice_client.stop()
            await asyncio.sleep(0.5)
            player.queue_looping = True
        else:
            ctx.voice_client.stop()

        await ctx.send(
            f"{ctx.author.mention} seeked to `{parse_duration(position)}` in *{data['title']}*",
            delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command()
    @check_queue(empty=True)
    @is_dj(strict_perm=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def shuffle(self, ctx):
        """Shuffle the songs in the queue"""

        player = self.get_player(ctx)
        random.shuffle(player.queue._queue)
        await ctx.send(f"{ctx.author.mention} **shuffled** the rest of the songs in the queue!",
                       delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command()
    @check_queue(current=True)
    @is_dj(requester_allowed=True)
    @check_voice()
    @commands.cooldown(1, 9, commands.BucketType.user)
    async def skip(self, ctx):
        """**Must be a DJ UNLESS you requested the song**
        Skip the currently playing song and go to the next one
        """
        player = self.get_player(ctx)
        player.looping = False
        ctx.voice_client.stop()
        await ctx.send(f"{ctx.author.mention} **skipped** the song!", delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(brief="Invalid formatting. The command is supposed to look like this: "
                            "`<prefix> skipto <position in queue>`")
    @check_queue(empty=True)
    @is_dj()
    @check_voice()
    async def skipto(self, ctx, pos: int):
        """`DJ` Skip to a different song in the queue
        Format like this: `<prefix> skipto <position in queue>`
        """
        player = self.get_player(ctx)
        if pos <= 0:
            await ctx.send("The position must be above 0", delete_after=5.0)
            return await delete_message(ctx, 5)
        elif pos > player.queue.qsize():
            await ctx.send(f"There are only {player.queue.qsize()} songs in the queue",
                           delete_after=6.0)
            return await delete_message(ctx, 6)

        skipped_songs = list(player.queue._queue)[:pos - 1]
        player.queue._queue = collections.deque(list(player.queue._queue)[pos - 1:])

        player.looping = False
        if player.queue_looping:
            player.queue._queue.extend(skipped_songs)
        ctx.voice_client.stop()
        await ctx.send(f"{ctx.author.mention} **skipped {pos} songs** in the queue!",
                       delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(name="stop")
    @is_dj()
    @check_voice()
    async def stop_(self, ctx):
        """`DJ` Stop the currently playing song, delete the entire queue, and disconnect me from voice"""

        await ctx.voice_client.disconnect()
        await ctx.send(f"{ctx.author.mention} **stopped** the song and deleted the entire queue",
                       delete_after=15.0)
        return await delete_message(ctx, 15)

    @commands.command(aliases=["setvolume", "setvol", "vol"],
                      brief="You didn't format the command correctly. It's supposed to look like "
                            "this: `<prefix> volume <new volume between 1 and 100>`")
    @has_voted()
    @check_voice()
    async def volume(self, ctx, vol: int=None):
        """Set the volume of the music player. By default it's 50
        Format like this: `<prefix> volume <new volume between 1 and 100>`
        """
        if vol < 1 or vol > 100:
            await ctx.send("The volume must be in between 1 and 100", delete_after=5.0)
            return await delete_message(ctx, 5)

        vc = ctx.voice_client
        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100
        player.volume = vol / 100

        await ctx.send(f"{ctx.author.mention} set the volume of the music player to `{vol}/100`",
                       delete_after=15.0)
        return await delete_message(ctx, 15)


def setup(bot):
    bot.add_cog(Music(bot))
