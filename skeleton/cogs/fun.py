from discord.ext import commands
from discord import app_commands
from random import choice
from english_words import get_english_words_set 
from asyncio import TimeoutError
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

body_parts = {

}

word_list = list(get_english_words_set(['web2'], lower=True))
hangman_words = [word for word in word_list if len(word) == 6 and word.isalpha()]

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Tell a joke")
    async def joke(self, interaction: discord.Interaction):
        random_joke = choice(list(jokes.keys()))
        await interaction.response.send_message(f"{random_joke} {jokes[random_joke]}")

    @app_commands.command(name="parrot", description="echo back what you say")
    async def parrot(self, interaction: discord.Interaction, *, message: str):
        await interaction.response.send_message(f"Squack! '{message}' Squack!")

    @app_commands.command(name="whisper", description="Whisper a message to a user")
    async def whisper(self, interaction: discord.Interaction, user: discord.User, *, message: str):
        print(f"{interaction.user} whispered to {user}: {message}")
        await user.send(f"{interaction.user.mention} whispered '{message}' to you.")
        await interaction.response.send_message("Your message has been whispered!", ephemeral=True)

    @app_commands.command(name="shout", description="Shout a message to a user")
    async def shout(self, interaction: discord.Interaction, user: discord.User, *, message: str):
        print(f"Shout command called with message '{message}' by {interaction.user} to {user}")

    @app_commands.command(name="coin", description="Flip a coin")
    async def coin(self, interaction: discord.Interaction):
        result = choice(["Heads", "Tails"])
        await interaction.response.send_message(f"{result}!")

    @app_commands.command(name="hangman", description="Play a game of hangman")
    async def hangman(self, interaction: discord.Interaction):
        word = choice(hangman_words)
        guessed_letters = set()
        print(f"Hangman game started with word: '{word}' for user: {interaction.user}")
        await interaction.response.send_message(f"Let's play Hangman! The word has {len(word)} letters. Type a letter to guess. You have {len(word)} incorrect guesses allowed. Start guessing! Type 'quit' to end the game.\n\_\_\_\_\_\_")
        guesses_remaining = 10
        running_len = 0
        while True:
            def check(m):
                return m.author == interaction.user and m.content.isalpha()

            try:
                guess_message = await self.bot.wait_for('message', check=check, timeout=60.0)
            except TimeoutError:
                await interaction.channel.send(f"Time's up {interaction.user.mention}! The word was '{word}'.")
                break

            guess = guess_message.content.lower()
            if guess == "quit":
                await interaction.channel.send(f"Game ended by {interaction.user.mention}. The word was '{word}'.")
                break
            elif guess == word:
                await interaction.channel.send(f"Congratulations {interaction.user.mention}! You've guessed the word '{word}'!")
                break
            elif guess in guessed_letters:
                await interaction.channel.send(f"You already guessed '{guess}'. Try again.")
                continue

            guessed_letters.update(guess)

            if guess in word:
                await interaction.channel.send(f"Good guess! '{guess}' is in the word.")
                running_len += len(guess)
                if running_len >= len(word):
                    await interaction.channel.send(f"Congratulations {interaction.user.mention}! You've guessed the word '{word}'!")
                    break
            else:
                await interaction.channel.send(f"Sorry, '{guess}' is not in the word.")
                guesses_remaining -= 1
                if guesses_remaining <= 0:
                    await interaction.channel.send(f"Game over {interaction.user.mention}! You've run out of guesses. The word was '{word}'.")
                    break
                else:
                    await interaction.channel.send(f"You have {guesses_remaining} incorrect guesses remaining.")

            display_word = ''.join([letter if letter in guessed_letters else '\_' for letter in word])
            await interaction.channel.send(f"Incorrect letters guessed: {', '.join(sorted(guessed_letters - set(word)))}\n{display_word}")

            if all(letter in guessed_letters for letter in word):
                await interaction.channel.send(f"Congratulations {interaction.user.mention}! You've guessed the word '{word}'!")
                break
                        
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))