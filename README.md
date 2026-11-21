# Faceit Helper

A Flask website and a Telegram bot for looking up CS2 player statistics on [FACEIT](https://www.faceit.com).

> [!NOTE]
> This is the first version of the project. The current version is split into [Faceit_Helper_Client](https://github.com/zdtexus/Faceit_Helper_Client) (React) and [Faceit_Helper_Server](https://github.com/zdtexus/Faceit_Helper_Server) (NestJS).

## Contents

- [Features](#features)
- [Getting started](#getting-started)
- [Bot commands](#bot-commands)
- [Project structure](#project-structure)

## Features

**Website**

- Search for a player by FACEIT nickname or Steam ID
- Player page with overall stats, global and country rank, and stats for each map
- Top players leaderboard that loads more players on demand

**Telegram bot**

- Look up a player from the chat
- Average stats over the last 10, 20, 50 or 100 matches
- Top players by region

## Getting started

### Prerequisites

- Python 3.12
- A [FACEIT API key](https://developers.faceit.com/)
- A [Steam Web API key](https://steamcommunity.com/dev/apikey)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Installation

```bash
git clone https://github.com/zdtexus/Faceit-helper.git
cd Faceit-helper
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt python-telegram-bot
```

### Configuration

Set the environment variables:

```bash
export FACEIT_API_KEY=your_faceit_api_key
export STEAM_API_KEY=your_steam_api_key
export TELEGRAM_API_KEY=your_telegram_bot_token
```

### Running

| Command | Description |
|---|---|
| `python run.py` | Start the website on `http://localhost:5000` |
| `python bot.py` | Start the Telegram bot |

## Bot commands

| Command | Description |
|---|---|
| `/start` | Show the main menu |
| `/help` | Show help |
| `/find_player` | Look up a player |
| `/top_players` | Choose a region for the leaderboard |
| `/eu`, `/na`, `/sa`, `/sea`, `/oce` | Top players in that region |

## Project structure

```text
app/
  models.py      FACEIT and Steam API calls, stats calculations
  routes.py      Flask routes
  templates/     Jinja templates
  static/        CSS, TypeScript, flags, map images
bot.py           Telegram bot
config.py        Reads API keys from the environment
run.py           Website entry point
```
