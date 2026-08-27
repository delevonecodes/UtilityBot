import logging
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import os
from skeleton import CustomBot

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = Intents.default()
intents.message_content, intents.members, intents.presences = True, True, True

bot = CustomBot(command_prefix=commands.when_mentioned_or('/'), intents=intents)

if __name__ == "__main__":
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)