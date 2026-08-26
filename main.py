import logging
import discord
from dotenv import load_dotenv
import os
from init import MyBot

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content, intents.members, intents.presences = True, True, True

bot = MyBot(command_prefix='!', intents=intents)

if __name__ == "__main__":
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)