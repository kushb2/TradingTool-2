"""Command-line entrypoint for Telegram bot module."""

from __future__ import annotations

import argparse
import os
from datetime import UTC, datetime
from pathlib import Path

from src.infrastructure.telegram import TelegramBotModule, TelegramMessage


def _build_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Telegram bot CLI (send messages, receive text/photos/documents)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send", help="Send a text message")
    send_parser.add_argument(
        "--chat-id",
        type=int,
        help="Target Telegram chat id (optional if TELEGRAM_CHAT_ID is set)",
    )
    send_parser.add_argument("--text", type=str, required=True, help="Text to send")

    listen_parser = subparsers.add_parser(
        "listen",
        help="Listen to incoming messages and save photos/documents",
    )
    listen_parser.add_argument(
        "--download-dir",
        type=Path,
        default=Path("data/telegram_downloads"),
        help="Directory to save downloaded files",
    )
    return parser


def _format_message(message: TelegramMessage) -> str:
    dt: datetime = datetime.fromtimestamp(message.date_unix, tz=UTC)
    return (
        f"update_id={message.update_id} chat_id={message.chat_id} "
        f"message_id={message.message_id} utc={dt.isoformat()}"
    )


def _safe_file_name(file_name: str) -> str:
    return Path(file_name).name


def _resolve_chat_id(chat_id: int | None) -> int:
    if chat_id is not None:
        return chat_id

    env_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID")
    if env_chat_id is None or env_chat_id.strip() == "":
        raise ValueError(
            "Missing chat id. Use '--chat-id' or set TELEGRAM_CHAT_ID in .env."
        )
    try:
        return int(env_chat_id.strip())
    except ValueError as error:
        raise ValueError(
            "Invalid TELEGRAM_CHAT_ID. Expected integer chat id."
        ) from error


def main() -> None:
    parser: argparse.ArgumentParser = _build_parser()
    args: argparse.Namespace = parser.parse_args()
    bot: TelegramBotModule = TelegramBotModule.from_env()

    if args.command == "send":
        chat_id: int = _resolve_chat_id(args.chat_id)
        message_id: int = bot.send_text(chat_id=chat_id, text=args.text)
        print(f"Sent message_id={message_id} to chat_id={chat_id}")
        return

    download_dir: Path = args.download_dir
    download_dir.mkdir(parents=True, exist_ok=True)
    print(f"Listening for incoming messages. Download dir: {download_dir}")

    def handle_message(message: TelegramMessage) -> None:
        print(_format_message(message))

        if message.text:
            print(f"text={message.text}")

        if message.photos:
            best_photo = message.photos[-1]
            photo_path: Path = download_dir / f"photo_{message.message_id}.jpg"
            bot.download_file(file_id=best_photo.file_id, destination=photo_path)
            print(f"photo_saved={photo_path}")

        if message.document:
            raw_file_name: str = (
                message.document.file_name or f"document_{message.message_id}.bin"
            )
            file_name: str = _safe_file_name(raw_file_name)
            document_path: Path = download_dir / f"{message.message_id}_{file_name}"
            bot.download_file(
                file_id=message.document.file_id, destination=document_path
            )
            print(f"document_saved={document_path}")

    bot.listen_forever(handler=handle_message)


if __name__ == "__main__":
    main()
