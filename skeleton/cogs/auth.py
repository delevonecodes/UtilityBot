from discord.ext import commands
from discord import app_commands
import discord

class Auth(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="whoami", description="Check your auth status")
    async def whoami(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You are {interaction.user}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Auth(bot))