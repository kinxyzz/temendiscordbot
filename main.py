import discord
from discord.ext import commands
from database import Base, engine
import os
from dotenv import load_dotenv
from commands.inventory import check_inventory
from commands.aqwwiki import check_wiki
from commands.classes import class_info
from commands.tolong import tolong
from commands.badge import badge_count
from commands.rankinghelper import help_ranking

load_dotenv()

Base.metadata.create_all(bind=engine)

TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.tree.add_command(check_inventory)
bot.tree.add_command(check_wiki)
bot.tree.add_command(class_info)
bot.tree.add_command(tolong)
bot.tree.add_command(badge_count)
bot.tree.add_command(help_ranking)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await bot.tree.sync()
    print("Bot is ready!")

bot.run(TOKEN)
