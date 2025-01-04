from discord import app_commands, Interaction
from discord.ui import  Modal, TextInput, View, Button
import discord
from sqlalchemy.orm import Session
from database import engine
from sqlalchemy.dialects.postgresql import insert
from models import UserScore
from sqlalchemy.exc import SQLAlchemyError

requesters = []

def find_request_by_channel(channel_id):
    return next((req for req in requesters if req["channel_help_created_id"] == channel_id), None)

@app_commands.command(name="thanks", description="Thank helpers and close the current channel.")
async def thanks(interaction: Interaction):
    restricted_channel_id = 1323978359180361818
    if interaction.channel.id == restricted_channel_id:
        await interaction.response.send_message(
            "This command cannot be used in this channel.", ephemeral=True
        )
        return
    request = find_request_by_channel(interaction.channel.id)
    if not request:
        await interaction.response.send_message(
            "This command can only be used in a help request channel created from the form.",
            ephemeral=True
        )
        return
    if interaction.user.id != request["sender"]:
        await interaction.response.send_message(
            "You are not authorized to conclude this help request.",
            ephemeral=True
        )
        return
    if 'helpers' not in request or not request['helpers']:
        await interaction.response.send_message(
            "No helpers have joined this request yet!",
            ephemeral=True
        )
        return
    helper_mentions = "\n".join([f"<@{helper_id}>" for helper_id in request['helpers']])

    embed = discord.Embed(
        title="Thanks",
        description=f"Request helper: {interaction.user.mention}\nHelper list:\n{helper_mentions}",
        color=discord.Color.green()
    )

    try:
        with Session(engine) as session:
            data = [{"id": uid, "userId": uid, "score": 10} for uid in request['helpers']]
            stmt = insert(UserScore).values(data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["userId"],
                set_={"score": UserScore.score + 10}
            )
            session.execute(stmt)
            session.commit()

        log_channel = interaction.guild.get_channel(1324023927902830642)
        if log_channel:
            await log_channel.send(embed=embed)

        CHANNEL_ID_CHAT = interaction.guild.get_channel(request["channel_id_chat"])
        MESSAGE = await CHANNEL_ID_CHAT.fetch_message(request["message_id_chat"])
        await MESSAGE.edit(content=f"Permintaan Bantuan {interaction.user.name} telah terselesaikan!")

        await interaction.channel.delete(reason="Help request concluded.")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        await interaction.response.send_message(
            "An error occurred while processing the thanks.",
            ephemeral=True
        )

class HelpRequestForm(Modal):
    def __init__(self):
        super().__init__(title="Help Request Form")

        self.add_item(TextInput(
            label="AQW Username",
            placeholder="Enter your AQW username",
            max_length=100
        ))

        self.add_item(TextInput(
            label="Map Name",
            placeholder="Enter the map name",
            max_length=100
        ))

        self.add_item(TextInput(
            label="Room Number",
            placeholder="Enter the room number",
            max_length=100
        ))

        self.add_item(TextInput(
            label="Server",
            placeholder="Enter the server name",
            max_length=100
        ))

        self.add_item(TextInput(
            label="Description",
            placeholder="Describe your issue (max 4000 characters)",
            style=discord.TextStyle.long,
            max_length=4000
        ))

    async def on_submit(self, interaction: discord.Interaction):
        aqw_username = self.children[0].value
        map_name = self.children[1].value
        room_number = self.children[2].value
        server = self.children[3].value
        description = self.children[4].value

        channel_name = f"help-{aqw_username.lower()}"

        category = discord.utils.get(interaction.guild.categories, name="『 HELP REQUEST 』")

        if not category:
            await interaction.response.send_message("Category '『 HELP REQUEST 』' not found.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        helper_role = discord.utils.get(interaction.guild.roles, name="Helper")
        if helper_role:
            helper_mention = helper_role.mention
        else:
            helper_mention = "@Helper"
           
        embed = discord.Embed(title="Help Request", description=f"Yow {helper_mention} Someone Need help\nAQW Username: {aqw_username}\nMap Name: {map_name}\nRoom Number: {room_number}\nServer: {server}\nDescription: {description}\n\nPlease wait for a helper to respond. dont forget to use the command **/thanks** and tag the helper to close the channel.", color=discord.Color.blue())
        
        view = HelpRequestButtons(interaction.user.id, channel.id)

        CHANNEL_ID_CHAT = interaction.guild.get_channel(1188139654717902869)
        MESSAGE_IN_HELP_CHANNEL= await channel.send(embed=embed, view=view)
        MESSAGE_IN_ID_CHAT_CHANNEL = await CHANNEL_ID_CHAT.send(f"Temanmu membutuhkan bantuan di {map_name} ayo bantu {channel.mention}")
        requesters.append({
        "sender": interaction.user.id,
        "message_help_id": MESSAGE_IN_HELP_CHANNEL.id, 
        "channel_help_created_id": channel.id,
        "channel_id_chat" : CHANNEL_ID_CHAT.id,
        "message_id_chat" : MESSAGE_IN_ID_CHAT_CHANNEL.id
        })

        await interaction.response.send_message(f"Your help request channel has been created: {channel.mention}", ephemeral=True)

class HelpRequestButtons(View):
    def __init__(self, original_author_id: int, channel_id: int):
        super().__init__(timeout=None)
        self.original_author_id = original_author_id
        self.channel_id = channel_id
        
        self.cancel_btn = Button(
            style=discord.ButtonStyle.danger,
            label="Cancel",
            custom_id="cancel_help"
        )
        self.cancel_btn.callback = self.cancel_callback
        
        self.join_btn = Button(
            style=discord.ButtonStyle.primary,
            label="Join",
            custom_id="join_help"
        )
        self.join_btn.callback = self.join_callback
        
        # Add buttons to view
        self.add_item(self.cancel_btn)
        self.add_item(self.join_btn)
    
    async def cancel_callback(self, interaction: Interaction):
        if interaction.user.id != self.original_author_id:
            await interaction.response.send_message(
                "Only the help request author can cancel this request.",
                ephemeral=True
            )
            return
        request = find_request_by_channel(self.channel_id)
        CHANNEL_ID_CHAT = interaction.guild.get_channel(request["channel_id_chat"])
        MESSAGE = await CHANNEL_ID_CHAT.fetch_message(request["message_id_chat"])
        await MESSAGE.edit(content=f"Permintaan Bantuan {interaction.user.name} telah dibatalkan")
        await interaction.channel.delete(reason="Help request cancelled by author.")

    async def join_callback(self, interaction: Interaction):
        request = find_request_by_channel(self.channel_id)
        if not request:
            await interaction.response.send_message(
                "Error: Could not find the help request data.",
                ephemeral=True
            )
            return

        if interaction.user.id == self.original_author_id:
            await interaction.response.send_message("You cannot join your own help request.", ephemeral=True)
            return

        if 'helpers' not in request:
            request['helpers'] = set()
            
        if interaction.user.id in request['helpers']:
            await interaction.response.send_message("You've already joined as a helper!", ephemeral=True)
            return
            
        request['helpers'].add(interaction.user.id)
        
        helper_mentions = " ".join([f"<@{helper_id}>" for helper_id in request['helpers']])
        
        embed = interaction.message.embeds[0]
        helpers_field_index = next((i for i, field in enumerate(embed.fields) if field.name == "Helpers"), None)
        
        if helpers_field_index is not None:
            embed.set_field_at(helpers_field_index, name="Helpers", value=helper_mentions, inline=False)
        else:
            embed.add_field(name="Helpers", value=helper_mentions, inline=False)
        
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("You joined as a helper!", ephemeral=True)