from discord.ext import commands
from discord import app_commands
from random import choice
from english_words import get_english_words_set
import discord
from pathlib import Path

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

word_list = list(get_english_words_set(['web2'], lower=True))
hangman_words = [
    word for word in word_list
    if 5 <= len(word) <= 8 and word.isalpha()
]

MAX_WRONG_GUESSES = 10


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_hangman_games = set()

    @app_commands.command(name="joke", description="Tell a joke")
    async def joke(self, interaction: discord.Interaction):
        random_joke = choice(list(jokes.keys()))
        await interaction.response.send_message(
            f"{random_joke} {jokes[random_joke]}"
        )

    @app_commands.command(name="parrot", description="echo back what you say")
    async def parrot(self, interaction: discord.Interaction, *, message: str):
        await interaction.response.send_message(
            f"Squack! '{message}' Squack!"
        )

    @app_commands.command(
        name="whisper",
        description="Whisper a message to a user"
    )
    async def whisper(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        *,
        message: str
    ):
        await user.send(
            f"{interaction.user.mention} whispered '{message}' to you."
        )
        await interaction.response.send_message(
            "Your message has been whispered!",
            ephemeral=True
        )

    @app_commands.command(name="coin", description="Flip a coin")
    async def coin(self, interaction: discord.Interaction):
        result = choice(["Heads", "Tails"])
        await interaction.response.send_message(f"{result}!")

    def _build_hangman_embed(
        self,
        word,
        guessed_letters,
        incorrect_guesses
    ):
        display = " ".join(
            letter if letter in guessed_letters else "\_"
            for letter in word
        )

        wrong_letters = sorted(
            guessed_letters - set(word)
        )

        embed = discord.Embed(
            title="Hangman",
            description=(
                f"**{display}**\n\n"
                f"Incorrect letters: "
                f"{', '.join(wrong_letters) if wrong_letters else 'none yet'}\n"
                f"Guesses remaining: "
                f"{MAX_WRONG_GUESSES - incorrect_guesses}"
            )
        )

        image_filename = None

        if incorrect_guesses > 0:
            image_filename = (
                f"hangman"
                f"{min(incorrect_guesses, MAX_WRONG_GUESSES)}.png"
            )
            embed.set_image(
                url=f"attachment://{image_filename}"
            )

        return embed, image_filename

    @app_commands.command(
        name="hangman",
        description="Play a game of hangman"
    )
    async def hangman(self, interaction: discord.Interaction):

        if interaction.user.id in self.active_hangman_games:
            await interaction.response.send_message(
                "You already have a Hangman game in progress. "
                "Finish that one first! or type 'quit' to end it.",
                ephemeral=True
            )
            return

        word = choice(hangman_words)
        print(f"Selected word for Hangman: {word}")  # Debugging line
        guessed_letters = set()
        incorrect_guesses = 0

        self.active_hangman_games.add(interaction.user.id)

        try:
            await interaction.response.send_message(
                f"**Let's play Hangman!** "
                f"The word has {len(word)} letters.\n"
                f"Type a single letter to guess, or the whole word "
                f"if you're confident. "
                f"You have {MAX_WRONG_GUESSES} incorrect guesses allowed. "
                f"Type 'quit' to end the game.\n", 
            )

            def check(message):
                return (
                    message.author.id == interaction.user.id
                    and message.channel.id == interaction.channel.id
                    and message.content.isalpha()
                )

            while True:
                try:
                    guess_message = await self.bot.wait_for(
                        "message",
                        check=check,
                        timeout=60.0
                    )
                except TimeoutError:
                    await interaction.channel.send(
                        f"Time's up {interaction.user.mention}! "
                        f"The word was '**{word}**'."
                    )
                    return

                guess = guess_message.content.lower()

                if guess == "quit":
                    await interaction.channel.send(
                        f"Game ended by {interaction.user.mention}. "
                        f"The word was '**{word}**'."
                    )
                    return

                if guess == word:
                    await interaction.channel.send(
                        f"Congratulations {interaction.user.mention}! "
                        f"You've guessed the word '**{word}**' 🎉!"
                    )
                    return

                if len(guess) != 1:
                    await interaction.channel.send(
                        "Guess a single letter, or type the whole word "
                        "if you're confident."
                    )
                    continue

                if guess in guessed_letters:
                    await interaction.channel.send(
                        f"You already guessed '**{guess}**'. Try again."
                    )
                    continue

                guessed_letters.add(guess)

                if guess in word:
                    result_line = (
                        f"Good guess! '**{guess}**' is in the word."
                    )
                else:
                    incorrect_guesses += 1
                    result_line = (
                        f"Sorry, '**{guess}**' is not in the word."
                    )

                if all(
                    letter in guessed_letters
                    for letter in word
                ):
                    await interaction.channel.send(
                        f"{result_line}\n"
                        f"Congratulations {interaction.user.mention}! "
                        f"You've guessed the word '**{word}**' 🎉!"
                    )
                    return

                embed, image_filename = self._build_hangman_embed(
                    word,
                    guessed_letters,
                    incorrect_guesses
                )

                image_path = (
                    Path(__file__).resolve().parents[2]
                    / "images"
                    / image_filename
                    if image_filename
                    else None
                )

                file = (
                    discord.File(
                        image_path,
                        filename=image_filename
                    )
                    if image_path
                    else None
                )

                if incorrect_guesses >= MAX_WRONG_GUESSES:
                    await interaction.channel.send(
                        f"{result_line}\n"
                        f"Game over {interaction.user.mention}! "
                        f"The word was '**{word}**'.",
                        embed=embed,
                        file=file
                    )
                    return

                await interaction.channel.send(
                    result_line,
                    embed=embed,
                    file=file
                )

        finally:
            self.active_hangman_games.discard(interaction.user.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
