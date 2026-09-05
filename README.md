# Stracker Discord Bot

A Python Discord bot that combines productivity tools, moderation, games, and integration with **[Stracker](https://stracker-oxu6.onrender.com/)**, my assignment management web application.

The bot uses Discord slash commands and communicates with Stracker through an API, allowing users to manage assignments and connect their Discord account to their Stracker account.

## Features

### Stracker Integration

* Link a Discord account to a Stracker account
* Check the currently linked Stracker account
* Unlink a Discord account from Stracker
* Add assignments to Stracker directly from Discord
* Send authenticated requests to the Stracker API

### Productivity

* Start a Pomodoro study timer
* Temporarily timeout the user while the timer is active
* Automatically remove the timeout when the timer finishes

### Fun & Games

* Random jokes
* Coin flips
* Hangman
* 8-Ball
* Parrot/echo command
* Private whisper command

### Moderation

* Kick server members

## Commands

| Command           | Description                                    |
| ----------------- | ---------------------------------------------- |
| `/link`           | Generate a code to connect Discord to Stracker |
| `/unlink`         | Disconnect the Discord account from Stracker   |
| `/whoami`         | Display the current Discord user               |
| `/stracker`       | Send the Stracker web application link         |
| `/add-assignment` | Add an assignment to Stracker                  |
| `/pomodoro`       | Start a Pomodoro study timer                   |
| `/kick`           | Kick a server member                           |
| `/joke`           | Tell a random joke                             |
| `/coin`           | Flip a coin                                    |
| `/hangman`        | Start a Hangman game                           |
| `/parrot`         | Echo a message                                 |
| `/8-ball`         | Get a random 8-Ball response                   |
| `/whisper`        | Send a private message to another Discord user |

## Architecture

The bot is organized using Discord.py cogs to separate commands by functionality.

```text
Discord Bot/
├── main.py
├── requirements.txt
├── .gitignore
└── skeleton/
    ├── __init__.py
    └── cogs/
        ├── fun.py
        ├── moderation.py
        └── utility.py
```

### Stracker Integration

```text
Discord User
      |
      v
Discord Slash Command
      |
      v
   Discord Bot
      |
      | HTTP Request
      v
 Stracker API
      |
      v
Stracker Application
```

The bot sends requests to Stracker when a user uses commands such as `/link`, `/unlink`, and `/add-assignment`.

## Technologies

* **Python**
* **discord.py**
* **aiohttp**
* **asyncio**
* **python-dotenv**
* **REST APIs**
* **Git / GitHub**

## Environment Variables

Create a `.env` file containing:

```env
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id
STRACKER_API_BASE=https://your-stracker-domain/api
BOT_API_KEY=your_shared_api_key
```

Never commit your `.env` file or expose your Discord token or API keys.

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd "Discord Bot"
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create your `.env` file with the required variables.

Run the bot:

```bash
python main.py
```

## Stracker API Integration

The bot communicates with Stracker through authenticated API requests.

The current integration includes:

```text
POST /link/start
GET  /link/status
POST /unlink
POST /add-assignment
```

### Adding an Assignment

After linking a Discord account, a user can run:

```text
/add-assignment
```

The bot sends the assignment information to Stracker through the API, where it is added to the user's account.

This allows assignments to be added without leaving Discord.

## Project Structure

### `main.py`

Responsible for:

* Starting the Discord bot
* Loading cogs
* Connecting to Discord
* Registering slash commands

### `cogs/fun.py`

Contains commands such as:

* `/joke`
* `/coin`
* `/hangman`
* `/parrot`
* `/whisper`
* `/8-ball`

### `cogs/moderation.py`

Contains moderation commands such as:

* `/kick`

### `cogs/utility.py`

Contains productivity and Stracker-related commands such as:

* `/link`
* `/unlink`
* `/whoami`
* `/stracker`
* `/add-assignment`
* `/pomodoro`

## What I Learned

Building this project gave me experience with:

* Asynchronous Python
* Discord slash commands
* REST API integration
* HTTP requests using `aiohttp`
* Connecting two separate applications
* API authentication
* Account linking
* Modular code organization
* Discord permissions
* Environment variables
* Handling API errors and user input

## Future Improvements

* Add a command to view upcoming assignments
* Add commands to complete and delete assignments
* Add assignment deadline reminders
* Add more moderation commands
* Add automated tests
* Add better logging
* Improve Discord embeds and command responses
* Add GitHub Actions for testing

## Demo

Coming soon.

The demo will show the bot being used to:

1. Link a Discord account to Stracker
2. Add an assignment through Discord
3. View the assignment in Stracker
4. Start a Pomodoro timer
5. Use the bot's other commands

## Related Project

**Stracker — Assignment Management Web Application**

[View Stracker on GitHub](https://github.com/delevonecodes/assignment_tracker2)

[Launch Stracker](https://stracker-oxu6.onrender.com/)

## Author

**Computer Science Student**

GitHub: [delevonecodes](https://github.com/delevonecodes)
