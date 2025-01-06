import discord
from discord.ext import commands
from service.checkRank import checkrank
from commands.thanks import HelpRequestForm 

async def customInteraction(interaction: discord.Interaction):
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


async def on_ready_event(bot):
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands with Discord.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

