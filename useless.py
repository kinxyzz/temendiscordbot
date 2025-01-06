# class PermanentButtons(View):
#     def __init__(self):
#         super().__init__(timeout=None)
        
#         # Request Help button
#         self.add_item(Button(
#             style=discord.ButtonStyle.secondary,
#             label="Request Help",
#             custom_id="request_help_button",
#             emoji="<:kannapeer:1304352842731229194>",
#         ))
        
#         # Be Helper button
#         self.add_item(Button(
#             style=discord.ButtonStyle.secondary,
#             label="Be Helper",
#             custom_id="be_helper_button",
#             emoji="<:nicoheart:1304354892529401956>"
#         ))
        
#         # Check Rank button
#         self.add_item(Button(
#             style=discord.ButtonStyle.secondary,
#             label="Check Rank",
#             custom_id="check_rank_button",
#             emoji="<:swegdg:1305397803509485608>"
#         ))

# @bot.event
# async def on_ready():
#     print(f'Bot is ready as {bot.user}')
    
#     channel = await bot.fetch_channel(1323978359180361818)
#     message = await channel.fetch_message(1323984550019469346)
    
#     await message.edit(view=PermanentButtons())