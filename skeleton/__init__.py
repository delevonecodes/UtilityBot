import discord
from discord.ext import commands

class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self): 
        print(f"We are ready to go in, {self.user.name}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention} - That word is prohibited!")
        else:
            print(f"Message from {message.author}: {message.content}")

        await self.process_commands(message)

