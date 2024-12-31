import discord
from discord import app_commands, Interaction, Embed, Color,ButtonStyle
from service.accountInfo import AccountInfo
import requests  # type: ignore
from discord.ui import View, Button
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

class InventoryPaginator(View):
    def __init__(self, pages, embed_title, ign, type_name, interaction, timeout=120):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0
        self.embed_title = embed_title
        self.ign = ign
        self.type_name = type_name
        self.interaction = interaction
        self.previous_page.disabled = True
        self.next_page.disabled = len(self.pages) <= 1

    def generate_embed(self):
        embed = Embed(
            title=self.embed_title,
            color=Color.green(),
        )
        embed.add_field(name="IGN", value=self.ign, inline=False)
        embed.add_field(name="Type", value=self.type_name.capitalize(), inline=False)
        embed.add_field(
            name=f"Page {self.current_page + 1}/{len(self.pages)}",
            value=self.pages[self.current_page],
            inline=False,
        )
        return embed

    def update_buttons_state(self):
        """Update the state of the navigation buttons based on the current page."""
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.pages) - 1

    @discord.ui.button(label="◀️", style=ButtonStyle.secondary)
    async def previous_page(self, interaction: Interaction, button: Button):
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("You cannot interact with this message.", ephemeral=True)

        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons_state()  # Update buttons' states
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("You cannot interact with this message.", ephemeral=True)

        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_buttons_state()  # Update buttons' states
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)

choose_options = [
    app_commands.Choice(name="Class", value="Class"),
    app_commands.Choice(name="Armor", value="Armor"),
    app_commands.Choice(name="Helm", value="Helm"),
    app_commands.Choice(name="Cape", value="Cape"),
    app_commands.Choice(name="Polearm", value="Polearm"),
    app_commands.Choice(name="Sword", value="Sword"),
    app_commands.Choice(name="Dagger", value="Dagger"),
    app_commands.Choice(name="Axe", value="Axe"),
    app_commands.Choice(name="Staff", value="Staff"),
    app_commands.Choice(name="Pet", value="Pet"),
    app_commands.Choice(name="Item", value="Item"),
    app_commands.Choice(name="Quest Item", value="Quest Item"),
    app_commands.Choice(name="Resource", value="Resource"),
]

@app_commands.command(name="checkinvent", description="Check inventory by IGN and type")
@app_commands.describe(ign="Enter the IGN", choose="Choose the type")
@app_commands.choices(choose=choose_options)
async def check_inventory(interaction: Interaction, ign: str, choose: app_commands.Choice[str]):
    ccid = AccountInfo.get_ccid(ign)
    if not ccid:
        embed = Embed(title="Error", color= Color.red())
        embed.add_field(name="IGN", value=ign, inline=False)
        embed.add_field(
            name="Error", value="CCID tidak ditemukan untuk IGN ini.", inline=False
        )
        await interaction.response.send_message(embed=embed)
        return

    inventory_url = f"{os.environ.get('charpageurl')}/Inventory?ccid={ccid}"
    try:
        response = requests.get(inventory_url)
        response.raise_for_status()
        inventory_data = response.json()

        filtered_items = [
            item for item in inventory_data if item["strType"].lower() == choose.value.lower()
        ]

        if not filtered_items:
            embed = Embed(title="Inventory Check", color=Color.orange())
            embed.add_field(name="IGN", value=ign, inline=False)
            embed.add_field(name="Type", value=choose.value.capitalize(), inline=False)
            embed.add_field(
                name="Result",
                value="Tidak ada item yang ditemukan untuk tipe ini.",
                inline=False,
            )
            await interaction.response.send_message(embed=embed)
            return
        
        icon_map = {
            "sword": "<:sword:1322665752544804954>",
            "armor": "<:armor:1322636616279523410>",
            "class": "<:class:1322636323114319922>",
            "cape" : "<:cape:1322636637645308004>",
            "helm": "<:helm:1322665725550395484>",
            "item": "<:misc:1322636897494761563>",
            "quest item": "<:misc:1322636897494761563>",
            "resource": "<:misc:1322636897494761563>",
        }

        icon = icon_map.get(choose.value.lower(), "<:misc:1322636897494761563>")

        valid_items = [
            f"{icon} {item['strName']} {item['intCount'] if choose.value.lower() in ['item', 'quest item', 'resource'] else ''} {('<:acs:1322635091230462005>' if item['bCoins'] else '')} {('<:legend:1322635134352097361>' if item['bUpgrade'] else '')}"
            for item in filtered_items if item['strName']
        ]

        pages = []
        current_chunk = ""
        for item in valid_items:
            if len(current_chunk) + len(item) + 1 > 1024:
                pages.append(current_chunk.strip())
                current_chunk = f"{item}\n"
            else:
                current_chunk += f"{item}\n"

        if current_chunk.strip():
            pages.append(current_chunk.strip())

        if len(pages) == 1:
            # Jika hanya ada satu halaman, kirim embed tanpa view
            embed = Embed(
                title="Inventory Check",
                color=Color.green(),
            )
            embed.add_field(name="IGN", value=ign, inline=False)
            embed.add_field(name="Type", value=choose.value.capitalize(), inline=False)
            embed.add_field(name="Items", value=pages[0], inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            # Jika lebih dari satu halaman, kirim embed dengan view
            view = InventoryPaginator(pages, "Inventory Check", ign, choose.value, interaction)
            await interaction.response.send_message(embed=view.generate_embed(), view=view)

    except requests.RequestException as e:
        embed = Embed(title="Error", color=Color.red())
        embed.add_field(name="Error", value=f"Gagal mengambil data: {str(e)}", inline=False)
        await interaction.response.send_message(embed=embed)
