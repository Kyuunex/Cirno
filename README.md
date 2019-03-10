# Cirno
Cirno is a osu! score tracking bot. It will post when a user makes a new top play.  
(Contains some of Ayato_K's code because I am to lazy to rewrite literally everything.)

This bot is built using discord.py rewrite library and uses sqlite3 database.

---

## Installation Instructions

1. Install git.
2. Clone this repo using this command `git clone https://github.com/Kyuunex/Cirno.git`
3. Install `Python 3.5.3` or newer
4. Install `discord.py rewrite library` using this command `python -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]` for windows or `python3 -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice] --user` for linux
5. Install `pycountry` using this command `pip install <package name>`. (`pip3` on linux)
6. Before using, you need to create a folder called `data` and create `token.txt` and `osuapikey.txt` in it. Then put your bot token and osu api key in the files. 
7. To start the bot, run `cirno.bat` if you are on windows or `cirno.sh` if you are on linux. Alternatively, you can manually run `run.py` file but I recommend using the included launchers because it starts the bot in a loop which is required by the `;restart` and `;gitpull` commands.

## How to use

1. Use `,help` to bring up the help menu.

## Support

To see this bot in action or if you need help setting it up, you can join the support server https://discord.gg/KGjYZZg but please, before you ask me anything, try to figure out how to make it work yourself.