import asyncio
import time
import discord
from modules import db
from modules.connections import osu as osu

async def main(client):
    try:
        await asyncio.sleep(10)
        print(time.strftime('%X %x %Z')+' | scoretracking loop')
        score_tracklist = db.query("SELECT * FROM score_tracking_tracklist")
        if score_tracklist:
            for one_user in score_tracklist:
                await checking_process(client, one_user)
        await asyncio.sleep(1200)
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in scoretracking")
        print(e)
        await asyncio.sleep(7200)


async def checking_process(client, one_user):
    user_id = one_user[0]
    user_name = one_user[1]
    channel_list = db.query(["SELECT channel_id FROM score_tracking_channels WHERE osu_id = ?", [str(user_id)]])
    if channel_list:
        await check_one_user(client, user_id, user_name, "0")
        await asyncio.sleep(1)
        await check_one_user(client, user_id, user_name, "1")
        await asyncio.sleep(1)
        await check_one_user(client, user_id, user_name, "2")
        await asyncio.sleep(1)
        await check_one_user(client, user_id, user_name, "3")
    else:
        print("%s is not tracked anywhere so I am gonna delete it from all tables" % (user_name))
        db.query(["DELETE FROM score_tracking_channels WHERE osu_id = ?", [str(user_id)]])
        db.query(["DELETE FROM score_tracking_posted_scores WHERE osu_id = ?", [str(user_id)]])
        db.query(["DELETE FROM score_tracking_tracklist WHERE osu_id = ?", [str(user_id)]])
    await asyncio.sleep(5)


async def check_one_user(client, user_id, user_name, gamemode):
    channel_list_gamemode = db.query(["SELECT channel_id FROM score_tracking_channels WHERE osu_id = ? AND gamemode = ?", [str(user_id), str(gamemode)]])
    if channel_list_gamemode:
        print("Currently checking %s on gamemode %s" % (user_name, gamemode))
        user_top_scores = await osu.get_user_best(u=user_id, limit="15", m=str(gamemode))
        if user_top_scores:
            for score in user_top_scores:
                if not db.query(["SELECT score_id FROM score_tracking_posted_scores WHERE score_id = ?", [str(score.id)]]):
                    beatmap = await osu.get_beatmap(b=score.beatmap_id)
                    embed = await print_play(score, beatmap, user_name, gamemode)
                    for channel_id in channel_list_gamemode:
                        channel = client.get_channel(int(channel_id[0]))
                        await channel.send(embed=embed)
                    db.query(["INSERT INTO score_tracking_posted_scores VALUES (?, ?)", [str(user_id), str(score.id)]])
        else:
            print("%s | restricted " % (user_id))


async def track(channel, user_id, gamemode):
    user_top_scores = await osu.get_user_best(u=user_id, limit="15", m=str(gamemode))
    user = await osu.get_user(u=user_id)
    if user_top_scores:
        if not db.query(["SELECT * FROM score_tracking_tracklist WHERE osu_id = ?", [str(user.id)]]):
            db.query(["INSERT INTO score_tracking_tracklist VALUES (?,?)", [str(user.id), str(user.name)]])

        for score in user_top_scores:
            if not db.query(["SELECT score_id FROM score_tracking_posted_scores WHERE score_id = ?", [str(score.id)]]):
                db.query(["INSERT INTO score_tracking_posted_scores VALUES (?, ?)", [str(user.id), str(score.id)]])

        if not db.query(["SELECT * FROM score_tracking_channels WHERE channel_id = ? AND gamemode = ? AND osu_id = ?", [str(channel.id), str(gamemode), str(user.id)]]):
            db.query(["INSERT INTO score_tracking_channels VALUES (?, ?, ?)", [str(user.id), str(channel.id), str(gamemode)]])
            await channel.send(content='Tracked `%s` in this channel with gamemode %s' % (user.name, gamemode))
        else:
            await channel.send(content='User `%s` is already tracked in this channel' % (user.name))


async def untrack(channel, user_id, gamemode):
    user = await osu.get_user(u=user_id)
    if user:
        user_id = user.id
        user_name = user.name
    else:
        user_name = user_id
    db.query(["DELETE FROM score_tracking_channels WHERE osu_id = ? AND channel_id = ? AND gamemode = ?", [str(user_id), str(channel.id), str(gamemode)]])
    await channel.send(content='`%s` is no longer tracked in this channel with gamemode %s' % (user_name, gamemode))


async def print_tracklist(channel, everywhere = None):
    tracklist = db.query("SELECT * FROM score_tracking_tracklist")
    if tracklist:
        for one_entry in tracklist:
            destination_list = db.query(["SELECT channel_id, gamemode FROM score_tracking_channels WHERE osu_id = ?", [str(one_entry[0])]])
            destination_list_str = ""
            for destination_id in destination_list:
                destination_list_str += ("<#%s>:%s " % (str(destination_id[0]), str(destination_id[1])))
            if (str(channel.id) in destination_list_str) or (everywhere):
                await channel.send(content='osu_id: `%s` | Username: `%s` | channels: %s' % (one_entry[0], one_entry[1], destination_list_str))

def get_gamemode(mode_id):
    gamemodes = [
        "osu!",
        "Taiko",
        "CtB",
        "osu!mania",
    ]
    return gamemodes[int(mode_id)]

def get_gamemode_icon(mode_id):
    gamemodes = [
        "https://raw.githubusercontent.com/ppy/osu-web/master/public/images/badges/user-achievements/osu-plays-5000.png",
        "https://raw.githubusercontent.com/ppy/osu-web/master/public/images/badges/user-achievements/taiko-hits-30000.png",
        "https://raw.githubusercontent.com/ppy/osu-web/master/public/images/badges/user-achievements/fruits-hits-20000.png",
        "https://raw.githubusercontent.com/ppy/osu-web/master/public/images/badges/user-achievements/mania-hits-40000.png",
    ]
    return gamemodes[int(mode_id)]

async def print_play(score, beatmap, display_name, gamemode):
    try:
        body = "**%s ☆ %s**\n" % (str(round(float(beatmap.difficultyrating), 2)), str(beatmap.version))
        body += "**PP:** %s\n" % (str(score.pp))
        body += "**Rank:** %s\n" % (str(score.rank))
        body += "**Accuracy:** %s\n" % (str(score.accuracy)+" %")
        body += "**Score:** %s\n" % (str(score.score))
        body += "**Combo:** %s/%s\n" % (str(score.maxcombo), str(beatmap.max_combo))
        body += "**Mods:** %s\n" % (str(score.mods))
        body += "**300x/100x/50x/0x:** %s/%s/%s/%s\n" % (str(score.count300), str(score.count100), str(score.count50), str(score.countmiss))
        body += "**Date:** %s\n" % (str(score.date))
        embed = discord.Embed(
            title=str(beatmap.title), 
            description=body, 
            url=beatmap.url, 
            color=compute_color(score, beatmap)
        )
        embed.set_author(
            name="%s just made a new top play on:" % (display_name),
            url="https://osu.ppy.sh/users/%s" % (str(score.user_id)),
            icon_url="https://a.ppy.sh/%s" % (str(score.user_id))
        )
        embed.set_thumbnail(
            url=beatmap.thumb
        )
        embed.set_footer(
            text=get_gamemode(gamemode), 
            icon_url=get_gamemode_icon(gamemode)
        )
        return embed
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in scoretracking.print_play")
        print(e)
        return None


def compute_color(play, beatmap):
    sr = round(float(beatmap.difficultyrating), 2)
    if sr <= 1:
        return 0x00ff00
    elif sr > 1 and sr <= 2:
        return 0xccff33
    elif sr > 2 and sr <= 3:
        return 0xffff00
    elif sr > 3 and sr <= 4:
        return 0xff9900
    elif sr > 4 and sr <= 4.5:
        return 0xff6600
    elif sr > 4.5 and sr <= 5:
        return 0xff0066
    elif sr > 5 and sr <= 5.5:
        return 0xcc00ff
    elif sr > 5.5 and sr <= 6:
        return 0x9933ff
    elif sr > 6 and sr <= 6.5:
        return 0x3333cc
    elif sr > 6.5:
        return 0x003366
