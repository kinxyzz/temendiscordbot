from discord import app_commands, Interaction, Embed, Color
from service.accountInfo import AccountInfo


@app_commands.command(
    name="badgecount", description="Fetch badge count and categorize by message"
)
async def badge_count(interaction: Interaction, message: str):

    ccid = AccountInfo.get_ccid(message)

    if not ccid:
        embed = Embed(title="Badge Count", color=Color.red())
        embed.add_field(name="IGN", value=message, inline=False)
        embed.add_field(
            name="Error", value="Account tidak ditemukan dalam halaman.", inline=False
        )
        await interaction.response.send_message(embed=embed)
        return

    badges_data = AccountInfo.get_badges(ccid)

    if not badges_data:
        embed = Embed(title="Badge Count {message}", color=Color.red())
        embed.add_field(name="IGN", value=message, inline=False)
        embed.add_field(name="Error", value="Gagal mengambil data badge.", inline=False)
        await interaction.response.send_message(embed=embed)
        return

    categories = [
        "Legendary",
        "Epic Hero",
        "Battle",
        "Support",
        "Exclusive",
        "Artix Entertainment",
        "HeroMart",
    ]
    category_counts = {category: 0 for category in categories}

    for badge in badges_data:
        category = badge.get("sCategory", "Unknown")
        if category in category_counts:
            category_counts[category] += 1

    total_badge_count = len(badges_data)

    embed = Embed(title=f"Badge Count {message}", color=Color.green())
    embed.add_field(
        name="<:pepegimmle:1304354921902248007> Total Badges",
        value=f"{total_badge_count} badges ditemukan.",
        inline=False,
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1226361685317783625/1322530781045985280/PicsArt_12-28-02.42.28.png?ex=67713645&is=676fe4c5&hm=ec43d5a48382fd56327fa56e63264de3556bf6b9cc5697334fa5d3bc9ebc2790&"
    )

    for category, count in category_counts.items():
        embed.add_field(name=category, value=f"{count} badges", inline=False)

    await interaction.response.send_message(embed=embed)
