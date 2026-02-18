# Service Run Guide

Use this as your daily reference for running the project locally.

## What runs in local dev

- Frontend: React + Ant Design (Vite dev server)
- Backend: FastAPI webhook API
- Telegram mode: Webhook only (no polling listener required)

## Prerequisites (run once)

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2
npm install
./scripts/run-poetry.sh install
```

## Environment setup

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2
cp .env.example .env
```

Set real values in `.env` for:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`

## Start frontend + backend together (recommended)

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2 && npm run dev:webhook
```

This starts:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Start services separately (optional)

Frontend only:

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2 && npm run dev:frontend
```

Backend only:

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2 && npm run dev:api
```

## Verify backend

```bash
curl http://localhost:8000/health
```

Expected:

```text
{"status":"ok"}
```

## Webhook commands

Set webhook to Render URL:

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2 && ./scripts/run-poetry.sh run python -m src.presentation.cli.telegram_webhook_cli set --public-base-url https://tradingtool-2.onrender.com --webhook-path /telegram/webhook
```

Check webhook info:

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2 && ./scripts/run-poetry.sh run python -m src.presentation.cli.telegram_webhook_cli info
```

Delete webhook:

```bash
cd /Users/kushbhardwaj/Documents/github/TradingTool-2 && ./scripts/run-poetry.sh run python -m src.presentation.cli.telegram_webhook_cli delete
```

## Stop services

In the running terminal, press:

```text
Ctrl + C
```

## Important note

Use webhook mode only for now. Do not run Telegram polling listener at the same time.

