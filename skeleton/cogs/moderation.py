import os
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class WarningRecord(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True)
    guild_id = Column(String(32), nullable=False)
    user_id = Column(String(32), nullable=False)
    moderator_id = Column(String(32), nullable=False)
    reason = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

engine = create_engine("sqlite:///moderation.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

WARNING_TIMEOUT_THRESHOLD = 3
AUTO_TIMEOUT_MINUTES = 30


class ConfirmBan(discord.ui.View):
    """Confirmation prompt shown before an irreversible ban."""

    def __init__(self, moderator_id: int, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.moderator_id = moderator_id
        self.confirmed = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.moderator_id:
            await interaction.response.send_message(
                "Only the moderator who ran this command can confirm it.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirm Ban", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="Ban confirmed.", view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="Ban cancelled.", view=self)
        self.stop()


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mod_log_channel_id = os.getenv("MOD_LOG_CHANNEL_ID")

    async def _log_action(self, interaction: discord.Interaction, action: str, target, reason: str):
        if not self.mod_log_channel_id:
            return
        channel = interaction.guild.get_channel(int(self.mod_log_channel_id))
        if channel is None:
            return
        embed = discord.Embed(
            title=f"Moderation Action: {action}",
            color=discord.Color.orange(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Target", value=f"{target} ({target.id})", inline=False)
        embed.add_field(name="Moderator", value=f"{interaction.user} ({interaction.user.id})", inline=False)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        await channel.send(embed=embed)

    @staticmethod
    def _hierarchy_ok(guild: discord.Guild, member: discord.Member) -> bool:
        return member.top_role < guild.me.top_role and member.id != guild.owner_id

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(reason="Why this member is being kicked")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member,
                   reason: str = "No reason provided"):
        if not self._hierarchy_ok(interaction.guild, member):
            await interaction.response.send_message(
                "I can't kick that member — their role is too high, or they're the server owner.",
                ephemeral=True,
            )
            return

        try:
            await member.send(f"You were kicked from **{interaction.guild.name}**.\nReason: {reason}")
        except discord.Forbidden:
            pass

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            await interaction.response.send_message(
                "Discord denied that kick. Check my role and permissions.", ephemeral=True
            )
            return

        await interaction.response.send_message(f"Kicked **{member}**. Reason: {reason}")
        await self._log_action(interaction, "Kick", member, reason)

    @app_commands.command(name="ban", description="Ban a member (requires confirmation)")
    @app_commands.describe(reason="Why this member is being banned")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member,
                  reason: str = "No reason provided"):
        if not self._hierarchy_ok(interaction.guild, member):
            await interaction.response.send_message(
                "I can't ban that member — their role is too high, or they're the server owner.",
                ephemeral=True,
            )
            return

        view = ConfirmBan(moderator_id=interaction.user.id)
        await interaction.response.send_message(
            f"Ban **{member}**? Reason: {reason}\nThis action is irreversible.",
            view=view,
            ephemeral=True,
        )
        await view.wait()

        if not view.confirmed:
            return

        try:
            await member.send(f"You were banned from **{interaction.guild.name}**.\nReason: {reason}")
        except discord.Forbidden:
            pass

        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            await interaction.followup.send(
                "Discord denied that ban. Check my role and permissions.", ephemeral=True
            )
            return

        await interaction.followup.send(f"Banned **{member}**. Reason: {reason}")
        await self._log_action(interaction, "Ban", member, reason)

    @app_commands.command(name="unban", description="Unban a user by their ID")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
        except (ValueError, discord.NotFound):
            await interaction.response.send_message(
                "That doesn't look like a valid user ID.", ephemeral=True
            )
            return

        try:
            await interaction.guild.unban(user)
        except discord.NotFound:
            await interaction.response.send_message(f"{user} isn't banned here.", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message(
                "Discord denied that unban. Check my permissions.", ephemeral=True
            )
            return

        await interaction.response.send_message(f"Unbanned **{user}**.")
        await self._log_action(interaction, "Unban", user, "—")

    @app_commands.command(name="timeout", description="Time out a member for a set duration")
    @app_commands.describe(minutes="Timeout duration in minutes", reason="Why this member is being timed out")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int,
                       reason: str = "No reason provided"):
        if minutes < 1 or minutes > 40320:
            await interaction.response.send_message(
                "Duration must be between 1 minute and 28 days.", ephemeral=True
            )
            return

        if not self._hierarchy_ok(interaction.guild, member):
            await interaction.response.send_message(
                "I can't time out that member — their role is too high, or they're the server owner.",
                ephemeral=True,
            )
            return

        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
        except discord.Forbidden:
            await interaction.response.send_message(
                "Discord denied that timeout. Check my role and permissions.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Timed out **{member.mention}** for {minutes} minute(s). Reason: {reason}"
        )
        await self._log_action(interaction, "Timeout", member, f"{reason} ({minutes}m)")

    @app_commands.command(name="untimeout", description="Remove a member's timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member):
        try:
            await member.timeout(None, reason=f"Timeout removed by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message(
                "Discord denied that. Check my role and permissions.", ephemeral=True
            )
            return

        await interaction.response.send_message(f"Removed timeout for **{member}**.")
        await self._log_action(interaction, "Untimeout", member, "—")

    @app_commands.command(name="warn", description="Log a warning against a member")
    @app_commands.describe(reason="Why this member is being warned")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        session = Session()
        try:
            session.add(WarningRecord(
                guild_id=str(interaction.guild.id),
                user_id=str(member.id),
                moderator_id=str(interaction.user.id),
                reason=reason,
            ))
            session.commit()

            count = (
                session.query(WarningRecord)
                .filter_by(guild_id=str(interaction.guild.id), user_id=str(member.id))
                .count()
            )
        finally:
            session.close()

        await interaction.response.send_message(f"Warned **{member.mention}** ({count} total). Reason: {reason}")
        await self._log_action(interaction, f"Warn ({count} total)", member, reason)

        if count >= WARNING_TIMEOUT_THRESHOLD and self._hierarchy_ok(interaction.guild, member):
            try:
                await member.timeout(
                    timedelta(minutes=AUTO_TIMEOUT_MINUTES),
                    reason=f"Reached {count} warnings",
                )
                await interaction.followup.send(
                    f"**{member.mention}** reached {count} warnings — auto-timed out for {AUTO_TIMEOUT_MINUTES} minutes."
                )
                await self._log_action(interaction, "Auto-timeout", member, f"Reached {count} warnings")
            except discord.Forbidden:
                pass

    @app_commands.command(name="warnings", description="View a member's warning history")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        session = Session()
        try:
            records = (
                session.query(WarningRecord)
                .filter_by(guild_id=str(interaction.guild.id), user_id=str(target.id))
                .order_by(WarningRecord.timestamp.desc())
                .all()
            )
        finally:
            session.close()

        if not records:
            await interaction.response.send_message(f"**{target}** has no warnings.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Warnings for {target}", color=discord.Color.orange())
        for record in records[:10]:
            embed.add_field(
                name=record.timestamp.strftime("%Y-%m-%d %H:%M UTC"),
                value=f"{record.reason} (by <@{record.moderator_id}>)",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="purge", description="Bulk-delete recent messages in this channel")
    @app_commands.describe(amount="Number of messages to delete (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Amount must be between 1 and 100.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} message(s).", ephemeral=True)
        await self._log_action(interaction, "Purge", interaction.channel, f"{len(deleted)} messages")

    @kick.error
    @ban.error
    @unban.error
    @timeout.error
    @untimeout.error
    @warn.error
    @purge.error
    async def moderation_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to use this command.", ephemeral=True
            )
        elif isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message(
                "I'm missing the permissions needed to do that. Check my role settings.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Something went wrong running that command.", ephemeral=True
            )
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))