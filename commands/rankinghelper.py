from discord import app_commands, Interaction, Embed, Color
from database import Session
from models import UserScore

@app_commands.command(name="rankhelper", description="Get Information About Helper Ranking")
async def help_ranking(interaction: Interaction):
    try:
        # Menggunakan context manager untuk sesi
        with Session() as session:
            top_users = (
                session.query(UserScore)
                .order_by(UserScore.score.desc())
                .limit(10)
                .all()
            )

        embed = Embed(title="Top 10 Helper Rankings", color=Color.green())

        if top_users:
            for i, user_score in enumerate(top_users, 1):
                embed.add_field(
                    name=f"#{i} <@{user_score.userId}>",
                    value=f"Score: {user_score.score}",
                    inline=False,
                )
        else:
            embed.add_field(name="No Data", value="Belum ada data skor.", inline=False)

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error saat menjalankan command: {e}")
        await interaction.response.send_message("Terjadi kesalahan saat mengambil data.", ephemeral=True)