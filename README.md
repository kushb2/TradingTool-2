# TradingTool-2

## Project Setup (Poetry)

### 1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Create and install environment

```bash
poetry env use 3.12
poetry install
```

### 3. Configure bot token

```bash
cp .env.example .env
export TELEGRAM_BOT_TOKEN="<bot_id>:<secret_from_botfather>"
export TELEGRAM_CHAT_ID="974882412"
export TELEGRAM_POLL_TIMEOUT_SECONDS="60"
export TELEGRAM_REQUEST_TIMEOUT_SECONDS="75"
```

## Telegram Module (Plug-and-Play)

Testing guide:
- `docs/telegram-bot-testing.md`

### Send a text message

```bash
poetry run python -m src.presentation.cli.telegram_cli send --text "Hello from TradingTool"
```

### Listen and receive messages/files

```bash
poetry run python -m src.presentation.cli.telegram_cli listen --download-dir data/telegram_downloads
```

The listener handles:
- text messages
- screenshots/images (`photo`)
- Excel files and other documents (`document`)

Long-polling reliability defaults:
- `TELEGRAM_POLL_TIMEOUT_SECONDS=60`
- `TELEGRAM_REQUEST_TIMEOUT_SECONDS=75` (must be greater than poll timeout)
- `TELEGRAM_ERROR_RETRY_SLEEP_SECONDS=1`
- `TELEGRAM_MAX_RETRY_SLEEP_SECONDS=30`

Downloaded files are saved under `data/telegram_downloads/`.

## Developer Checks

```bash
poetry run ruff check .
poetry run mypy src
```

## Module Files

- `src/infrastructure/telegram/client.py`: Telegram Bot API HTTP client.
- `src/infrastructure/telegram/module.py`: High-level module facade.
- `src/infrastructure/telegram/models.py`: Typed message models.
- `src/presentation/cli/telegram_cli.py`: CLI for send/listen.
