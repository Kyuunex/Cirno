import asyncio
import time
import json
import discord
from modules import dbhandler
from modules import osuapi
from modules import osuembed
from modules import csvproc


async def comparelists(list2, list1):
    difference = []
    for i in list1:
        if not i in list2:
            difference.append(i)
    return difference


async def main(client):
    try:
        await asyncio.sleep(10)
        print(time.strftime('%X %x %Z')+' | scoretracking loop')
        tracklist = await dbhandler.query("SELECT * FROM score_tracking_data")
        if tracklist:
            for oneentry in tracklist:
                user_top_scores = await osuapi.get_user_best(oneentry[0])
                if user_top_scores:
                    print("checking user %s" % (oneentry[1]))
                    if oneentry[3] == "force_skip":
                        difference = []
                    else:
                        localdata = json.loads(oneentry[3])
                        difference = await comparelists(localdata, user_top_scores)
                    await dbhandler.query(["UPDATE score_tracking_data SET contents = ? WHERE osu_id = ?", [json.dumps(user_top_scores), oneentry[0]]])
                    for newscore in difference:
                        beatmap = await osuapi.get_beatmap(newscore['beatmap_id'], "b")
                        embed = await print_play(newscore, beatmap, oneentry[1])
                        for onechannel in oneentry[2].split(","):
                            tochannel = client.get_channel(int(onechannel))
                            await tochannel.send(embed=embed)
                else:
                    print("%s | restricted or connection issues" % (str(oneentry[0])))
                await asyncio.sleep(5)
        await asyncio.sleep(1200)
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in scoretracking")
        print(e)
        await asyncio.sleep(7200)


async def track(ctx, userid, channellist):
    user_top_scores = await osuapi.get_user_best(str(userid))
    if user_top_scores:
        trackinfo = await dbhandler.query(["SELECT * FROM score_tracking_data WHERE osu_id = ?", [str(user_top_scores[0]['user_id'])]])
        if not trackinfo:
            osuprofile = await osuapi.get_user(str(userid))
            await dbhandler.query(
                [
                    "INSERT INTO score_tracking_data VALUES (?,?,?,?)", 
                    [
                        str(user_top_scores[0]['user_id']), 
                        str(osuprofile['username']), 
                        str(channellist), 
                        str(json.dumps(user_top_scores)),
                    ]
                ])
            await ctx.send(content='Tracked %s' % (userid))
        else:
            newcsv = await csvproc.csv_add(trackinfo[0][2], channellist)
            await dbhandler.query(["UPDATE score_tracking_data SET channels = ? WHERE osu_id = ?", [newcsv, str(user_top_scores[0]['user_id'])]])
            await ctx.send(content='Tracked %s in here' % (userid))


async def untrack(ctx, userid, channellist):
    trackinfo = await dbhandler.query(["SELECT * FROM score_tracking_data WHERE osu_id = ?", [str(userid)]])
    if trackinfo:
        newcsv = await csvproc.csv_remove(trackinfo[0][2], channellist)
        if newcsv:
            await dbhandler.query(["UPDATE score_tracking_data SET channels = ? WHERE osu_id = ?", [newcsv, str(userid)]])
        else:
            await dbhandler.query(["DELETE FROM score_tracking_data WHERE osu_id = ?", [str(userid)]])
        await ctx.send(content='Untracked %s in here' % (userid))


async def tracklist(ctx, everywhere = None):
    tracklist = await dbhandler.query("SELECT * FROM score_tracking_data")
    if tracklist:
        for oneentry in tracklist:
            if (str(ctx.channel.id) in oneentry[2]) or (everywhere):
                channellist = await csvproc.csv_wrap_entries(oneentry[2])
                await ctx.send(content='osu_id: `%s` | Username: `%s` | channels: %s' % (oneentry[0], oneentry[1], channellist))


async def print_play(play, beatmap, display_name):
    try:
        body = "**%s ☆ %s**\n" % (str(round(float(beatmap['difficultyrating']), 2)), str(beatmap['version']))
        body += "**PP:** %s\n" % (str(play['pp']))
        body += "**Rank:** %s\n" % (str(play['rank']))
        body += "**Accuracy:** %s\n" % (str(await compute_acc(str(play['countmiss']), str(play['count50']), str(play['count100']), str(play['count300'])))+" %")
        body += "**Score:** %s\n" % (str(play['score']))
        body += "**Combo:** %s/%s\n" % (str(play['maxcombo']), str(beatmap['max_combo']))
        body += "**Mods:** %s\n" % (str(await get_mods(int(play['enabled_mods']))))
        body += "**300x/100x/50x/0x:** %s/%s/%s/%s\n" % (str(play['count300']), str(play['count100']), str(play['count50']), str(play['countmiss']))
        body += "**Date:** %s\n" % (str(play['date']))
        embed = discord.Embed(
            title=str(beatmap['title']), 
            description=body, 
            url='https://osu.ppy.sh/beatmapsets/%s' % (str(beatmap['beatmapset_id'])), 
            color=await compute_color(play, beatmap)
        )
        embed.set_author(
            name="%s just made a new top play on:" % (display_name),
            url="https://osu.ppy.sh/users/%s" % (str(play['user_id'])),
            icon_url="https://a.ppy.sh/%s" % (str(play['user_id']))
        )
        embed.set_thumbnail(
            url="https://b.ppy.sh/thumb/%sl.jpg" % (str(beatmap['beatmapset_id']))
        )
        embed.set_footer(
            text="Made by Kyuunex", 
            icon_url='https://avatars0.githubusercontent.com/u/5400432'
        )
        return embed
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in scoretracking.print_play")
        print(e)
        return None


async def compute_color(play, beatmap):
    sr = round(float(beatmap['difficultyrating']), 2)
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


async def compute_acc(cmiss, c50, c100, c300):
    # Thanks Ayato_k
    return str(round(float(((int(c50)*50 + int(c100)*100 + int(c300)*300) / ((int(cmiss)+int(c50)+int(c100)+int(c300))*300))*100), 2))


async def get_mods(number):
    # Thanks Ayato_k
    mod_list = ['NF', 'EZ', 'NV', 'HD', 'HR', 'SD', 'DT', '128', 'HT', 'NC', 'FL', 'AutoPlay', 'SO', 'AP', 'PF', '4K', '5K', '6K', '7K', '8K', 'KM', 'FI', 'RanD', 'LM', 'FM', '9K', '10K', '1K', '3K', '2K']
    if number <= 0:
        return 'None'
    bin_list = [int(x) for x in bin(number)[2:]]
    i=0
    mod_str = ''
    for y in reversed(bin_list):
        if y == 1:
            mod_str += mod_list[i]
        i+=1
    return mod_str