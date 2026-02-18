"""FastAPI app with Telegram webhook endpoint."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.telegram import TelegramBotModule, TelegramMessage
from src.infrastructure.telegram.client import TelegramApiError

app: FastAPI = FastAPI(title="TradingTool-2 API", version="0.1.0")

load_dotenv()
raw_cors_origins: str = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://kushb2.github.io,http://localhost:5173,http://127.0.0.1:5173",
)
cors_allowed_origins: list[str] = [
    origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass(frozen=True)
class WebhookRuntime:
    """Runtime dependencies for webhook request handling."""

    bot: TelegramBotModule
    download_dir: Path
    secret_token: str | None


@lru_cache(maxsize=1)
def get_runtime() -> WebhookRuntime:
    """Create shared runtime objects once per process."""
    load_dotenv()

    bot: TelegramBotModule = TelegramBotModule.from_env()
    download_dir: Path = Path(
        os.getenv("TELEGRAM_DOWNLOAD_DIR", "data/telegram_downloads")
    )
    download_dir.mkdir(parents=True, exist_ok=True)

    secret_raw: str | None = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    secret_token: str | None = None
    if secret_raw is not None and secret_raw.strip() != "":
        secret_token = secret_raw.strip()

    return WebhookRuntime(
        bot=bot,
        download_dir=download_dir,
        secret_token=secret_token,
    )


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint for quick Render checks."""
    return {"service": "TradingTool-2", "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    """Health endpoint used by deployment checks."""
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, object]:
    """Receive Telegram webhook updates and process supported messages."""
    runtime: WebhookRuntime = get_runtime()

    if runtime.secret_token is not None:
        if x_telegram_bot_api_secret_token != runtime.secret_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Telegram webhook secret token",
            )

    payload: object
    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {error}",
        ) from error

    try:
        message: TelegramMessage | None = runtime.bot.parse_update_message(payload)
    except TelegramApiError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Telegram update payload: {error}",
        ) from error

    if message is None:
        return {
            "ok": True,
            "processed": False,
            "reason": "unsupported_update_type",
        }

    saved_files: list[str] = _process_incoming_message(
        bot=runtime.bot,
        message=message,
        download_dir=runtime.download_dir,
    )
    return {
        "ok": True,
        "processed": True,
        "update_id": message.update_id,
        "chat_id": message.chat_id,
        "saved_files": saved_files,
    }


def _process_incoming_message(
    bot: TelegramBotModule,
    message: TelegramMessage,
    download_dir: Path,
) -> list[str]:
    """Save files for photo/document updates and log text messages."""
    saved_files: list[str] = []

    if message.text:
        print(f"[telegram] chat_id={message.chat_id} text={message.text}")

    if message.photos:
        best_photo = message.photos[-1]
        photo_path: Path = download_dir / f"photo_{message.message_id}.jpg"
        bot.download_file(file_id=best_photo.file_id, destination=photo_path)
        saved_files.append(str(photo_path))
        print(f"[telegram] saved photo={photo_path}")

    if message.document:
        raw_file_name: str = (
            message.document.file_name or f"document_{message.message_id}.bin"
        )
        file_name: str = _safe_file_name(raw_file_name)
        document_path: Path = download_dir / f"{message.message_id}_{file_name}"
        bot.download_file(file_id=message.document.file_id, destination=document_path)
        saved_files.append(str(document_path))
        print(f"[telegram] saved document={document_path}")

    return saved_files


def _safe_file_name(file_name: str) -> str:
    return Path(file_name).name
