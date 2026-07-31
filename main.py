import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

role_name = "Gamer"

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - dont use that word!")

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} has been given the role '{role_name}'")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"{ctx.author.mention} - {msg}")

@bot.command()
async def parrot(ctx, *, msg):
    await ctx.reply(msg)

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("Yes")
    await poll_message.add_reaction("No")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"'{role_name}' has been removed from {ctx.author.mention}")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
@commands.has_role(role_name)
async def secret(ctx):
    await ctx.send("Shhhh, you're in the secret club")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)