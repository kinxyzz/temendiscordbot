import discord  # type: ignore
from discord.ui import View  # type: ignore
from database import session, Base, engine
from models import UserScore
from models import UserScore
from discord.ui import View, Button
from discord import app_commands, Interaction, Embed, Color,ButtonStyle

class HelpRequestView(View):
    def __init__(
        self, requester: discord.Member, message: str, max_helpers: int = None
    ):
        super().__init__(timeout=None)
        self.requester = requester
        self.message = message
        self.max_helpers = max_helpers
        self.users_helping = []

    def update_message_content(self):
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
        return (
            f"{self.requester.mention}\nMeminta bantuan untuk\n**`{self.message}`**\n\n"
            f"{helper_count_text}\n{helper_text}"
        )

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
        updated_content = self.update_message_content()
        try:
            await interaction.response.edit_message(content=updated_content, view=self)
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
                "Permintaan telah dibatalkan oleh mu.", ephemeral=True
            )
            return

        if user.id in self.users_helping:
            self.users_helping.remove(user.id)
            updated_content = self.update_message_content()
            try:
                await interaction.response.edit_message(
                    content=updated_content, view=self
                )
                if not interaction.response.is_done():
                    await interaction.response.edit_message(
                        content=updated_content, view=self
                    )
                else:
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

    @discord.ui.button(
        label="Done", style=discord.ButtonStyle.green, custom_id="done_button"
    )
    async def done_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.requester:
            await interaction.response.send_message(
                "Biar yang minta bantuan yang klik!", ephemeral=True
            )
            return

        for uid in self.users_helping:
            user_score = session.query(UserScore).filter_by(userId=str(uid)).first()
            if user_score:
                user_score.score += 10
            else:
                new_score = UserScore(id=str(uid), userId=str(uid), score=10)
                session.add(new_score)

        session.commit()

        orang_baik_list = (
            "\n".join([f"<@{uid}> +10 point" for uid in self.users_helping]) or ""
        )

        final_content = (
            f"{self.requester.mention}\nTelah menyelesaikan:\n** `{self.message}`**\n"
            f"Bersama:\n{orang_baik_list}\n\n"
            "Terimakasih Puh!\n✅ Done!"
        )

        self.disable_buttons()
        try:
            await interaction.response.edit_message(content=final_content, view=None)
        except discord.HTTPException as e:
            print(f"Failed to update message: {e}")

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True
        self.stop()

@app_commands.command(name="tolong", description="Meminta bantuan dengan opsi maxhelper.")
async def tolong(interaction: Interaction, message: str, maxhelper: int = None):
    if maxhelper is not None and maxhelper < 1:
        await interaction.response.send_message(
            "Jumlah maksimum helper harus lebih dari 0.", ephemeral=True
        )
        return
    requester = interaction.user
    help_request = f"{requester.mention}\nMeminta bantuan sepuh untuk\n**`{message}`**"
    max_helper_text = f" \n`Butuh {maxhelper} orang`" if maxhelper else ""
    view = HelpRequestView(requester, message, maxhelper)
    try:
        await interaction.response.send_message(
            content=f"{help_request}\n\nMohon bantuannya!{max_helper_text}", view=view
        )
    except discord.HTTPException as e:
        print(f"Failed to send message: {e}")