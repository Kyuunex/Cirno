import sqlite3
from cirno.modules.storage_management import database_file


async def add_admins(self):
    async with await self.db.execute("SELECT user_id, permissions FROM admins") as cursor:
        admin_list = await cursor.fetchall()

    if not admin_list:
        app_info = await self.application_info()
        if app_info.team:
            for team_member in app_info.team.members:
                await self.db.execute("INSERT INTO admins VALUES (?, ?)", [int(team_member.id), 1])
                print(f"Added {team_member.name} to admin list")
        else:
            await self.db.execute("INSERT INTO admins VALUES (?, ?)", [int(app_info.owner.id), 1])
            print(f"Added {app_info.owner.name} to admin list")
        await self.db.commit()


def ensure_tables():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS "config" (
        "setting"    TEXT, 
        "parent"    TEXT,
        "value"    TEXT,
        "flag"    TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS "admins" (
        "user_id"    INTEGER NOT NULL UNIQUE,
        "permissions"    INTEGER NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS "ignored_users" (
        "user_id"    INTEGER NOT NULL UNIQUE,
        "reason"    TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS "scoretracking_channels" (
        "osu_id"    INTEGER NOT NULL,
        "channel_id"    INTEGER NOT NULL,
        "gamemode"    INTEGER NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS "scoretracking_history" (
        "osu_id"    INTEGER NOT NULL,
        "score_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS "scoretracking_tracklist" (
        "osu_id"    INTEGER NOT NULL,
        "osu_username"    TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
