import discord
from discord import app_commands, Interaction, Embed, Color
from discord.ui import Select, View
from service.wikiinfo import AQWWikiScraper
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

@app_commands.command(name="wiki", description="Check AQW Wiki")
async def check_wiki(interaction: Interaction, item: str):
    """
    Command untuk mencari item di AQW Wiki dan menampilkan hasil dalam format embed.
    """
    try:
        # Mengambil hasil pencarian dari AQWWikiScraper
        wiki_results = AQWWikiScraper.get_list_search(item)
        
        # Jika tidak ada hasil
        if not wiki_results:
            embed = Embed(
                title="Pencarian Wiki",
                description=f"Tidak ditemukan hasil untuk **{item}**.",
                color=Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        # Membuat embed untuk hasil pencarian
        embed = Embed(
            title=f"{item}",
            url=f"{os.environ.get('wikiurl')}/{item.replace(' ', '-')}",
            description=f"{item} usually refers to:",
            color=Color.blue()
        )

        # Menambahkan hasil pencarian ke embed
        for i, result in enumerate(wiki_results, start=1):
            embed.add_field(
                name=f"{i}.",
                value=f"[{result['text']}]({os.environ.get('wikiurl')}{result['href']})",
                inline=False,
            )

        # Membuat Select menu untuk memilih item
        select = Select(
            placeholder="Pilih item dari hasil pencarian",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=result['text'], value=str(i)) 
                for i, result in enumerate(wiki_results, start=1)
            ]
        )
        
        async def select_callback(interaction: Interaction):
            selected_index = int(select.values[0]) - 1 
            selected_item = wiki_results[selected_index]
            
            embed = Embed(
                title="Aku Lagi Malas",
                description=f"Informasi lebih lanjut tentang {selected_item['text']}:\n\n{selected_item['text']}",
                color=Color.green()
            )
            embed.add_field(
                name="Link",
                value=f"[Klik disini untuk membuka halaman wiki]({selected_item['href']})",
                inline=False
            )
            await interaction.response.send_message(embed=embed)

        select.callback = select_callback

        view = View()
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view)

    except Exception as e:
        # Error handling
        embed = Embed(
            title="Error",
            description=f"Terjadi kesalahan saat memproses pencarian: {str(e)}",
            color=Color.red()
        )
        await interaction.response.send_message(embed=embed)
