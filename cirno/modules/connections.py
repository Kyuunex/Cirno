import os
from cirno.modules.storage_management import dirs


if os.environ.get('CIRNO_TOKEN'):
    bot_token = os.environ.get('CIRNO_TOKEN')
else:
    try:
        with open(dirs.user_data_dir + "/token.txt", "r+") as token_file:
            bot_token = token_file.read().strip()
    except FileNotFoundError as e:
        print("i need a bot token. either set CIRNO_TOKEN environment variable")
        print("or put it in token.txt in my AppData/.config folder")
        raise SystemExit

if os.environ.get('CIRNO_OSU_API_KEY'):
    osu_api_key = os.environ.get('CIRNO_OSU_API_KEY')
else:
    try:
        with open(dirs.user_data_dir + "/osu_api_key.txt", "r+") as token_file:
            osu_api_key = token_file.read().strip()
    except FileNotFoundError as e:
        print("i need a osu api key. either set CIRNO_OSU_API_KEY environment variable")
        print("or put it in token.txt in my AppData/.config folder")
        raise SystemExit
