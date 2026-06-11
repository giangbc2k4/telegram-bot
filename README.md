# telegram-bot

Small Telegram bot for getting the current chat ID. This is useful when configuring notifications, reports, or automation workflows that need a Telegram `chat_id`.

## Features

- `/getid` command.
- Replies with the current Telegram chat ID.
- Dockerfile included for container deployment.

## Tech Stack

- Python
- python-telegram-bot
- Docker

## Getting Started

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your bot token:

```bash
set BOT_TOKEN=your_telegram_bot_token
```

Run the bot:

```bash
python bot.py
```

## Bot Command

```text
/getid
```

The bot replies with:

```text
Chat ID cua ban la: <chat_id>
```

## Docker

```bash
docker build -t telegram-bot .
docker run -e BOT_TOKEN=your_telegram_bot_token telegram-bot
```

## Notes

The current bot only uses `python-telegram-bot`. If the bot remains focused on `/getid`, dependencies such as `pandas`, `matplotlib`, and `openpyxl` can be removed.

