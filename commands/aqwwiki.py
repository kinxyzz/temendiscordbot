import discord
from discord import app_commands, Interaction, Embed, Color
from discord.ui import Select, View
from service.wikiinfo import AQWWikiScraper
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

def extract_embed_content(content):
    # Split content into lines
    lines = content.split('\n')
    
    # Define markers
    start_marker = "**Location:**"
    end_marker = "Male"

    # Find the start index
    start_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(start_marker):
            start_index = i
            break

    # Find the end index
    end_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(end_marker):
            end_index = i
            break

    # Extract content between the start and end markers
    if start_index != -1 and end_index != -1:
        extracted_lines = lines[start_index:end_index]
        return "\n".join(extracted_lines).strip()
    else:
        return ""

@app_commands.command(name="wiki", description="Check AQW Wiki")
async def check_wiki(interaction: Interaction, item: str):
    try:
        wiki_results = AQWWikiScraper.get_list_search(item)
        
        if not wiki_results:
            embed = Embed(
                title="Pencarian Wiki",
                description=f"Tidak ditemukan hasil untuk **{item}**.",
                color=Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = Embed(
            title=f"{item}",
            url=f"{os.environ.get('wikiurl')}/{item.replace(' ', '-')}",
            description=f"{item} usually refers to:",
            color=Color.blue()
        )

        for i, result in enumerate(wiki_results, start=1):
            embed.add_field(
                name=f"{i}.",
                value=f"[{result['text']}]({os.environ.get('wikiurl')}{result['href']})",
                inline=False,
            )

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
                title=f"{selected_item['text']}",
                url=f"{os.environ.get('wikiurl')}{selected_item['href']}",
                description=f"Informasi lebih lanjut tentang {selected_item['text']}\nas",
                color=Color.green()
            )
            embed.add_field(
                name="Link",
                value=f"Malasss Manual",
                inline=False
            )
            await interaction.response.send_message(embed=embed)

        select.callback = select_callback

        view = View()
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view)

    except Exception as e:
        
        embed = Embed(
            title="Error",
            description=f"Terjadi kesalahan saat memproses pencarian: {str(e)}",
            color=Color.red()
        )
        await interaction.response.send_message(embed=embed)
