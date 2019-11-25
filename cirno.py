#!/usr/bin/env python3

from discord.ext import commands
import os

from modules import db

from modules.connections import database_file as database_file
from modules.connections import bot_token as bot_token

command_prefix = ","
app_version = "s20191125"
client = commands.Bot(command_prefix=command_prefix,
                      description=f"Cirno {app_version}")

if not os.path.exists(database_file):
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query("CREATE TABLE scoretracking_tracklist (osu_id, osu_username)")
    db.query("CREATE TABLE scoretracking_channels (osu_id, channel_id, gamemode)")
    db.query("CREATE TABLE scoretracking_history (osu_id, score_id)")

initial_extensions = [
    "cogs.BotManagement",
    "cogs.ScoreTracking",
]

if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print(e)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")
    if not db.query("SELECT * FROM admins"):
        app_info = await client.application_info()
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(app_info.owner.id), "1"]])
        print(f"Added {app_info.owner.name} to admin list")


client.run(bot_token)
