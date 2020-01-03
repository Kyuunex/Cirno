import asyncio
import time
import discord
from discord.ext import commands
from modules import db
from modules import permissions
from modules.connections import osu as osu


class ScoreTracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.scoretracking_background_loop())
        )

    @commands.command(name="track", brief="Start tracking user's scores",
                      description="0 = osu!, 1 = osu!taiko, 2 = osu!catch, 3 = osu!mania")
    @commands.check(permissions.is_admin)
    async def track(self, ctx, user_id, gamemode="0"):
        channel = ctx.channel
        user_top_scores = await osu.get_user_best(u=user_id, limit="5", m=str(gamemode))
        user = await osu.get_user(u=user_id)
        if user_top_scores:
            if not db.query(["SELECT * FROM scoretracking_tracklist WHERE osu_id = ?", [str(user.id)]]):
                db.query(["INSERT INTO scoretracking_tracklist VALUES (?,?)", [str(user.id), str(user.name)]])

            for score in user_top_scores:
                if not db.query(["SELECT score_id FROM scoretracking_history WHERE score_id = ?", [str(score.id)]]):
                    db.query(["INSERT INTO scoretracking_history VALUES (?, ?)", [str(user.id), str(score.id)]])

            if not db.query(
                    ["SELECT * FROM scoretracking_channels "
                     "WHERE channel_id = ? AND gamemode = ? AND osu_id = ?",
                     [str(channel.id), str(gamemode), str(user.id)]]):
                db.query(["INSERT INTO scoretracking_channels VALUES (?, ?, ?)",
                          [str(user.id), str(channel.id), str(gamemode)]])
                await channel.send(content=f"Tracked `{user.name}` in this channel with gamemode {gamemode}")
            else:
                await channel.send(content=f"User `{user.name}` is already tracked in this channel")

    @commands.command(name="untrack", brief="Stop tracking user's scores", description="")
    @commands.check(permissions.is_admin)
    async def untrack(self, ctx, user_id, gamemode="0"):
        channel = ctx.channel
        user = await osu.get_user(u=user_id)
        if user:
            user_id = user.id
            user_name = user.name
        else:
            user_name = user_id
        db.query(["DELETE FROM scoretracking_channels "
                  "WHERE osu_id = ? AND channel_id = ? AND gamemode = ?",
                  [str(user_id), str(channel.id), str(gamemode)]])
        await channel.send(content=f"`{user_name}` is no longer tracked in this channel with gamemode {gamemode}")

    @commands.command(name="tracklist", brief="Show a list of all users being tracked and where", description="")
    @commands.check(permissions.is_admin)
    async def tracklist(self, ctx, everywhere=None):
        channel = ctx.channel
        tracklist = db.query("SELECT * FROM scoretracking_tracklist")
        if tracklist:
            for one_entry in tracklist:
                destination_list = db.query(["SELECT channel_id, gamemode FROM scoretracking_channels "
                                             "WHERE osu_id = ?",
                                             [str(one_entry[0])]])
                destination_list_str = ""
                for destination_id in destination_list:
                    destination_list_str += f"<#{destination_id[0]}>:{destination_id[1]} "
                if (str(channel.id) in destination_list_str) or everywhere:
                    await channel.send(f"osu_id: `{one_entry[0]}` "
                                       f"| Username: `{one_entry[1]}` "
                                       f"| channels: {destination_list_str}")

    async def scoretracking_background_loop(self):
        print("Score tracking Loop launched!")
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await asyncio.sleep(10)
                score_tracklist = db.query("SELECT * FROM scoretracking_tracklist")
                if score_tracklist:
                    print(time.strftime("%X %x %Z") + " | started checking scores")
                    for one_user in score_tracklist:
                        await self.checking_process(one_user)
                    print(time.strftime("%X %x %Z") + " | finished checking scores")
                await asyncio.sleep(1200)
            except Exception as e:
                print(time.strftime("%X %x %Z"))
                print("in scoretracking")
                print(e)
                await asyncio.sleep(7200)

    async def checking_process(self, one_user):
        user_id = one_user[0]
        user_name = one_user[1]
        channel_list = db.query(["SELECT channel_id FROM scoretracking_channels WHERE osu_id = ?", [str(user_id)]])
        if channel_list:
            await self.check_one_user(user_id, user_name, "0")
            await asyncio.sleep(1)
            await self.check_one_user(user_id, user_name, "1")
            await asyncio.sleep(1)
            await self.check_one_user(user_id, user_name, "2")
            await asyncio.sleep(1)
            await self.check_one_user(user_id, user_name, "3")
        else:
            print(f"{user_name} is not tracked anywhere so I am gonna delete it from all tables")
            db.query(["DELETE FROM scoretracking_channels WHERE osu_id = ?", [str(user_id)]])
            db.query(["DELETE FROM scoretracking_history WHERE osu_id = ?", [str(user_id)]])
            db.query(["DELETE FROM scoretracking_tracklist WHERE osu_id = ?", [str(user_id)]])
        await asyncio.sleep(5)

    async def check_one_user(self, user_id, user_name, gamemode):
        channel_list_gamemode = db.query(["SELECT channel_id FROM scoretracking_channels "
                                          "WHERE osu_id = ? AND gamemode = ?",
                                          [str(user_id), str(gamemode)]])
        if channel_list_gamemode:
            print(f"Currently checking {user_name} on gamemode {gamemode}")
            user_top_scores = await osu.get_user_best(u=user_id, limit="5", m=str(gamemode))
            if user_top_scores:
                for score in user_top_scores:
                    if not db.query(["SELECT score_id FROM scoretracking_history WHERE score_id = ?", [str(score.id)]]):
                        beatmap = await osu.get_beatmap(b=score.beatmap_id)
                        embed = await self.print_play(score, beatmap, user_name, gamemode)
                        for channel_id in channel_list_gamemode:
                            channel = self.bot.get_channel(int(channel_id[0]))
                            await channel.send(embed=embed)
                        db.query(["INSERT INTO scoretracking_history VALUES (?, ?)", [str(user_id), str(score.id)]])
            else:
                print(f"{user_id} | restricted")

    def get_gamemode(self, mode_id):
        gamemodes = [
            "osu!",
            "osu!taiko",
            "osu!catch",
            "osu!mania",
        ]
        return gamemodes[int(mode_id)]

    async def print_play(self, score, beatmap, display_name, gamemode):
        try:
            body = f"**{str(round(float(beatmap.difficultyrating), 2))} ☆ {beatmap.version}**\n"
            body += f"**PP:** {score.pp}\n"
            body += f"**Rank:** {score.rank}\n"
            body += f"**Accuracy:** {score.accuracy} %\n"
            body += f"**Score:** {score.score}\n"
            body += f"**Combo:** {score.maxcombo}/{beatmap.max_combo}\n"
            body += f"**Mods:** {score.mods}\n"
            body += f"**300x/100x/50x/0x:** {score.count300}/{score.count100}/{score.count50}/{score.countmiss}\n"
            body += f"**Date:** {score.date}\n"
            embed = discord.Embed(
                title=beatmap.title,
                description=body,
                url=beatmap.url,
                color=self.compute_color(score, beatmap)
            )
            embed.set_author(
                name=f"{display_name} just made a new top play on:",
                url=f"https://osu.ppy.sh/users/{score.user_id}",
                icon_url=f"https://a.ppy.sh/{score.user_id}",
            )
            embed.set_thumbnail(
                url=beatmap.thumb
            )
            embed.set_footer(
                text=self.get_gamemode(gamemode),
            )
            return embed
        except Exception as e:
            print(time.strftime("%X %x %Z"))
            print("in scoretracking.print_play")
            print(e)
            return None

    def compute_color(self, play, beatmap):
        sr = round(float(beatmap.difficultyrating), 2)
        if sr <= 1:
            return 0x00ff00
        elif 1 < sr <= 2:
            return 0xccff33
        elif 2 < sr <= 3:
            return 0xffff00
        elif 3 < sr <= 4:
            return 0xff9900
        elif 4 < sr <= 4.5:
            return 0xff6600
        elif 4.5 < sr <= 5:
            return 0xff0066
        elif 5 < sr <= 5.5:
            return 0xcc00ff
        elif 5.5 < sr <= 6:
            return 0x9933ff
        elif 6 < sr <= 6.5:
            return 0x3333cc
        elif sr > 6.5:
            return 0x003366


def setup(bot):
    bot.add_cog(ScoreTracking(bot))
