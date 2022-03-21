import re
from discord.ext import commands
import discord
import json
import random

settings = {
    "honesty": 90,
    "discretion": 75,
    "humor": 100,
}

# Load JSON data
def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}'")
        return json.load(bot_responses)


# Store JSON data
response_data = load_json("bot.json")

def random_bad_input_response():
    random_list = [
        "Please be more descriptive.",
        "I don't understand that yet.",
        "Do you mind trying to rephrase that?",
        "I can't answer that yet, please try asking something else."
    ]

    list_count = len(random_list)
    random_item = random.randrange(list_count)

    return random_list[random_item]

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """"
    Rudimentary chat bot code obtained from
    https://github.com/federicocotogno/json_chatbot
    """
    def get_response(self, input_string):
        split_message = re.split(r'\s+|[,;?!.-]\s*', input_string.lower())
        score_list = []

        # Check all the responses
        for response in response_data:
            response_score = 0
            required_score = 0
            required_words = response["required_words"]

            # Check if there are any required words
            if required_words:
                for word in split_message:
                    if word in required_words:
                        required_score += 1

            # Amount of required words should match the required score
            if required_score == len(required_words):
                # print(required_score == len(required_words))
                # Check each word the user has typed
                for word in split_message:
                    # If the word is in the response, add to the score
                    if word in response["user_input"]:
                        response_score += 1

            # Add score to list
            score_list.append(response_score)
            # Debugging: Find the best phrase
            # print(response_score, response["user_input"])

        # Find the best response and return it if they're not all 0
        best_response = max(score_list)
        response_index = score_list.index(best_response)

        # Check if input is empty
        if input_string == "":
            reply_candidates = [
                "Yeah? What's up?",
                "You rang?",
                "What do you need?",
                "You pinged me.",
                "Hm?",
                "Yes?"
            ]
            return random.choice(reply_candidates)

        # If there is no good response, return a random one.
        if best_response != 0:
            return random.choice(response_data[response_index]["bot_response"])

        return random_bad_input_response()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
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
