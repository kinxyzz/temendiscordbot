import discord
from discord import app_commands
from typing import List


@app_commands.command(name="sendmessage", description="Kirim Pesan Secara anonym")
@app_commands.describe(
    message="Pesan yang akan dikirim",
    category="Pilih category channel",
    channel_id="Pilih channel untuk mengirim pesan"
)
async def sendmessage(
    interaction: discord.Interaction,
    message: str,
    category: discord.CategoryChannel,
    channel_id: str
):
    try:
        channel = interaction.guild.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message(
                "Channel tidak ditemukan!",
                ephemeral=True
            )
            return
      
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Anda tidak memiliki izin untuk menggunakan perintah ini.", 
                ephemeral=True
            )
            return

        await channel.send(message)
        await interaction.response.send_message(
            f"Pesan berhasil dikirim ke channel {channel.mention}!",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Saya tidak memiliki izin untuk mengirim pesan ke channel tersebut.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Terjadi kesalahan: {str(e)}",
            ephemeral=True
        )

@sendmessage.autocomplete('channel_id')
async def channel_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    category_option = None
    for option in interaction.data.get('options', []):
        if option['name'] == 'category':
            category_option = option
            break
    
    if not category_option:
        return []

    try:
        category = await interaction.guild.fetch_channel(int(category_option['value']))
        channels = [
            channel for channel in category.channels 
            if isinstance(channel, discord.TextChannel) and 
            current.lower() in channel.name.lower()
        ]
        
        return [
            app_commands.Choice(name=channel.name, value=str(channel.id))
            for channel in channels[:25]
        ]
    except Exception:
        return []