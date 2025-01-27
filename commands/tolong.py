import discord  # type: ignore
from discord.ui import View  # type: ignore
from discord.ui import View, Button
from discord import app_commands, Interaction, Embed, Color,ButtonStyle
from datetime import datetime, timedelta
from database import Session
from models import LogHelper


class HelpRequestView(View):
    def __init__(
        self, requester: discord.Member, message: str, max_helpers: int = None
    ):
        super().__init__(timeout=None)
        self.requester = requester
        self.message = message
        self.max_helpers = max_helpers
        self.users_helping = []
    

        done_button = discord.ui.Button(
            label="Done", 
            style=discord.ButtonStyle.green, 
            custom_id=f"done_button_{self.requester.id}"
        )
        self.add_item(done_button)

    def update_message_embed(self):
        embed = discord.Embed(
            title="Permintaan Bantuan",
            description=f"{self.requester.mention} meminta bantuan untuk:\n**`{self.message}`**",
            color=discord.Color.blue(),
        )

        if self.max_helpers is not None:
            helper_list = [
                (
                    f"{i + 1}. <@{self.users_helping[i]}>"
                    if i < len(self.users_helping)
                    else f"{i + 1}."
                )
                for i in range(self.max_helpers)
            ]
            helper_count_text = (
                f"Sepuh yang bersedia ({len(self.users_helping)}/{self.max_helpers}):"
            )
        else:
            helper_list = [
                f"{i + 1}. <@{uid}>" for i, uid in enumerate(self.users_helping)
            ]
            helper_count_text = "Sepuh yang bersedia:"

        helper_text = "\n".join(helper_list) or "Belum ada yang membantu."

        embed.add_field(name=helper_count_text, value=helper_text, inline=False)
        embed.set_footer(text="Temen Assistant", icon_url="https://cdn.discordapp.com/attachments/1226361685317783625/1325452313258758185/temen.png?ex=677bd729&is=677a85a9&hm=4a3f5affb1a1d7d1945f2c257ebc1c75f0721e340002a98fce17f8a")
        embed.set_author(name=self.requester.name, icon_url=self.requester.avatar.url)

        return embed

    @discord.ui.button(
        label="Ikut", style=discord.ButtonStyle.primary, custom_id="help_button"
    )
    async def help_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        user = interaction.user
        if user == self.requester:
            await interaction.response.send_message(
                "Kau kan yang minta bantuan!", ephemeral=True
            )
            return
        if user.id in self.users_helping:
            await interaction.response.send_message("Kau dah kedaftar!", ephemeral=True)
            return
        if self.max_helpers is not None and len(self.users_helping) >= self.max_helpers:
            await interaction.response.send_message(
                f"Jumlah helper sudah mencapai maksimum ({self.max_helpers}).",
                ephemeral=True,
            )
            return

        self.users_helping.append(user.id)
        updated_embed = self.update_message_embed()

        try:
            await interaction.response.edit_message(embed=updated_embed, view=self)
        except discord.HTTPException as e:
            print(f"Failed to update message: {e}")

    @discord.ui.button(
        label="Gajadi", style=discord.ButtonStyle.danger, custom_id="cancel_help_button"
    )
    async def cancel_help_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        user = interaction.user

        if user == self.requester:
            await interaction.message.delete()
            await interaction.response.send_message(
                "Permintaan telah dibatalkan olehmu.", ephemeral=True
            )
            return

        if user.id in self.users_helping:
            self.users_helping.remove(user.id)
            updated_embed = self.update_message_embed()
            try:
                await interaction.response.edit_message(embed=updated_embed, view=self)
                await interaction.followup.send(
                    f"{user.mention}, kamu telah menghapus diri dari daftar bantuan.",
                    ephemeral=True,
                )
            except discord.HTTPException as e:
                print(f"Gagal Update Pesan: {e}")
        else:
            await interaction.response.send_message(
                "Kamu tidak terdaftar dalam daftar bantuan.", ephemeral=True
            )

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True
        self.stop()

@app_commands.command(name="tolong", description="Meminta bantuan dengan opsi maxhelper.")
async def tolong(interaction: Interaction, message: str, maxhelper: int = None):
    if maxhelper is not None:
        if maxhelper < 1:
            await interaction.response.send_message(
                "Jumlah maksimum helper harus lebih dari 0.", ephemeral=True
            )
            return
        elif maxhelper > 20:
            await interaction.response.send_message(
                "Jumlah maksimum helper tidak boleh lebih dari 20.", ephemeral=True
            )
            return
    
    requester = interaction.user
    print(requester)
    with Session() as session:
        print(requester.id)
        user_id_to_filter = str(requester.id)
        latest_log = (
            session.query(LogHelper)
            .filter(LogHelper.userId == user_id_to_filter) 
            .order_by(LogHelper.timestamp.desc())
            .first()
        )

        if latest_log:
            print(latest_log.timestamp)
            current_time = datetime.now()
            time_difference = current_time - latest_log.timestamp
            print(current_time)
            print(time_difference)

            if time_difference < timedelta(hours=1):
                remaining_time = timedelta(hours=1) - time_difference
                remaining_minutes = int(remaining_time.total_seconds() // 60)
                await interaction.response.send_message(
                    f"Maaf, Anda bisa meminta bantuan lagi setelah {remaining_minutes} menit.",
                    ephemeral=True,
                )
                return

    embed = discord.Embed(
        title="Permintaan Bantuan",
        description=f"{requester.mention} meminta bantuan untuk:\n**`{message}`**",
        color=discord.Color.blue(),
    )

    if maxhelper:
        embed.add_field(name="Jumlah Maksimum Helper", value=f"{maxhelper} orang", inline=False)

    embed.set_footer(text="Temen Assistant", 
                     icon_url="https://cdn.discordapp.com/attachments/1226361685317783625/1325452313258758185/temen.png?ex=677bd729&is=677a85a9&hm=4a3f5affb1a1d7d1945f2c257ebc1c75f0721e340002a98fce17f8a")
    embed.set_author(name=requester.name, icon_url=requester.avatar.url)

    view = HelpRequestView( requester, message, maxhelper)

    try:
        message = await interaction.response.send_message(embed=embed, view=view)
    except discord.HTTPException as e:
        print(f"Failed to send message: {e}")
