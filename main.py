import discord
from discord.ext import commands
from database import Base, engine, Session
import os
import importlib
from pathlib import Path
from dotenv import load_dotenv
from events.customInteraction import customInteraction, on_ready_event

load_dotenv()

Base.metadata.create_all(bind=engine)

TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
commands_dir = Path("commands")
print(commands_dir)
for file in commands_dir.glob("*.py"):
    if file.name == "__init__.py":
        continue
    command_name = file.stem
    try:
        module = importlib.import_module(f"commands.{command_name}")
        command = getattr(module, command_name)
        bot.tree.add_command(command)
        print(f"Command '{command_name}' berhasil diload.")
    except (ImportError, AttributeError) as e:
        print(f"Error saat meload command '{command_name}': {e}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    await customInteraction(interaction)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong")


@bot.event
async def on_ready():
    await on_ready_event(bot)
        
bot.run(TOKEN)