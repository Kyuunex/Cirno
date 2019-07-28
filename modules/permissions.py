import discord
from modules import db


def check(id):
    if db.query(["SELECT user_id FROM admins WHERE user_id = ?", [str(id)]]):
        return 1
    else:
        return 0


def checkowner(id):
    if db.query(["SELECT user_id FROM admins WHERE user_id = ? AND permissions = ?", [str(id), str(1)]]):
        return 1
    else:
        return 0


def botowner():
    owner = db.query(["SELECT user_id FROM admins WHERE permissions = ?", [str(1)]])
    return owner[0][0]


def adminlist():
    contents = ""
    for admin in db.query("SELECT user_id FROM admins"):
        contents += "<@%s>\n" % (admin)
    return discord.Embed(title="Bot admin list", description=contents, color=0xadff2f)


def error():
    embed = discord.Embed(title="This command is reserved for bot admins only", description="Ask <@%s>" % (botowner()), color=0xce1010)
    embed.set_author(name="Lack of permissions",
                     icon_url='https://cdn.discordapp.com/emojis/499963996141518872.png')
    return embed


def ownererror():
    embed = discord.Embed(title="This command is only for", description="<@%s>" % (botowner()), color=0xce1010)
    embed.set_author(name="Lack of permissions",
                     icon_url='https://cdn.discordapp.com/emojis/499963996141518872.png')
    return embed
