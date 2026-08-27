import discord
from discord.ext import commands
import os

class CustomBot(commands.Bot):
    def __init__(self, banned_words=[...], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.banned_words = banned_words

    async def setup_hook(self):
        cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"skeleton.cogs.{filename[:-3]}")
        await self.tree.sync()

    async def on_ready(self):
        print(f"We are ready to go in, {self.user.name}")

