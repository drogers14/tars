from discord.ext import commands
import discord
import json

# Load JSON data
def load_json(filename):
    with open(filename) as read_file:
        print(f"Loaded {filename}")
        return json.load(read_file)

def save_json(obj, filename):
    file = open(filename, "w")
    json.dump(obj, file)
    file.close()

def xp_requirement(level):
    return level + (150 * level) + 20

class UserXPTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load user_levels data
        self.user_level_data = load_json("user_levels.json")

    @commands.command()
    async def stats(self, ctx):
        author = ctx.message.author
        user = author.name + author.discriminator

        if user not in self.user_level_data.keys():
            data = self.user_level_data[user] = {}
            data["level"] = 0
            data["xp"] = 0
        
        data = self.user_level_data[user]
        
        await ctx.message.reply(f"Stats for {ctx.author.name}:\nLevel {data['level']}\n{xp_requirement(data['level']) - data['xp']} XP until next level")

    async def update_user_stats(self, message):
        author = message.author
        user = author.name + author.discriminator

        # Add user to stats tracker if nonexistent
        if user not in self.user_level_data.keys():
            data = self.user_level_data[user] = {}
            data["level"] = 0
            data["xp"] = 0

        data = self.user_level_data[user]
        xp_gain = len(message.content)
        print(f"Giving {message.author.name} {xp_gain} XP")
        data["xp"] += xp_gain
        if data["xp"] >= xp_requirement(data["level"]):
            data["level"] += 1
            data["xp"] -= xp_requirement(data["level"])
            if data["xp"] < 0:
                data["xp"] = 0
            await message.channel.send(f"{message.author.mention} has reached level {data['level']}")
        
        save_json(self.user_level_data, "user_levels.json")