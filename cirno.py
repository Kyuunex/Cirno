#!/usr/bin/env python3

import discord
from discord.ext import commands
import os

from modules import db

from modules.connections import database_file as database_file
from modules.connections import bot_token as bot_token

command_prefix = ','
appversion = "s20191017.2"
client = commands.Bot(command_prefix=command_prefix, 
                      description='Cirno %s' % (appversion),
                      activity=discord.Game("Version %s" % appversion))

if not os.path.exists(database_file):
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query("CREATE TABLE scoretracking_tracklist (osu_id, osu_username)")
    db.query("CREATE TABLE scoretracking_channels (osu_id, channel_id, gamemode)")
    db.query("CREATE TABLE scoretracking_history (osu_id, score_id)")

initial_extensions = [
    'cogs.BotManagement', 
    'cogs.ScoreTracking', 
]

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print(e)

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

client.run(bot_token)
