#!/usr/bin/env python3

import discord
import asyncio
from discord.ext import commands
import os

from modules import permissions
from modules import osuapi
from modules import osuembed
from modules import dbhandler
from modules import scoretracking

client = commands.Bot(command_prefix=',', description='Cirno teaches you how to be a bot master.')
#client.remove_command('help')
appversion = "b20190517"


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not os.path.exists('data/maindb.sqlite3'):
        appinfo = await client.application_info()
        await dbhandler.query("CREATE TABLE config (setting, parent, value, flag)")
        await dbhandler.query("CREATE TABLE admins (user_id, permissions)")
        await dbhandler.query("CREATE TABLE score_tracking_data (osu_id, osu_username, channels, contents)")
        await dbhandler.query(["INSERT INTO admins VALUES (?, ?)", [str(appinfo.owner.id), "1"]])


@client.command(name="adminlist", brief="Show bot admin list.", description="", pass_context=True)
async def adminlist(ctx):
    await ctx.send(embed=await permissions.adminlist())


@client.command(name="makeadmin", brief="Add a user to bot admin list.", description="", pass_context=True)
async def makeadmin(ctx, user_id: str):
    if await permissions.checkowner(ctx.message.author.id):
        await dbhandler.query(["INSERT INTO admins VALUES (?, ?)", [str(user_id), "0"]])
        await ctx.send(":ok_hand:")
    else:
        await ctx.send(embed=await permissions.ownererror())


@client.command(name="restart", brief="Restart the bot.", description="", pass_context=True)
async def restart(ctx):
    if await permissions.check(ctx.message.author.id):
        await ctx.send("Restarting")
        quit()
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="gitpull", brief="Update the bot.", description="Grabs the latest version from GitHub.", pass_context=True)
async def gitpull(ctx):
    if await permissions.check(ctx.message.author.id):
        await ctx.send("Fetching the latest version from the repository and updating from version %s" % (appversion))
        os.system('git pull')
        quit()
        # exit()
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="sql", brief="Executre an SQL query.", description="", pass_context=True)
async def sql(ctx, *, query):
    if await permissions.checkowner(ctx.message.author.id):
        if len(query) > 0:
            response = await dbhandler.query(query)
            await ctx.send(response)
    else:
        await ctx.send(embed=await permissions.ownererror())


@client.command(name="mapset", brief="Show mapset info.", description="", pass_context=True)
async def mapset(ctx, mapsetid: str, text: str = None):
    if await permissions.check(ctx.message.author.id):
        embed = await osuembed.mapset(await osuapi.get_beatmaps(mapsetid))
        if embed:
            await ctx.send(content=text, embed=embed)
            # await ctx.message.delete()
        else:
            await ctx.send(content='`No mapset found with that ID`')
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="user", brief="Show osu user info.", description="", pass_context=True)
async def user(ctx, *, username):
    embed = await osuembed.osuprofile(await osuapi.get_user(username))
    if embed:
        await ctx.send(embed=embed)
        # await ctx.message.delete()
    else:
        await ctx.send(content='`No user found with that username`')


@client.command(name="track", brief="Start tracking user's scores.", description="", pass_context=True)
async def scoretrack(ctx, *, userid):
    if await permissions.check(ctx.message.author.id):
        csv_channellist = None
        if csv_channellist == None:
            csv_channellist = ctx.channel.id
        await scoretracking.track(ctx, userid, csv_channellist)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="untrack", brief="Stop tracking user's scores.", description="", pass_context=True)
async def scoreuntrack(ctx, *, userid):
    if await permissions.check(ctx.message.author.id):
        csv_channellist = None
        if csv_channellist == None:
            csv_channellist = ctx.channel.id
        await scoretracking.untrack(ctx, userid, csv_channellist)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="tracklist", brief="Show a list of all users being tracked and where.", description="", pass_context=True)
async def scoretracklist(ctx, everywhere = None):
    if await permissions.check(ctx.message.author.id):
        await scoretracking.tracklist(ctx, everywhere)
    else:
        await ctx.send(embed=await permissions.error())


async def scoretracking_background_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await scoretracking.main(client)

client.loop.create_task(scoretracking_background_loop())
client.run(open("data/token.txt", "r+").read(), bot=True)
