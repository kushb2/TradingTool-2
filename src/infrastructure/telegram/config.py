"""Telegram configuration models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramConfig:
    """Configuration required to call Telegram Bot API."""

    token: str
    request_timeout_seconds: float = 30.0
