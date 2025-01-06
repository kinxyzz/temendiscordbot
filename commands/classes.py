import requests
from discord import app_commands, Interaction, Embed

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
                    "note": None,
                }
            elif current_class and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key in class_data[current_class]:
                    class_data[current_class][key] = value
                elif key == "keywords":
                    class_data[current_class]["keywords"] = [
                        kw.strip().lower() for kw in value.split(",")
                    ]
                elif key == "note":
                    class_data[current_class]["note"] = value

        return class_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {}
    

@app_commands.command(name="classes", description="Get class information")
async def classes(interaction:Interaction, keyword: str):
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