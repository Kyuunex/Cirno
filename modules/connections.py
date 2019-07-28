from aioosuapi import aioosuapi

osu_api_key = open("data/osu_api_key.txt", "r+").read()
bot_token = open("data/token.txt", "r+").read()
database_file = 'data/maindb.sqlite3'
osu = aioosuapi.aioosuapi(osu_api_key)
