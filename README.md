# TradingTool-2

## Frontend (React + Ant Design)

This UI uses only Ant Design components (no custom CSS files).

### 1. Install frontend dependencies

```bash
npm install
```

### 2. Run local stack (recommended)

```bash
npm run dev
```

This starts:
- frontend (Vite dev server)
- backend API (FastAPI)

### 3. Run modes

```bash
npm run dev:webhook   # Frontend + FastAPI (webhook mode)
npm run dev:polling   # Frontend + FastAPI + Telegram polling listener
npm run dev:frontend  # Frontend only
npm run dev:api       # FastAPI only
npm run dev:telegram  # Telegram polling listener only
```

Do not use polling and webhook together for the same bot token in production.

### 4. Build production frontend

`npm run dev` is development mode:
- hot reload
- local server
- no production bundle output

`npm run build` creates production files in `dist/` for deployment.

```bash
npm run build
```

### 5. Deploy to GitHub Pages

Recommended: deploy from GitHub Actions automatically on every push to `main`.

One-time GitHub Pages setting:
- Source: `GitHub Actions`

Optional manual deploy (legacy `gh-pages` branch flow):

```bash
npm run deploy
```

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
- `docs/telegram-webhook-setup.md`
- `docs/service-run.md`
- `docs/supabase-setup.md`

Render deployment blueprint:
- `render.yaml`

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

### Webhook mode (Render + FastAPI)

Start API locally:

```bash
poetry run uvicorn src.presentation.api.telegram_webhook_app:app --host 0.0.0.0 --port 8000 --reload
```

Register webhook (use your public Render URL):

```bash
poetry run python -m src.presentation.cli.telegram_webhook_cli set --public-base-url https://tradingtool-2.onrender.com --webhook-path /telegram/webhook
```

Check webhook info:

```bash
poetry run python -m src.presentation.cli.telegram_webhook_cli info
```

Delete webhook:

```bash
poetry run python -m src.presentation.cli.telegram_webhook_cli delete
```

Do not run polling and webhook together for the same bot token.

## Supabase Integration

Configure `.env`:

```bash
export SUPABASE_URL="https://agadprjhajxqabseiqhr.supabase.co"
export SUPABASE_KEY="<supabase_secret_or_service_role_key>"
```

CLI health check:

```bash
poetry run python -m src.presentation.cli.supabase_cli health
```

API health check:

```bash
curl https://tradingtool-2.onrender.com/health/supabase
```

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
- `src/presentation/api/telegram_webhook_app.py`: FastAPI webhook receiver.
- `src/presentation/cli/telegram_webhook_cli.py`: Webhook set/info/delete CLI.
- `src/infrastructure/supabase/client.py`: Supabase client provider + health check.
- `src/presentation/cli/supabase_cli.py`: Supabase health CLI.
