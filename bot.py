from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
#from chat import Chat
from cogs.functions import Functions
#from cogs.user_xp import UserXPTracker

load_dotenv()

token = os.getenv("TOKEN")
prefix = os.getenv("PREFIX")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

bot.add_cog(Functions(bot))
#bot.add_cog(Chat(bot))
#bot.add_cog(UserXPTracker(bot))

@bot.event
async def on_ready():
    print(f'TARS online')

bot.run(token)