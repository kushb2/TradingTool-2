"""High-level plug-and-play Telegram module."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from pathlib import Path

from .client import TelegramApiClient
from .config import TelegramConfig
from .models import TelegramMessage

TelegramMessageHandler = Callable[[TelegramMessage], None]


class TelegramBotModule:
    """Facade for sending and receiving Telegram bot messages."""

    def __init__(
        self, client: TelegramApiClient, poll_timeout_seconds: int = 30
    ) -> None:
        self._client: TelegramApiClient = client
        self._poll_timeout_seconds: int = poll_timeout_seconds
        self._next_update_id: int | None = None

    @classmethod
    def from_token(
        cls, token: str, poll_timeout_seconds: int = 30
    ) -> TelegramBotModule:
        config: TelegramConfig = TelegramConfig(token=token)
        client: TelegramApiClient = TelegramApiClient(config=config)
        return cls(client=client, poll_timeout_seconds=poll_timeout_seconds)

    @classmethod
    def from_env(
        cls,
        token_env_var: str = "TELEGRAM_BOT_TOKEN",
        poll_timeout_seconds: int = 30,
    ) -> TelegramBotModule:
        token: str | None = os.getenv(token_env_var)
        if token is None or token.strip() == "":
            raise ValueError(
                "Missing Telegram bot token. "
                f"Set environment variable '{token_env_var}'."
            )
        return cls.from_token(
            token=token.strip(), poll_timeout_seconds=poll_timeout_seconds
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
        idle_sleep_seconds: float = 0.3,
    ) -> None:
        """Listen for new messages forever and dispatch each one to `handler`."""
        while True:
            messages: list[TelegramMessage] = self.poll_once()
            if not messages:
                time.sleep(idle_sleep_seconds)
                continue
            for message in messages:
                handler(message)

    def download_file(self, file_id: str, destination: Path) -> Path:
        """Download photo/document from Telegram by file id."""
        return self._client.download_file(file_id=file_id, destination=destination)
