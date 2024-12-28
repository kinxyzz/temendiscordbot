import discord # type: ignore
from discord.ext import commands # type: ignore
from discord.ui import View # type: ignore
from database import session, Base, engine
from models import UserScore
import os
from discord import Embed # type: ignore
from models import UserScore
import requests # type: ignore
from dotenv import load_dotenv # type: ignore
from accountInfo import AccountInfo

load_dotenv()

Base.metadata.create_all(bind=engine)

TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def load_class_data():
    class_data = {}
    url = "https://xyfkjeqsrrpzdfalimnb.supabase.co/storage/v1/object/public/temenstorage/class_data.txt?t=2024-12-27T14%3A10%3A47.853Z"

    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        current_class = None
        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current_class = line[1:-1].lower()
                class_data[current_class] = {
                    "ench_solo": None,
                    "ench_farm": None,
                    "ench_ultra": None,
                    "ench_nonforge": None,
                    "combo_solo": None,
                    "combo_multi_target": None,
                    "combo_full_damage": None,
                    "combo_defend": None,
                    "combo_dodge": None,
                    "combo_ultra": None,
                    "potion": None,
                    "keywords": [],
                    "note": None
                }
            elif current_class and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key in class_data[current_class]:
                    class_data[current_class][key] = value
                elif key == "keywords":
                    class_data[current_class]["keywords"] = [kw.strip().lower() for kw in value.split(",")]
                elif key == "note":
                    class_data[current_class]["note"] = value

        return class_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {}

class HelpRequestView(View):
    def __init__(self, requester: discord.Member, message: str, max_helpers: int = None):
        super().__init__(timeout=None)
        self.requester = requester
        self.message = message
        self.max_helpers = max_helpers
        self.users_helping = []

    def update_message_content(self):
        if self.max_helpers is not None:
            helper_list = [
                f"{i + 1}. <@{self.users_helping[i]}>" if i < len(self.users_helping) else f"{i + 1}."
                for i in range(self.max_helpers)
            ]
            helper_count_text = f"Sepuh yang bersedia ({len(self.users_helping)}/{self.max_helpers}):"
        else:
            helper_list = [
                f"{i + 1}. <@{uid}>" for i, uid in enumerate(self.users_helping)
            ]
            helper_count_text = "Sepuh yang bersedia:"
        helper_text = '\n'.join(helper_list) or "Belum ada yang membantu."
        return (
            f"{self.requester.mention}\nMeminta bantuan untuk\n**`{self.message}`**\n\n"
            f"{helper_count_text}\n{helper_text}"
        )

    @discord.ui.button(label="Ikut", style=discord.ButtonStyle.primary, custom_id="help_button")
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user == self.requester:
            await interaction.response.send_message("Kau kan yang minta bantuan!", ephemeral=True)
            return
        if user.id in self.users_helping:
            await interaction.response.send_message("Kau dah kedaftar!", ephemeral=True)
            return
        if self.max_helpers is not None and len(self.users_helping) >= self.max_helpers:
            await interaction.response.send_message(
                f"Jumlah helper sudah mencapai maksimum ({self.max_helpers}).",
                ephemeral=True
            )
            return
        self.users_helping.append(user.id)
        updated_content = self.update_message_content()
        try:
            await interaction.response.edit_message(content=updated_content, view=self)
        except discord.HTTPException as e:
            print(f"Failed to update message: {e}")

    @discord.ui.button(label="Gajadi", style=discord.ButtonStyle.danger, custom_id="cancel_help_button")
    async def cancel_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user == self.requester:
            await interaction.message.delete()
            await interaction.response.send_message(
                "Permintaan telah dibatalkan oleh mu.", 
                ephemeral=True
            )
            return

        if user.id in self.users_helping:
            self.users_helping.remove(user.id)
            updated_content = self.update_message_content()
            try:
                await interaction.response.edit_message(content=updated_content, view=self)
                if not interaction.response.is_done():
                         await interaction.response.edit_message(content=updated_content, view=self)
                else:
                        await interaction.followup.send(
                                 f"{user.mention}, kamu telah menghapus diri dari daftar bantuan.", 
                                 ephemeral=True
    )
            except discord.HTTPException as e:
                print(f"Gagal Update Pesan: {e}")
        else:
            await interaction.response.send_message(
                "Kamu tidak terdaftar dalam daftar bantuan.",
                ephemeral=True
            )

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green, custom_id="done_button")
    async def done_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.requester:
            await interaction.response.send_message("Biar yang minta bantuan yang klik!", ephemeral=True)
            return
    
        for uid in self.users_helping:
            user_score = session.query(UserScore).filter_by(userId=str(uid)).first()
            if user_score:
                user_score.score += 10  
            else:
                new_score = UserScore(id=str(uid), userId=str(uid), score=10)
                session.add(new_score)
        
        session.commit()

        orang_baik_list = '\n'.join([f"<@{uid}> +10 point" for uid in self.users_helping]) or ""
        
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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()
    print("Bot is ready!")

@bot.tree.command(name="badgecount", description="Fetch badge count and categorize by message")
async def badge_count(interaction: discord.Interaction, message: str):
   
    ccid = AccountInfo.get_ccid(message)

    if not ccid:
        embed = Embed(title="Badge Count", color=discord.Color.red())
        embed.add_field(name="IGN", value=message, inline=False)  
        embed.add_field(name="Error", value="Account tidak ditemukan dalam halaman.", inline=False)
        await interaction.response.send_message(embed=embed)
        return

    badges_data = AccountInfo.get_badges(ccid)

    if not badges_data:
        embed = Embed(title="Badge Count {message}", color=discord.Color.red())
        embed.add_field(name="IGN", value=message, inline=False)  
        embed.add_field(name="Error", value="Gagal mengambil data badge.", inline=False)
        await interaction.response.send_message(embed=embed)
        return

    categories = [
        "Legendary","Epic Hero", "Battle", "Support",
        "Exclusive", "Artix Entertainment"
    ]
    category_counts = {category: 0 for category in categories}

    # Hitung jumlah badge per kategori
    for badge in badges_data:
        category = badge.get("sCategory", "Unknown")
        if category in category_counts:
            category_counts[category] += 1

    # Hitung total badge
    total_badge_count = len(badges_data)

    # Membuat embed untuk menampilkan hasilnya
    embed = Embed(title=f"Badge Count {message}", color=discord.Color.green())
    embed.add_field(name="<:pepegimmle:1304354921902248007> Total Badges", value=f"{total_badge_count} badges ditemukan.", inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1226361685317783625/1322530781045985280/PicsArt_12-28-02.42.28.png?ex=67713645&is=676fe4c5&hm=ec43d5a48382fd56327fa56e63264de3556bf6b9cc5697334fa5d3bc9ebc2790&")
    # Menambahkan jumlah badge per kategori
    for category, count in category_counts.items():
        embed.add_field(name=category, value=f"{count} badges", inline=False)

    # Kirim embed sebagai respons
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="rankhelper", description="Get Information About Helper Ranking")
async def help_ranking(interaction: discord.Interaction):
    top_users = session.query(UserScore).order_by(UserScore.score.desc()).limit(10).all()
    embed = Embed(title="Top 10 Helper Rankings", color=discord.Color.green())

    if top_users:
        for i, user_score in enumerate(top_users, 1):
            embed.add_field(name=f"#{i} <@{user_score.userId}>", value=f"Score: {user_score.score}", inline=False)
    else:
        embed.add_field(name="No Data", value="Belum ada data skor.", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tolong", description="Meminta bantuan dengan opsi maxhelper.")
async def tolong(interaction: discord.Interaction, message: str, maxhelper: int = None):
    if maxhelper is not None and maxhelper < 1:
        await interaction.response.send_message(
            "Jumlah maksimum helper harus lebih dari 0.",
            ephemeral=True
        )
        return
    requester = interaction.user
    help_request = f"{requester.mention}\nMeminta bantuan sepuh untuk\n**`{message}`**"
    max_helper_text = f" \n`Butuh {maxhelper} orang`" if maxhelper else ""
    view = HelpRequestView(requester, message, maxhelper)
    try:
        await interaction.response.send_message(
            content=f"{help_request}\n\nMohon bantuannya!{max_helper_text}",
            view=view
        )
    except discord.HTTPException as e:
        print(f"Failed to send message: {e}")


@bot.tree.command(name="class", description="Get class information")
async def class_info(interaction: discord.Interaction, keyword: str):
    keyword = keyword.lower()
    class_data = load_class_data()
    matched_class = None
    for class_name, data in class_data.items():
        if keyword == class_name or keyword in data.get("keywords", []):
            matched_class = class_name
            break
    if matched_class:
        data = class_data[matched_class]
        embed = Embed(title=f"⚔︎ Info Class\n{matched_class.title()}")
        note_field = ""
        if data["note"]:
            note_field = f"{data['note']}\n"
        if note_field:
            embed.add_field(name="Note", value=note_field, inline=False)
        enchantment_field = ""
        if data["ench_nonforge"]:
            enchantment_field += f"- Non-Forge: `{data['ench_nonforge']}`\n"
        if data["ench_solo"]:
            enchantment_field += f"- Solo: `{data['ench_solo']}`\n"
        if data["ench_farm"]:
            enchantment_field += f"- Farm: `{data['ench_farm']}`\n"
        if data["ench_ultra"]:
            enchantment_field += f"- Ultra: `{data['ench_ultra']}`\n"
        if enchantment_field:
            embed.add_field(name="Enchantment", value=enchantment_field, inline=False)
        combo_field = ""
        if data["combo_solo"]:
            combo_field += f"- Solo: `{data['combo_solo']}`\n"
        if data["combo_multi_target"]:
            combo_field += f"- Multi Target: `{data['combo_multi_target']}`\n"
        if data["combo_full_damage"]:
            combo_field += f"- Damage: `{data['combo_full_damage']}`\n"
        if data["combo_defend"]:
            combo_field += f"- Defensive: `{data['combo_defend']}`\n"
        if data["combo_dodge"]:
            combo_field += f"- Dodge: `{data['combo_dodge']}`\n"
        if data["combo_ultra"]:
            combo_field += f"- Ultra: `{data['combo_ultra']}`\n"
        if combo_field:
            embed.add_field(name="Combo", value=combo_field, inline=False)
        potion_field = ""
        if data["potion"]:
            potion_field = f"{data['potion']}"
        if potion_field:
            embed.add_field(name="Potion", value=f"`{potion_field}`", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        custom_message = class_data.get("general", {}).get("custom_message", None)
        if custom_message:
            response = custom_message.format(keyword=keyword)
        else:
            response = f"Class {keyword} belum tersedia di dalam database.\n\nApakah Anda ingin mengajukan permintaan atau menjadi kontributor informasi class?\nSilakan kirim pesan langsung (DM) kepada pxnda. Terima kasih!"
        await interaction.response.send_message(response, ephemeral=True)

bot.run(TOKEN)
