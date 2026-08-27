from discord.ext import commands
from discord import app_commands
from random import choice

import discord

jokes = {
    "Why don't scientists trust atoms?": "Because they make up everything!",
    "Why did the scarecrow win an award?": "Because he was outstanding in his field!",
    "Why did the bicycle fall over?": "Because it was two-tired!",
    "Why did the robber jump in the shower?": "Because he wanted to make a clean getaway!",
    "Why did the tomato turn red?": "Because it saw the salad dressing!",
    "Why did the math book look sad?": "Because it had too many problems!",
    "Why did the chicken cross the playground?": "To get to the other slide!",
    "Why did the cookie go to the doctor?": "Because it was feeling crumbly!",
    "Why did the computer go to the doctor?": "Because it had a virus!",
    "Why did the coffee file a police report?": "Because it got mugged!",
}

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Tell a joke")
    async def joke(self, interaction: discord.Interaction):
        random_joke = choice(list(jokes.keys()))
        await interaction.response.send_message(f"{random_joke} {jokes[random_joke]}")

    @app_commands.command(name="parrot", description="Parrot back what you say")
    async def parrot(self, interaction: discord.Interaction, *, message: str):
        await interaction.response.send_message(f"Squack! '{message}' Squack!")

    @app_commands.command(name="whisper", description="Whisper a message to a user")
    async def whisper(self, interaction: discord.Interaction, user: discord.User, *, message: str):
        print(f"{interaction.user} whispered to {user}: {message}")
        await user.send(f"'{interaction.user}' whispered to you: '{message}'")
        #await interaction.delete_original_response() #deletes original message so only the user sees it and its super secret

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))