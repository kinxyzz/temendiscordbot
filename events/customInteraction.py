import discord
from discord.ext import commands
from service.checkRank import checkrank
from commands.thanks import HelpRequestForm 
from discord.ui import TextInput, Modal
import re
from sqlalchemy.orm import Session
from database import engine
from sqlalchemy.dialects.postgresql import insert
from models import UserScore, LogHelper
from datetime import datetime
from repository.userScoreRepo import UserScoreRepository

async def customInteraction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get('custom_id', '')
        
     
        if custom_id and custom_id.startswith('done_button_'):
            requester_id = int(custom_id.split('_')[-1])
            
        
            message = interaction.message
            if not message:
                return

      
            if interaction.user.id != requester_id:
                await interaction.response.send_message(
                    "Biar yang minta bantuan yang klik!", 
                    ephemeral=True
                )
                return

      
            view = discord.ui.View()
            for component in message.components:
                for child in component.children:
                    button = discord.ui.Button(
                        style=child.style,
                        label=child.label,
                        custom_id=child.custom_id,
                        disabled=True
                    )
                    view.add_item(button)

     
            await message.edit(view=view)

            helper_ids = []
            
            original_message = None
            if message.embeds:
                embed = message.embeds[0]
            
                description = embed.description
                if description:
                    original_message = description.split('**`')[1].split('`**')[0]
            
                for field in embed.fields:
                    if "Sepuh yang bersedia" in field.name:
                        mentions = re.findall(r'<@(\d+)>', field.value)
                        helper_ids = [int(uid) for uid in mentions]
                        break

            orang_baik_list = "\n".join([f"<@{uid}> +10" for uid in helper_ids])

            if(helper_ids == []):
                await interaction.response.send_message(
                    "Sepuh yang bersedia masih kosong!", 
                  
                )
                await message.delete()
                return

            embed = discord.Embed(
                title="Bantuan Selesai ✅",
                description=(
                    f"<@{requester_id}>\ntelah menyelesaikan:\n"
                    f"**`{original_message}`**\n\n"
                    f"**Bersama:**\n{orang_baik_list}\n\n"
                    "Terima kasih, Puh! 🙏"
                ),
                color=discord.Color.from_rgb(44, 47, 51)
            )
            
            embed.set_footer(
                text="Temen Assistant",
                icon_url="https://cdn.discordapp.com/attachments/1226361685317783625/1325452313258758185/temen.png?ex=677bd729&is=677a85a9&hm=4a3f5affb1a1d7d1945f2c257ebc1c75f0721e340002a98fce17f8a"
            )
            
            try:
                if helper_ids:
                    with Session(engine) as session:
                        userScoreRepo = UserScoreRepository(session)
                        user_score_data = [
                            {
                                "id": uid,
                                "userId": uid,
                                "score": 10,
                                "nickname": interaction.guild.get_member(int(uid)).nick.split("|")[1].strip(),
                                "ultra_score": 0
                            }
                            for uid in helper_ids
                        ]
                        userScoreRepo.insert_or_update_user_scores(user_score_data)
               
                            
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_id = f"{requester_id}_{timestamp}"

                        log_helper_data = ({
                            "id": unique_id,
                            "userId": requester_id,
                            "timestamp": datetime.now()
                        })
                        
                        stmt_log_helper = insert(LogHelper).values(log_helper_data)
                        session.execute(stmt_log_helper)

                     
                        session.commit()
                    log_channel = interaction.guild.get_channel(1324023927902830642)
                    if log_channel:
                        await log_channel.send(embed=embed)
                await interaction.response.send_message(embed=embed)
                await message.delete()
            except discord.HTTPException as e:
                print(f"Failed to update message: {e}")
        
        elif custom_id == "request_help_button":
            await interaction.response.send_modal(HelpRequestForm())
        
        elif custom_id == "be_helper_button":
            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message("This action can only be performed in a server.", ephemeral=True)
                return
            
            role_name = "Helper"
            helper_role = discord.utils.get(guild.roles, name=role_name)

            if helper_role is None:
                await interaction.response.send_message(
                    f"Role `{role_name}` tidak ditemukan di server.",
                    ephemeral=True,
                )
                return

            try:
                await interaction.user.add_roles(helper_role)
                await interaction.response.send_message(
                    f"Selamat! Kamu sekarang menjadi seorang `{role_name}`.",
                    ephemeral=True,
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Bot tidak memiliki izin untuk menambahkan role ini.",
                    ephemeral=True,
                )
            except discord.HTTPException as e:
                await interaction.response.send_message(
                    f"Terjadi kesalahan saat menambahkan role: {e}",
                    ephemeral=True,
                )

        elif custom_id == "check_rank_button":
            try:
                await checkrank(interaction)
            except Exception as e:
                await interaction.response.send_message(
                    f"Terjadi kesalahan saat menjalankan command: {e}",
                    ephemeral=True,
                )

        elif custom_id.startswith("set_role_"):
            role_name = custom_id.replace("set_role_", "")
            role = discord.utils.get(interaction.guild.roles, name=role_name.replace("_", " "))
            
            if role:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(f"Role {role.name} telah dihapus!", ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"Role {role.name} telah ditambahkan!", ephemeral=True)
            else:
                await interaction.response.send_message(f"Role {role_name} tidak ditemukan!", ephemeral=True)
        
        elif custom_id == "temen_verification":
              try:
                  await interaction.response.send_modal(VerificationForm())
              except Exception as e:
                  await interaction.response.send_message(
                      f"Terjadi kesalahan saat menjalankan command: {e}",
                      ephemeral=True,
                  )


# async def on_ready_event(bot: commands.Bot):
#     try:
#         channel = await bot.fetch_channel(1333459281877401670)
#         message = await channel.fetch_message(1335681579099488310)
        
#         view = discord.ui.View(timeout=None)
        
    
#         view.add_item(discord.ui.Button(label="Maniak Ultra", emoji="<:sword:1322665752544804954>", custom_id="set_role_Maniak_Ultra"))
#         view.add_item(discord.ui.Button(label="Atlet Set", emoji="<:armor:1322636616279523410>", custom_id="set_role_Atlet_Set",))
#         view.add_item(discord.ui.Button(label="Preman PVP", emoji="<:sigma:1296717173804498975>", custom_id="set_role_Preman_PVP"))
#         view.add_item(discord.ui.Button(label="Petani Ulung", emoji="<:deathnote:1304352853019852841>", custom_id="set_role_Petani_Ulung"))
        
#         await message.edit(view=view)
#         bot.add_view(view)
#         print("Button roles telah siap!")
#         await bot.tree.sync()
        
#     except Exception as e:
#         print(f"Error: {str(e)}")


async def on_ready_event(bot : commands.Bot):
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Failed to sync commands: {e}")

class VerificationForm(Modal):
    def __init__(self):
        super().__init__(title="Verification Form")

        self.add_item(TextInput(
            label="Nickname",
            placeholder="Enter your Nickname like mahmud, Rusdi, etc",
            max_length=100
        ))

        self.add_item(TextInput(
            label="Aqw Username",
            placeholder="Enter your Aqw Username",
            max_length=100
        ))

    async def on_submit(self, interaction: discord.Interaction):
        uname = self.children[0].value
        aqwUsername = self.children[1].value
        new_nickname = f"{uname} | {aqwUsername}"
        role_name = "Orang Keren"
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role is not None:
            try:
                await interaction.user.edit(nick=new_nickname)
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Terimakasih telah melakukan verifikasi, nickname kamu sekarang: `{new_nickname}` dan kamu telah diberi role `{role_name}`.",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Bot tidak memiliki izin untuk mengubah nickname atau menambahkan role.",
                    ephemeral=True
                )
            except discord.HTTPException as e:
                await interaction.response.send_message(
                    f"Terjadi kesalahan saat memperbarui nickname atau role: {e}",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                f"Role `{role_name}` tidak ditemukan di server.",
                ephemeral=True
            )