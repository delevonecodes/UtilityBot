from discord.ext import commands
from discord import app_commands
import discord

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        await member.kick()
        await interaction.response.send_message(f"Kicked {member}")

    @app_commands.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, member: discord.Member):
        await member.ban()
        await interaction.response.send_message(f"Banned {member}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))