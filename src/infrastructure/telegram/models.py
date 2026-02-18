"""Typed Telegram models used by the module."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramPhoto:
    """Photo metadata sent by Telegram."""

    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int | None


@dataclass(frozen=True)
class TelegramDocument:
    """Document metadata sent by Telegram."""

    file_id: str
    file_unique_id: str
    file_name: str | None
    mime_type: str | None
    file_size: int | None


@dataclass(frozen=True)
class TelegramMessage:
    """Normalized incoming message from Telegram updates."""

    update_id: int
    message_id: int
    chat_id: int
    from_user_id: int | None
    text: str | None
    caption: str | None
    photos: tuple[TelegramPhoto, ...]
    document: TelegramDocument | None
    date_unix: int
