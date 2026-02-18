"""CLI utilities to manage Telegram webhook registration."""

from __future__ import annotations

import argparse
import os

from src.infrastructure.telegram import TelegramBotModule


def _build_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Manage Telegram webhook for FastAPI deployment."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_parser = subparsers.add_parser("set", help="Register webhook URL")
    set_parser.add_argument(
        "--public-base-url",
        type=str,
        help="Public backend base URL (fallback: RENDER_EXTERNAL_URL)",
    )
    set_parser.add_argument(
        "--webhook-path",
        type=str,
        default="/telegram/webhook",
        help="Webhook path in FastAPI app",
    )
    set_parser.add_argument(
        "--secret-token",
        type=str,
        help="Telegram webhook secret token (fallback: TELEGRAM_WEBHOOK_SECRET)",
    )
    set_parser.add_argument(
        "--drop-pending-updates",
        action="store_true",
        help="Drop pending updates while setting webhook",
    )

    subparsers.add_parser("info", help="Show webhook info")

    delete_parser = subparsers.add_parser("delete", help="Delete webhook")
    delete_parser.add_argument(
        "--drop-pending-updates",
        action="store_true",
        help="Drop pending updates while deleting webhook",
    )
    return parser


def _resolve_public_base_url(cli_value: str | None) -> str:
    if cli_value is not None and cli_value.strip() != "":
        return cli_value.strip().rstrip("/")

    env_value: str | None = os.getenv("RENDER_EXTERNAL_URL")
    if env_value is None or env_value.strip() == "":
        raise ValueError(
            "Missing public base URL. Use '--public-base-url' or set "
            "RENDER_EXTERNAL_URL."
        )
    return env_value.strip().rstrip("/")


def _resolve_secret_token(cli_value: str | None) -> str | None:
    if cli_value is not None and cli_value.strip() != "":
        return cli_value.strip()

    env_value: str | None = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if env_value is None or env_value.strip() == "":
        return None
    return env_value.strip()


def _build_webhook_url(public_base_url: str, webhook_path: str) -> str:
    normalized_path: str = webhook_path.strip()
    if normalized_path == "":
        raise ValueError("Webhook path cannot be empty.")
    if not normalized_path.startswith("/"):
        normalized_path = f"/{normalized_path}"
    return f"{public_base_url}{normalized_path}"


def _print_webhook_info(info: dict[str, object]) -> None:
    print(f"url={info.get('url')}")
    print(f"pending_update_count={info.get('pending_update_count')}")
    print(f"last_error_message={info.get('last_error_message')}")
    print(f"last_error_date={info.get('last_error_date')}")
    print(f"max_connections={info.get('max_connections')}")
    print(f"ip_address={info.get('ip_address')}")


def main() -> None:
    parser: argparse.ArgumentParser = _build_parser()
    args: argparse.Namespace = parser.parse_args()

    bot: TelegramBotModule = TelegramBotModule.from_env()

    if args.command == "set":
        public_base_url: str = _resolve_public_base_url(args.public_base_url)
        webhook_url: str = _build_webhook_url(public_base_url, args.webhook_path)
        secret_token: str | None = _resolve_secret_token(args.secret_token)

        success: bool = bot.set_webhook(
            webhook_url=webhook_url,
            secret_token=secret_token,
            drop_pending_updates=args.drop_pending_updates,
        )
        if not success:
            raise RuntimeError("Telegram setWebhook returned false")

        print(f"Webhook set: {webhook_url}")
        if secret_token is not None:
            print("Secret token: configured")
        else:
            print("Secret token: not set")
        _print_webhook_info(bot.get_webhook_info())
        return

    if args.command == "info":
        _print_webhook_info(bot.get_webhook_info())
        return

    if args.command == "delete":
        success = bot.delete_webhook(
            drop_pending_updates=args.drop_pending_updates,
        )
        if not success:
            raise RuntimeError("Telegram deleteWebhook returned false")
        print("Webhook deleted")
        _print_webhook_info(bot.get_webhook_info())
        return


if __name__ == "__main__":
    main()
