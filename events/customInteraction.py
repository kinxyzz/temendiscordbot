import discord
from discord.ext import commands
from service.checkRank import checkrank
from commands.thanks import HelpRequestForm 
from discord.ui import Button, View, TextInput, Modal

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

        elif custom_id == "temen_verification":
              try:
                  await interaction.response.send_modal(VerificationForm())
              except Exception as e:
                  await interaction.response.send_message(
                      f"Terjadi kesalahan saat menjalankan command: {e}",
                      ephemeral=True,
                  )


async def on_ready_event(bot : commands.Bot):
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Failed to sync commands: {e}")

class VerificationForm(Modal):
    def __init__(self):
        super().__init__(title="Verification Form")

        self.add_item(TextInput(
            label="Nickname",
            placeholder="Enter your Nickname like mahmud, Rusdi, etc",
            max_length=100
        ))

        self.add_item(TextInput(
            label="Aqw Username",
            placeholder="Enter your Aqw Username",
            max_length=100
        ))

    async def on_submit(self, interaction: discord.Interaction):
        uname = self.children[0].value
        aqwUsername = self.children[1].value
        new_nickname = f"{uname} | {aqwUsername}"
        role_name = "Orang Keren"
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role is not None:
            try:
                await interaction.user.edit(nick=new_nickname)
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Terimakasih telah melakukan verifikasi, nickname kamu sekarang: `{new_nickname}` dan kamu telah diberi role `{role_name}`.",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Bot tidak memiliki izin untuk mengubah nickname atau menambahkan role.",
                    ephemeral=True
                )
            except discord.HTTPException as e:
                await interaction.response.send_message(
                    f"Terjadi kesalahan saat memperbarui nickname atau role: {e}",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                f"Role `{role_name}` tidak ditemukan di server.",
                ephemeral=True
            )