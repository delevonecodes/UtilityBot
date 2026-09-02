from discord.ext import commands
from discord import app_commands
import discord
import aiohttp
import os
 
class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_base = os.getenv("STRACKER_API_BASE", "https://stracker-oxu6.onrender.com/api")
        self.headers = {"X-API-Key": os.getenv("BOT_API_KEY")}
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))
 
    async def cog_unload(self):
        await self.session.close()
 
    @app_commands.command(name="whoami", description="Check your auth status")
    async def whoami(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You are {interaction.user}")
 
    @app_commands.command(name="stracker", description="Send a link to Stracker")
    async def stracker(self, interaction: discord.Interaction):
        await interaction.response.send_message("Here's the link to Stracker: https://stracker-oxu6.onrender.com")
 
    @app_commands.command(name="link", description="Link your Discord account to Stracker")
    async def link(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            async with self.session.post(
                f"{self.api_base}/link/start",
                headers=self.headers,
                json={"discord_id": str(interaction.user.id)}
            ) as resp:
                data = await resp.json()
                status = resp.status
        except Exception:
            await interaction.followup.send(
                "Couldn't reach Stracker right now. Try again in a moment.", ephemeral=True
            )
            return
 
        if status == 409:
            await interaction.followup.send(
                f"This Discord account is already linked to Stracker user **{data.get('username')}**. "
                f"Use `/unlink` first if you want to link a different account.",
                ephemeral=True
            )
            return
        
        if status != 200:
            await interaction.followup.send(
                "Couldn't reach Stracker right now. Try again in a moment.", ephemeral=True
            )
            return
 
        await interaction.followup.send(
            f"Open **'http://127.0.0.1:5000/link-discord'**, and enter this code within 10 minutes:\n"
            f"### `{data['code']}`",
            ephemeral=True
        )
 
    @app_commands.command(name="unlink", description="Unlink your Discord account from Stracker")
    async def unlink(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            async with self.session.post(
                f"{self.api_base}/unlink",
                headers=self.headers,
                json={"discord_id": str(interaction.user.id)}
            ) as resp:
                status = resp.status
        except Exception:
            await interaction.followup.send(
                "Couldn't reach Stracker right now. Try again in a moment.", ephemeral=True
            )
            return
 
        if status == 404:
            await interaction.followup.send(
                "Your Discord account isn't linked to a Stracker account.", ephemeral=True
            )
            return
        if status != 200:
            await interaction.followup.send(
                "Couldn't reach Stracker right now. Try again in a moment.", ephemeral=True
            )
            return
 
        await interaction.followup.send(
            "Your Discord account has been unlinked from Stracker.", ephemeral=True
        )
 
async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))