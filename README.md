# Cirno
Cirno is a osu! score tracking bot. It will post when a tracked user makes a new top play. Supports all 4 gamemodes.

This bot is built using discord.py and uses sqlite3 database.

---

## Installation Instructions

1. Install `git` and `Python 3.5.3` (or newer) if you don't already have them.
2. Clone this repository using this command `git clone https://github.com/Kyuunex/Cirno.git`.
3. Install `discord.py` using this command `python3 -m pip install -U discord.py[voice]`.
4. `pip3 install pycountry`.
5. `pip3 install git+https://github.com/Kyuunex/aioosuapi.git@v1`
6. `pip3 install git+https://github.com/Kyuunex/osudiscordpyembed.git`
7. Create a folder named `data`, then create `token.txt` and `osu_api_key.txt` inside it. Then put your bot token and osu api key in them. 
8. To start the bot, run `cirno.bat` if you are on windows or `cirno.sh` if you are on linux. Alternatively, you can manually run `cirno.py` file but I recommend using the included launchers because it starts the bot in a loop which is required by the `,restart` and `,update` commands.

## How to use

1. Use `,help` to bring up the help menu.
