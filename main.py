import discord
from discord.ext import commands
from database import Base, engine, Session
import os
from dotenv import load_dotenv
from commands.inventory import check_inventory
from commands.aqwwiki import check_wiki
from commands.classes import class_info
from commands.tolong import tolong
from commands.badge import badge_count
from commands.thanks import thanks, HelpRequestForm
from commands.rankinghelper import help_ranking
from models import UserScore

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
bot.tree.add_command(thanks)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get('custom_id')
        if custom_id == "request_help_button":
            await interaction.response.send_modal(HelpRequestForm())
        elif custom_id == "be_helper_button":
            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message("This action can only be performed in a server.", ephemeral=True)
                return
            
            role_name = "Helper"
            helper_role = discord.utils.get(guild.roles, name=role_name)

            if helper_role is None:
                await interaction.response.send_message(
                    f"Role `{role_name}` tidak ditemukan di server.",
                    ephemeral=True,
                )
                return

            try:
                await interaction.user.add_roles(helper_role)
                await interaction.response.send_message(
                    f"Selamat! Kamu sekarang menjadi seorang `{role_name}`.",
                    ephemeral=True,
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Bot tidak memiliki izin untuk menambahkan role ini.",
                    ephemeral=True,
                )
            except discord.HTTPException as e:
                await interaction.response.send_message(
                    f"Terjadi kesalahan saat menambahkan role: {e}",
                    ephemeral=True,
                )

        elif custom_id == "check_rank_button":
            try:
                await checkrank(interaction)
            except Exception as e:
                await interaction.response.send_message(
                    f"Terjadi kesalahan saat menjalankan command: {e}",
                    ephemeral=True,
                )
        
@bot.command(name="checkrank")
async def checkrank(interaction: discord.Interaction):
    try:
        with Session() as session:
            top_users = (
                session.query(UserScore)
                .order_by(UserScore.score.desc())
                .limit(10)
                .all()
            )

        embed = discord.Embed(title="Top 10 Helper Rankings", color=discord.Color.green())

        if top_users:
            for i, user_score in enumerate(top_users, 1):
                embed.add_field(
                    name=f"#{i} <@{user_score.userId}>",
                    value=f"Score: {user_score.score}",
                    inline=False,
                )
        else:
            embed.add_field(name="No Data", value="Belum ada data skor.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        print(f"Error saat menjalankan command: {e}")
        await interaction.response.send_message("Terjadi kesalahan saat mengambil data.", ephemeral=True)
    
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands with Discord.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
        
bot.run(TOKEN)


# class PermanentButtons(View):
#     def __init__(self):
#         super().__init__(timeout=None)
        
#         # Request Help button
#         self.add_item(Button(
#             style=discord.ButtonStyle.secondary,
#             label="Request Help",
#             custom_id="request_help_button",
#             emoji="<:kannapeer:1304352842731229194>",
#         ))
        
#         # Be Helper button
#         self.add_item(Button(
#             style=discord.ButtonStyle.secondary,
#             label="Be Helper",
#             custom_id="be_helper_button",
#             emoji="<:nicoheart:1304354892529401956>"
#         ))
        
#         # Check Rank button
#         self.add_item(Button(
#             style=discord.ButtonStyle.secondary,
#             label="Check Rank",
#             custom_id="check_rank_button",
#             emoji="<:swegdg:1305397803509485608>"
#         ))

# @bot.event
# async def on_ready():
#     print(f'Bot is ready as {bot.user}')
    
#     channel = await bot.fetch_channel(1323978359180361818)
#     message = await channel.fetch_message(1323984550019469346)
    
#     await message.edit(view=PermanentButtons())