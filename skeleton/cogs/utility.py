from discord.ext import commands
from discord import app_commands
import discord

class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="whoami", description="Check your auth status")
    async def whoami(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You are {interaction.user}")

    @app_commands.command(name="stracker", description="Link to Stracker")
    async def stracker(self, interaction: discord.Interaction):
        await interaction.response.send_message("Here's the link to Stracker: https://stracker-oxu6.onrender.com")

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))