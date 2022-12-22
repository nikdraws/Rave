import discord
from discord.ext import commands
import aiosqlite
import asyncio
import time
import random
from dotenv import load_dotenv, find_dotenv
import os


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
load_dotenv(find_dotenv())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    setattr(bot, 'db', await aiosqlite.connect("level.db"))
    await asyncio.sleep(3)
    async with bot.db.cursor() as cursor:
        await cursor.execute("""CREATE TABLE IF NOT EXISTS levels
                                (user INT PRIMARY KEY NOT NULL, xp INT, level INT, nextlevel INT, background VARCHAR(30), time INT, total INT, name VARCHAR(50))""")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    author = message.author
    guild = message.guild

    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT xp, level, time, total FROM levels WHERE user =?", (author.id,))
        xplevel = await cursor.fetchone()

        if not xplevel:
            await cursor.execute("INSERT INTO levels VALUES (?,?,?,?,?,?,?,?)", (author.id, 0, 0, 100, None, int(time.time() + 60), 0, author.name))
            await bot.db.commit()
            return

        xp = xplevel[0]
        level = xplevel[1]
        level_time = xplevel[2]
        total = xplevel[3]

        if level_time >= int(time.time()):
            return

        num = random.randint(15, 25)
        await cursor.execute("UPDATE levels SET xp =?, total =?, time =?, name =? WHERE user =?", (xp+num, total+num, int(time.time()+60), author.name, author.id,))

        await cursor.execute("SELECT level, xp FROM levels WHERE user =?", (author.id,))
        xplevel = await cursor.fetchone()
        level = xplevel[0]
        xp = xplevel[1]

        goal = 5 * (level ** 2) + (50 * level) + 100 - xp

        if goal <= 0:
            g = 5 * ((level + 1) ** 2) + (50 * (level + 1)) + 100
            await cursor.execute("UPDATE levels SET xp =?, level =?, nextlevel =?  WHERE user =?", (0, level+1, g, author.id,))
            channel = bot.get_channel(1003708900148785223)

            await channel.send(f"{author.mention} has leveled up to level **{level+1}**!")
    await bot.db.commit()


bot.run(os.getenv("TOKEN"))