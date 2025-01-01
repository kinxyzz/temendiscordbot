from discord import app_commands, Interaction
from discord.ui import  Modal, TextInput
import discord

created_channels = []

@app_commands.command(name="thanks", description="Thank helpers and close the current channel.")
async def thanks(interaction: Interaction, helpers: str):
    """Thank helpers and close the current channel."""
    restricted_channel_id = 1323978359180361818

    if interaction.channel.id == restricted_channel_id:
        await interaction.response.send_message("This command cannot be used in this channel.", ephemeral=True)
        return

    if interaction.channel.id in created_channels:
        print(helpers)
        helper_mentions = helpers.replace(',', '\n')
        embed = discord.Embed(
            title="Thanks",
            description=f"Request helper: {interaction.user.mention}\nHelper list:\n{helper_mentions}",
            color=discord.Color.green()
        )

        log_channel = interaction.guild.get_channel(1324023927902830642)
        if log_channel:
            await log_channel.send(embed=embed)
        await interaction.channel.delete(reason="Help request concluded.")
    else:
        await interaction.response.send_message("This command can only be used in a help request channel created from the form.", ephemeral=True)

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
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        created_channels.append(channel.id)

        helper_role = discord.utils.get(interaction.guild.roles, name="Helper")
        if helper_role:
            helper_mention = helper_role.mention
        else:
            helper_mention = "@Helper"
        print(created_channels)
        embed = discord.Embed(title="Help Request", description=f"Yow {helper_mention} Someone Need help\nAQW Username: {aqw_username}\nMap Name: {map_name}\nRoom Number: {room_number}\nServer: {server}\nDescription: {description}\n\nPlease wait for a helper to respond. dont forget to use the command **/thanks** and tag the helper to close the channel.", color=discord.Color.blue())
        await channel.send(embed=embed)

        await interaction.response.send_message(f"Your help request channel has been created: {channel.mention}", ephemeral=True)