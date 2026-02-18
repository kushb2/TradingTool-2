# Supabase Setup (Backend)

Use this guide to connect FastAPI/CLI to Supabase.

## 1. Add environment variables

Edit `.env`:

```bash
SUPABASE_URL=https://agadprjhajxqabseiqhr.supabase.co
SUPABASE_KEY=<your-supabase-secret-or-service-role-key>
SUPABASE_PUBLISHABLE_KEY=<your-supabase-publishable-key>
```

Notes:
- Backend should use `SUPABASE_KEY` (secret/service-role key).
- Do not commit secrets to Git.

## 2. Local health check from CLI

```bash
./scripts/run-poetry.sh run python -m src.presentation.cli.supabase_cli health
```

Expected output:
- JSON with `"ok": true`
- `status_code` should be `200`

## 3. Health check from API

Start API:

```bash
./scripts/run-poetry.sh run uvicorn src.presentation.api.telegram_webhook_app:app --host 0.0.0.0 --port 8000 --reload
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health/supabase
```

## 4. Render environment variables

In Render service settings, add:
- `SUPABASE_URL`
- `SUPABASE_KEY`

If you deploy with `render.yaml`, these keys are already declared with `sync: false`; Render will ask you to set values in dashboard.
