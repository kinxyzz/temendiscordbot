import discord
from database import Session
from models import UserScore

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