from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import chat
from cogs import functions

load_dotenv()

token = os.getenv("TOKEN")
prefix = os.getenv("PREFIX")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

bot.add_cog(functions.Functions(bot))
bot.add_cog(chat.Chat(bot))

@bot.event
async def on_ready():
    print(f'TARS online')

bot.run(token)