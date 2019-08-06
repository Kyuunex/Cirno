#!/usr/bin/env python3

import discord
import asyncio
from discord.ext import commands
import os

from modules import permissions
from osuembed import osuembed
from modules import db
from modules import score_tracking

from modules.connections import osu as osu
from modules.connections import database_file as database_file
from modules.connections import bot_token as bot_token

client = commands.Bot(command_prefix=',', description='Cirno teaches you how to be a bot master.')
#client.remove_command('help')
appversion = "b20190806"

if not os.path.exists(database_file):
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query("CREATE TABLE score_tracking_tracklist (osu_id, osu_username)")
    db.query("CREATE TABLE score_tracking_channels (osu_id, channel_id, gamemode)")
    db.query("CREATE TABLE score_tracking_posted_scores (osu_id, score_id)")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not db.query("SELECT * FROM admins"):
        appinfo = await client.application_info()
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(appinfo.owner.id), "1"]])
        print("Added %s to admin list" % (appinfo.owner.name))


@client.command(name="adminlist", brief="Show bot admin list.", description="", pass_context=True)
async def adminlist(ctx):
    await ctx.send(embed=permissions.adminlist())


@client.command(name="makeadmin", brief="Add a user to bot admin list.", description="", pass_context=True)
async def makeadmin(ctx, user_id: str):
    if permissions.checkowner(ctx.message.author.id):
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(user_id), "0"]])
        await ctx.send(":ok_hand:")
    else:
        await ctx.send(embed=permissions.ownererror())


@client.command(name="restart", brief="Restart the bot", description="", pass_context=True)
async def restart(ctx):
    if permissions.check(ctx.message.author.id):
        await ctx.send("Restarting")
        quit()
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="update", brief="Update the bot", description="it just does git pull", pass_context=True)
async def update(ctx):
    if permissions.check(ctx.message.author.id):
        await ctx.send("Updating.")
        os.system('git pull')
        quit()
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="sql", brief="Executre an SQL query.", description="", pass_context=True)
async def sql(ctx, *, query):
    if permissions.checkowner(ctx.message.author.id):
        if len(query) > 0:
            response = db.query(query)
            await ctx.send(response)
    else:
        await ctx.send(embed=permissions.ownererror())


@client.command(name="mapset", brief="Show mapset info.", description="", pass_context=True)
async def mapset(ctx, mapsetid: str, text: str = None):
    if permissions.check(ctx.message.author.id):
        result = await osu.get_beatmapset(s=mapsetid) 
        embed = await osuembed.beatmapset(result)
        if embed:
            await ctx.send(content=text, embed=embed)
        else:
            await ctx.send(content='`No mapset found with that ID`')
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="user", brief="Show osu user info.", description="", pass_context=True)
async def user(ctx, *, username):
    result = await osu.get_user(u=username)
    embed = await osuembed.user(result)
    if embed:
        await ctx.send(embed=embed)
    else:
        await ctx.send(content='`No user found with that username`')


@client.command(name="track", brief="Start tracking user's scores.", description="", pass_context=True)
async def scoretrack(ctx, user_id, gamemode = "0"):
    if permissions.check(ctx.message.author.id):
        await score_tracking.track(ctx.channel, user_id, gamemode)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="untrack", brief="Stop tracking user's scores.", description="", pass_context=True)
async def scoreuntrack(ctx, user_id, gamemode = "0"):
    if permissions.check(ctx.message.author.id):
        await score_tracking.untrack(ctx.channel, user_id, gamemode)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="tracklist", brief="Show a list of all users being tracked and where.", description="", pass_context=True)
async def scoretracklist(ctx, everywhere = None):
    if permissions.check(ctx.message.author.id):
        await score_tracking.print_tracklist(ctx.channel, everywhere)
    else:
        await ctx.send(embed=permissions.error())


async def score_tracking_background_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await score_tracking.main(client)

client.loop.create_task(score_tracking_background_loop())
client.run(bot_token)
