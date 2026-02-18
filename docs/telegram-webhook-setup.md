# Telegram Webhook Setup (Render + FastAPI)

Use this when deploying Telegram updates via FastAPI webhook instead of long polling.

## 1. Required env vars

Set in Render service environment:

```bash
TELEGRAM_BOT_TOKEN=<bot_id>:<secret_from_botfather>
TELEGRAM_CHAT_ID=974882412
TELEGRAM_WEBHOOK_SECRET=<random_secret_string>
TELEGRAM_DOWNLOAD_DIR=data/telegram_downloads
RENDER_EXTERNAL_URL=https://tradingtool-2.onrender.com
```

## 2. Start FastAPI app

Render Start Command:

```bash
poetry run uvicorn src.presentation.api.telegram_webhook_app:app --host 0.0.0.0 --port $PORT
```

## 3. Register webhook with Telegram

Run once after deploy:

```bash
poetry run python -m src.presentation.cli.telegram_webhook_cli set --public-base-url https://tradingtool-2.onrender.com --webhook-path /telegram/webhook
```

## 4. Check webhook status

```bash
poetry run python -m src.presentation.cli.telegram_webhook_cli info
```

## 5. Remove webhook (if needed)

```bash
poetry run python -m src.presentation.cli.telegram_webhook_cli delete
```

## 6. Important operational rule

Do not run webhook and long polling at the same time for the same bot token.

