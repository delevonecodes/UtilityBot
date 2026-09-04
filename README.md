# Stracker Discord Bot

A Python Discord bot that combines productivity tools, moderation, games, and direct integration with **[Stracker](https://stracker-oxu6.onrender.com/)**, a full-stack assignment management web application.

The bot uses Discord slash commands and communicates with Stracker through an authenticated HTTP API, allowing users to manage assignments from Discord while keeping their data connected to the web application.

## Features

### Stracker Integration

* Link a Discord account to a Stracker account using a temporary verification code
* Check the currently authenticated Discord user
* Unlink a Discord account from Stracker
* Create Stracker assignments directly from Discord
* Communicate with Stracker through authenticated REST API requests
* Associate Discord users with their Stracker accounts

### Productivity

* Start a configurable Pomodoro study timer
* Temporarily timeout the user for the selected study duration
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

| Command           | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `/link`           | Generate a temporary code to connect Discord to Stracker |
| `/unlink`         | Disconnect the Discord account from Stracker             |
| `/whoami`         | Display the current Discord user                         |
| `/stracker`       | Send the Stracker web application link                   |
| `/add-assignment` | Add an assignment to Stracker from Discord               |
| `/pomodoro`       | Start a Pomodoro study timer                             |
| `/kick`           | Kick a server member                                     |
| `/joke`           | Tell a random joke                                       |
| `/coin`           | Flip a coin                                              |
| `/hangman`        | Start a Hangman game                                     |
| `/parrot`         | Echo a message                                           |
| `/8-ball`         | Receive a magic 8-ball response                          |
| `/whisper`        | Send a private message to another Discord user           |

## Architecture

The bot is organized using Discord.py cogs, separating commands by responsibility.

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

### System Architecture

```text
Discord User
      │
      ▼
Discord Slash Command
      │
      ▼
   discord.py
      │
      │ Authenticated HTTP Request
      ▼
  Stracker REST API
      │
      ▼
Stracker Backend
      │
      ▼
 Database
```

### Account Linking Flow

```text
Discord User
      │
      │ /link
      ▼
Discord Bot
      │
      │ Request verification code
      ▼
Stracker API
      │
      │ Temporary Code
      ▼
Discord User
      │
      │ Enter code in Stracker
      ▼
Stracker
      │
      │ Link Discord ID
      ▼
Discord Bot
```

## Technologies

* **Python**
* **discord.py**
* **Discord Slash Commands / Application Commands**
* **aiohttp**
* **asyncio**
* **python-dotenv**
* **REST APIs**
* **Git / GitHub**

## Environment Variables

Create a `.env` file containing the required environment variables:

```env
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id
STRACKER_API_BASE=https://your-stracker-domain/api
BOT_API_KEY=your_shared_api_key
```

Never commit `.env` or expose your Discord bot token or API keys publicly.

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

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file with the required variables.

Run the bot:

```bash
python main.py
```

## Stracker API Integration

The Discord bot communicates with Stracker through authenticated API endpoints.

Current functionality includes:

```text
POST /link/start
GET  /link/status
POST /unlink
POST /add-assignment
```

API requests are authenticated using an API key.

### Adding an Assignment

A user can run:

```text
/add-assignment
```

The bot sends an authenticated API request to Stracker containing the assignment information.

Stracker then creates the assignment in the user's account.

This allows users to manage their assignments without leaving Discord.

## Deployment

The bot requires a persistent Python environment with access to:

* `DISCORD_TOKEN`
* `GUILD_ID`
* `STRACKER_API_BASE`
* `BOT_API_KEY`

Environment variables should be configured through the hosting provider rather than committed to the repository.

Before deployment, verify that:

1. The Stracker API is publicly accessible.
2. `STRACKER_API_BASE` points to the production Stracker API.
3. All Discord bot permissions are configured correctly.
4. Secrets are stored securely as environment variables.

## Security

The project uses several security practices:

* Environment variables for secrets
* `.gitignore` protection for `.env`
* API-key authentication between the bot and Stracker
* Temporary account-linking codes
* Ephemeral Discord responses for sensitive account actions where appropriate

## Project Structure

### `main.py`

Responsible for:

* Starting the Discord client
* Loading cogs
* Registering slash commands
* Connecting to Discord

### `cogs/fun.py`

Contains entertainment-related commands such as:

* `/joke`
* `/coin`
* `/hangman`
* `/parrot`
* `/whisper`

### `cogs/moderation.py`

Contains moderation functionality such as:

* `/kick`

### `cogs/utility.py`

Contains productivity and Stracker integration functionality such as:

* `/link`
* `/unlink`
* `/whoami`
* `/stracker`
* `/add-assignment`
* `/pomodoro`

## What I Learned

Building this project provided hands-on experience with:

* Asynchronous Python programming
* Discord application commands
* REST API integration
* HTTP requests with `aiohttp`
* Authentication between services
* Temporary account-linking systems
* Modular application architecture
* Discord permissions and member management
* Environment-variable based configuration
* Connecting multiple independent applications
* Error handling for external APIs

## Future Improvements

* Add `/assignments` to view upcoming Stracker assignments
* Add `/complete` and `/delete-assignment` commands
* Add deadline reminders through Discord
* Add assignment statistics and productivity analytics
* Add automated unit and integration tests
* Add centralized logging
* Add stronger moderation permission checks
* Add GitHub Actions for testing and CI/CD
* Improve Discord embeds, buttons, and command UX
* Replace account-linking polling with a more event-driven system

## Demo

Coming soon.

A future demo will show:

1. Linking a Discord account to Stracker
2. Creating an assignment through Discord
3. Viewing the assignment in Stracker
4. Starting a Pomodoro timer
5. Receiving productivity/deadline reminders

## Related Project

**Stracker — Full-Stack Assignment Management Platform**

[View Stracker on GitHub](https://github.com/delevonecodes/assignment_tracker2)

[Launch Stracker](https://stracker-oxu6.onrender.com/)

## Author

**Computer Science Student**

GitHub: [delevonecodes](https://github.com/delevonecodes)
