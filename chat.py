import re
from discord.ext import commands
import discord
import json
import random
import os

from aidungeonapi import AIDungeonClient

from cogs.user_xp import UserXPTracker

settings = {
    "honesty": 90,
    "discretion": 75,
    "humor": 100,
}



class Chat(commands.Cog):
    async def __init__(self, bot):
        self.bot = bot
        aidc = await AIDungeonClient()
        adventure = await aidc.connect_to_public_adventure(os.getenv("DUNGEON"))
        await adventure.register_actions_callback(self.get_response)

    def get_response(self, result):
        return result

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        # await UserXPTracker(self.bot).update_user_stats(message)

        # Check if bot was pinged in this message
        # We check the message content as opposed to its mentions,
        # because we only want the bot to respond to @TARS

        if str(self.bot.user.id) in message.content and not message.author.bot:
            if "setting" in message.content:
                if "trust" in message.content:
                    await message.reply("Lower than yours, apparently.")
                    return
                if any(key in settings.keys() for key in message.content.split()):
                    words = message.content.split()
                    output_settings = []
                    for key in settings.keys():
                        if key in words:
                            output_settings.append(key)
                    if len(output_settings) > 0:
                        final_output = ""
                        for setting in output_settings:
                            final_output += f"{setting.capitalize()} is at {settings[setting]}%\n"
                        await message.reply(f"{final_output}")
                else:
                    await message.reply(f"My settings are:\n{json.dumps(settings, indent=2)}")
            # Edge case for user showing the bot a picture.
            elif len(message.attachments) > 0:
                attachment_types = []
                for a in message.attachments:
                    attachment_types.append(a.content_type)
                if any(filetype in ["image/png", "image/jpeg"] for filetype in attachment_types):
                    await message.reply(self.get_response("<picture>"))
            else:
                recvd_msg = message.content[len(self.bot.user.mention)+1:]
                await message.reply(self.get_response(recvd_msg))
