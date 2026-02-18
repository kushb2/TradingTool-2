"""High-level plug-and-play Telegram module."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv

from .client import TelegramApiClient, TelegramApiError, parse_update_message
from .config import TelegramConfig
from .models import TelegramMessage

TelegramMessageHandler = Callable[[TelegramMessage], None]


class TelegramBotModule:
    """Facade for sending and receiving Telegram bot messages."""

    def __init__(
        self,
        client: TelegramApiClient,
        poll_timeout_seconds: int = 60,
        error_retry_sleep_seconds: float = 1.0,
        max_retry_sleep_seconds: float = 30.0,
    ) -> None:
        self._client: TelegramApiClient = client
        self._poll_timeout_seconds: int = poll_timeout_seconds
        self._error_retry_sleep_seconds: float = error_retry_sleep_seconds
        self._max_retry_sleep_seconds: float = max_retry_sleep_seconds
        self._next_update_id: int | None = None

    @classmethod
    def from_token(
        cls,
        token: str,
        poll_timeout_seconds: int = 60,
        request_timeout_seconds: float = 75.0,
        error_retry_sleep_seconds: float = 1.0,
        max_retry_sleep_seconds: float = 30.0,
    ) -> TelegramBotModule:
        min_request_timeout_seconds: float = float(poll_timeout_seconds) + 5.0
        effective_request_timeout: float = max(
            request_timeout_seconds, min_request_timeout_seconds
        )
        config: TelegramConfig = TelegramConfig(
            token=token,
            request_timeout_seconds=effective_request_timeout,
        )
        client: TelegramApiClient = TelegramApiClient(config=config)
        return cls(
            client=client,
            poll_timeout_seconds=poll_timeout_seconds,
            error_retry_sleep_seconds=error_retry_sleep_seconds,
            max_retry_sleep_seconds=max_retry_sleep_seconds,
        )

    @classmethod
    def from_env(
        cls,
        token_env_var: str = "TELEGRAM_BOT_TOKEN",
        poll_timeout_seconds: int = 60,
        request_timeout_seconds: float = 75.0,
        error_retry_sleep_seconds: float = 1.0,
        max_retry_sleep_seconds: float = 30.0,
    ) -> TelegramBotModule:
        load_dotenv()
        token: str | None = os.getenv(token_env_var)
        if token is None or token.strip() == "":
            raise ValueError(
                "Missing Telegram bot token. "
                f"Set environment variable '{token_env_var}' or add it to .env."
            )
        cleaned_token: str = token.strip()
        if ":" not in cleaned_token:
            raise ValueError(
                "Invalid Telegram bot token format. "
                "Expected '<bot_id>:<secret>' from BotFather."
            )
        env_poll_timeout_seconds: int = _get_env_int(
            env_var_name="TELEGRAM_POLL_TIMEOUT_SECONDS",
            default_value=poll_timeout_seconds,
            minimum_value=1,
        )
        env_request_timeout_seconds: float = _get_env_float(
            env_var_name="TELEGRAM_REQUEST_TIMEOUT_SECONDS",
            default_value=request_timeout_seconds,
            minimum_value=1.0,
        )
        env_error_retry_sleep_seconds: float = _get_env_float(
            env_var_name="TELEGRAM_ERROR_RETRY_SLEEP_SECONDS",
            default_value=error_retry_sleep_seconds,
            minimum_value=0.1,
        )
        env_max_retry_sleep_seconds: float = _get_env_float(
            env_var_name="TELEGRAM_MAX_RETRY_SLEEP_SECONDS",
            default_value=max_retry_sleep_seconds,
            minimum_value=0.1,
        )
        return cls.from_token(
            token=cleaned_token,
            poll_timeout_seconds=env_poll_timeout_seconds,
            request_timeout_seconds=env_request_timeout_seconds,
            error_retry_sleep_seconds=env_error_retry_sleep_seconds,
            max_retry_sleep_seconds=max(
                env_error_retry_sleep_seconds,
                env_max_retry_sleep_seconds,
            ),
        )

    def send_text(self, chat_id: int, text: str) -> int:
        """Send text message to a Telegram chat."""
        return self._client.send_message(chat_id=chat_id, text=text)

    def poll_once(self) -> list[TelegramMessage]:
        """Fetch the next batch of messages using long polling."""
        messages: list[TelegramMessage] = self._client.get_updates(
            offset=self._next_update_id,
            timeout_seconds=self._poll_timeout_seconds,
        )
        if not messages:
            return []

        highest_update_id: int = max(message.update_id for message in messages)
        self._next_update_id = highest_update_id + 1
        return messages

    def listen_forever(
        self,
        handler: TelegramMessageHandler,
        idle_sleep_seconds: float = 0.1,
    ) -> None:
        """Listen for new messages forever and dispatch each one to `handler`."""
        retry_sleep_seconds: float = self._error_retry_sleep_seconds
        while True:
            try:
                messages: list[TelegramMessage] = self.poll_once()
            except TelegramApiError as error:
                # Long-polling can intermittently timeout; keep listener alive.
                print(
                    f"[telegram] polling error: {error}. "
                    f"Retrying in {retry_sleep_seconds:.1f}s."
                )
                time.sleep(retry_sleep_seconds)
                retry_sleep_seconds = min(
                    retry_sleep_seconds * 2.0,
                    self._max_retry_sleep_seconds,
                )
                continue
            except Exception as error:
                print(
                    f"[telegram] unexpected listener error: {error}. "
                    f"Retrying in {retry_sleep_seconds:.1f}s."
                )
                time.sleep(retry_sleep_seconds)
                retry_sleep_seconds = min(
                    retry_sleep_seconds * 2.0,
                    self._max_retry_sleep_seconds,
                )
                continue

            retry_sleep_seconds = self._error_retry_sleep_seconds
            if not messages:
                time.sleep(idle_sleep_seconds)
                continue
            for message in messages:
                try:
                    handler(message)
                except Exception as error:
                    print(
                        f"[telegram] handler error for update "
                        f"{message.update_id}: {error}"
                    )

    def download_file(self, file_id: str, destination: Path) -> Path:
        """Download photo/document from Telegram by file id."""
        return self._client.download_file(file_id=file_id, destination=destination)

    def parse_update_message(self, raw_update: object) -> TelegramMessage | None:
        """Parse a raw Telegram update payload into a message if present."""
        return parse_update_message(raw_update)

    def set_webhook(
        self,
        webhook_url: str,
        secret_token: str | None = None,
        drop_pending_updates: bool = False,
    ) -> bool:
        """Register webhook URL with Telegram Bot API."""
        return self._client.set_webhook(
            webhook_url=webhook_url,
            secret_token=secret_token,
            drop_pending_updates=drop_pending_updates,
        )

    def delete_webhook(self, drop_pending_updates: bool = False) -> bool:
        """Remove webhook registration from Telegram Bot API."""
        return self._client.delete_webhook(drop_pending_updates=drop_pending_updates)

    def get_webhook_info(self) -> dict[str, object]:
        """Get Telegram webhook configuration and delivery stats."""
        return self._client.get_webhook_info()


def _get_env_int(
    env_var_name: str,
    default_value: int,
    minimum_value: int,
) -> int:
    raw_value: str | None = os.getenv(env_var_name)
    if raw_value is None or raw_value.strip() == "":
        return default_value
    try:
        parsed_value: int = int(raw_value.strip())
    except ValueError as error:
        raise ValueError(
            f"Invalid value for {env_var_name}. Expected integer."
        ) from error
    if parsed_value < minimum_value:
        raise ValueError(
            f"Invalid value for {env_var_name}. "
            f"Expected >= {minimum_value}."
        )
    return parsed_value


def _get_env_float(
    env_var_name: str,
    default_value: float,
    minimum_value: float,
) -> float:
    raw_value: str | None = os.getenv(env_var_name)
    if raw_value is None or raw_value.strip() == "":
        return default_value
    try:
        parsed_value: float = float(raw_value.strip())
    except ValueError as error:
        raise ValueError(
            f"Invalid value for {env_var_name}. Expected number."
        ) from error
    if parsed_value < minimum_value:
        raise ValueError(
            f"Invalid value for {env_var_name}. "
            f"Expected >= {minimum_value}."
        )
    return parsed_value
