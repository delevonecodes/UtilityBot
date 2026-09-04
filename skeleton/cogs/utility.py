from time import time
from asyncio import sleep
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import datetime
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
        link_embed = discord.Embed(
            title="Link Your Discord Account to Stracker",
            description=(
                f"Open **'http://127.0.0.1:5000/link-discord'**, and enter this code within 10 minutes:\n"
                f"### `**{data['code']}**`"
            )
        )
        await interaction.followup.send(
            embed=link_embed,
            ephemeral=True
        )
        for _ in range(200):
            await sleep(3)
            try:
                async with self.session.get(
                    f"{self.api_base}/link/status",
                    headers=self.headers,
                    params={"discord_id": str(interaction.user.id)}
                ) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
            except Exception as e:
                    await interaction.followup.send(
                        "Couldn't reach Stracker right now. Try again in a moment.", ephemeral=True
                    )
                    print(f"Error checking link status: {e}")
                    return
            if data.get('linked'):
                await interaction.followup.send(f"Your Discord account has been successfully linked to Stracker user **{data.get('username')}**!", ephemeral=True)
                return
        await interaction.followup.send("Your Discord account was not linked within the time limit. Please try again.", ephemeral=True)

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

    @app_commands.command(name="add-assignment", description="Add an assignment to Stracker")
    @app_commands.describe(
        course="Course name",
        assignment_name="Assignment name",
        due_date="Due date, format MM/DD/YYYY or 'today'",
        priority="How urgent this assignment is",
        description="Optional notes"
    )
    @app_commands.choices(priority=[
        app_commands.Choice(name="High", value="High"),
        app_commands.Choice(name="Medium", value="Medium"),
        app_commands.Choice(name="Low", value="Low"),
    ])
    async def add_assignment(self, interaction: discord.Interaction, course: str, assignment_name: str, due_date: str, priority: app_commands.Choice[str], *, description: str = None):
        await interaction.response.defer(ephemeral=True)

        if due_date.lower() == "today":
            due_date_obj = datetime.date.today()
        else:
            try:
                due_date_obj = datetime.datetime.strptime(due_date, "%m/%d/%Y").date()
            except ValueError:
                await interaction.followup.send("Invalid due date format. Please use MM/DD/YYYY or 'today'.", ephemeral=True)
                return

        try:
            async with self.session.post(
                f"{self.api_base}/add-assignment",
                headers=self.headers,
                json={
                    "discord_id": str(interaction.user.id),
                    "course": course,
                    "assignment_name": assignment_name,
                    "due_date": due_date_obj.isoformat(),
                    "priority": priority.value,
                    "description": description
                }
            ) as resp:
                data = await resp.json()
                status = resp.status
                
        except Exception as e:
            await interaction.followup.send(
                "Couldn't reach Stracker right now. Try again in a moment.", ephemeral=True
            )
            print(f"Error adding assignment: {e}")
            return

        if status == 404:
            await interaction.followup.send(
                "Your Discord account isn't linked to Stracker yet. Run `/link` first.",
                ephemeral=True
            )
            return

        if status != 201:
            await interaction.followup.send(
                "Couldn't add that assignment. Double-check the details and try again.",
                ephemeral=True
            )
            return
        embed = discord.Embed(
            title="New Assignment Added",
            description=f"**Assignment**: {data['name']}\n**Course**: {data['course']}\n**Due**: {due_date_obj.strftime('%m/%d/%Y')}\n**Priority**: {data['priority']}"
        )
        await interaction.followup.send(embed=embed,ephemeral=True)

    @app_commands.command(name="pomodoro", description="Start a Pomodoro timer and be timed out while you study")
    @app_commands.describe(duration="Pomodoro duration in minutes")
    async def pomodoro(self, interaction: discord.Interaction, duration: int):
        if interaction.guild is None:
            await interaction.response.send_message(
                "The Pomodoro command can only be used in a server.",
                ephemeral=True
            )
            return

        if duration < 1:
            await interaction.response.send_message(
                "The duration must be at least 1 minute.",
                ephemeral=True
            )
            return

        if duration > 40320:
            await interaction.response.send_message(
                "The maximum Pomodoro duration is 28 days.",
                ephemeral=True
            )
            return

        member = interaction.guild.get_member(interaction.user.id)

        if member is None:
            await interaction.response.send_message(
                "I couldn't find you as a member of this server.",
                ephemeral=True
            )
            return

        bot_member = interaction.guild.me

        if not bot_member.guild_permissions.moderate_members:
            await interaction.response.send_message(
                "I don't have the **Moderate Members** permission, so I can't "
                "start the Pomodoro timeout.",
                ephemeral=True
            )
            return

        if member.top_role >= bot_member.top_role:
            await interaction.response.send_message(
                "I can't time you out because your highest role is higher than "
                "or equal to my highest role. Move my bot role above your role "
                "in **Server Settings → Roles**.",
                ephemeral=True
            )
            return

        if member.id == interaction.guild.owner_id:
            await interaction.response.send_message(
                "I can't time out the server owner.",
                ephemeral=True
            )
            return

        try:
            await member.timeout(
                timedelta(minutes=duration),
                reason=f"Pomodoro timer - {duration} minutes"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "Discord denied the timeout. Make sure I have the **Moderate "
                "Members** permission and that my bot role is above your role.",
                ephemeral=True
            )
            return

        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Discord returned an error while trying to time you out: `{e}`",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Pomodoro started for **{duration} minutes**!\n"
            f"You are now timed out. Go study! 📚",
            ephemeral=True
        )
        await sleep(duration * 60)
        try:
            await member.timeout(
                None,
                reason="Pomodoro timer finished"
            )

            await interaction.followup.send(
                f"Your **{duration}-minute Pomodoro is over!** "
                f"You're no longer timed out. 🎉",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "Your Pomodoro is over, but I couldn't remove your timeout. "
                "Please check my **Moderate Members** permission.",
                ephemeral=True
            )

        except discord.HTTPException:
            await interaction.followup.send(
                "Your Pomodoro is over, but Discord returned an error while "
                "removing the timeout.",
                ephemeral=True
            )
    
async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))