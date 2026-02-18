"""Low-level Telegram Bot API client."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import TelegramConfig
from .models import TelegramDocument, TelegramMessage, TelegramPhoto


class TelegramApiError(RuntimeError):
    """Raised when Telegram API returns an error payload."""


class TelegramApiClient:
    """Minimal typed client for Telegram Bot API."""

    def __init__(self, config: TelegramConfig) -> None:
        self._config: TelegramConfig = config
        self._api_base_url: str = f"https://api.telegram.org/bot{config.token}"
        self._file_base_url: str = f"https://api.telegram.org/file/bot{config.token}"

    def send_message(self, chat_id: int, text: str) -> int:
        payload: dict[str, object] = {"chat_id": chat_id, "text": text}
        response: dict[str, object] = self._post_json("sendMessage", payload)
        result: dict[str, object] = _require_dict(response.get("result"), "result")
        return _require_int(result.get("message_id"), "message_id")

    def get_updates(
        self,
        offset: int | None = None,
        timeout_seconds: int = 30,
    ) -> list[TelegramMessage]:
        payload: dict[str, object] = {"timeout": timeout_seconds}
        if offset is not None:
            payload["offset"] = offset

        response: dict[str, object] = self._post_json("getUpdates", payload)
        raw_updates: list[object] = _require_list(response.get("result"), "result")

        parsed_messages: list[TelegramMessage] = []
        for raw_update in raw_updates:
            update_map: dict[str, object] = _require_dict(raw_update, "update")
            maybe_message: object | None = update_map.get("message")
            if maybe_message is None:
                continue

            message_map: dict[str, object] = _require_dict(maybe_message, "message")
            parsed_messages.append(
                _parse_message(update_map=update_map, message_map=message_map)
            )
        return parsed_messages

    def get_file_path(self, file_id: str) -> str:
        payload: dict[str, object] = {"file_id": file_id}
        response: dict[str, object] = self._post_json("getFile", payload)
        result: dict[str, object] = _require_dict(response.get("result"), "result")
        return _require_str(result.get("file_path"), "file_path")

    def download_file(self, file_id: str, destination: Path) -> Path:
        file_path: str = self.get_file_path(file_id)
        file_url: str = f"{self._file_base_url}/{file_path}"

        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urlopen(
                file_url, timeout=self._config.request_timeout_seconds
            ) as response:
                content: bytes = response.read()
        except (HTTPError, URLError) as error:
            raise TelegramApiError(
                f"Failed to download file from Telegram: {error}"
            ) from error

        destination.write_bytes(content)
        return destination

    def _post_json(self, method: str, payload: dict[str, object]) -> dict[str, object]:
        url: str = f"{self._api_base_url}/{method}"
        encoded_payload: bytes = json.dumps(payload).encode("utf-8")
        request: Request = Request(
            url=url,
            data=encoded_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(
                request, timeout=self._config.request_timeout_seconds
            ) as response:
                body: bytes = response.read()
        except (HTTPError, URLError) as error:
            raise TelegramApiError(
                f"HTTP request to Telegram failed: {error}"
            ) from error

        decoded: object = json.loads(body.decode("utf-8"))
        data: dict[str, object] = _require_dict(decoded, "response")
        ok: bool = _require_bool(data.get("ok"), "ok")
        if not ok:
            description: str = (
                _optional_str(data.get("description")) or "Unknown Telegram API error"
            )
            error_code: int | None = _optional_int(data.get("error_code"))
            if error_code is None:
                raise TelegramApiError(description)
            raise TelegramApiError(f"Telegram error {error_code}: {description}")
        return data


def _parse_message(
    update_map: dict[str, object], message_map: dict[str, object]
) -> TelegramMessage:
    chat_map: dict[str, object] = _require_dict(message_map.get("chat"), "chat")
    from_user_map: dict[str, object] | None = _optional_dict(message_map.get("from"))
    raw_photos: list[object] = _optional_list(message_map.get("photo")) or []
    photos: list[TelegramPhoto] = [_parse_photo(raw_photo) for raw_photo in raw_photos]

    document: TelegramDocument | None = None
    raw_document: object | None = message_map.get("document")
    if raw_document is not None:
        document = _parse_document(raw_document)

    return TelegramMessage(
        update_id=_require_int(update_map.get("update_id"), "update_id"),
        message_id=_require_int(message_map.get("message_id"), "message_id"),
        chat_id=_require_int(chat_map.get("id"), "chat.id"),
        from_user_id=_optional_int(from_user_map.get("id")) if from_user_map else None,
        text=_optional_str(message_map.get("text")),
        caption=_optional_str(message_map.get("caption")),
        photos=tuple(photos),
        document=document,
        date_unix=_require_int(message_map.get("date"), "date"),
    )


def _parse_photo(raw_photo: object) -> TelegramPhoto:
    photo_map: dict[str, object] = _require_dict(raw_photo, "photo")
    return TelegramPhoto(
        file_id=_require_str(photo_map.get("file_id"), "photo.file_id"),
        file_unique_id=_require_str(
            photo_map.get("file_unique_id"), "photo.file_unique_id"
        ),
        width=_require_int(photo_map.get("width"), "photo.width"),
        height=_require_int(photo_map.get("height"), "photo.height"),
        file_size=_optional_int(photo_map.get("file_size")),
    )


def _parse_document(raw_document: object) -> TelegramDocument:
    document_map: dict[str, object] = _require_dict(raw_document, "document")
    return TelegramDocument(
        file_id=_require_str(document_map.get("file_id"), "document.file_id"),
        file_unique_id=_require_str(
            document_map.get("file_unique_id"), "document.file_unique_id"
        ),
        file_name=_optional_str(document_map.get("file_name")),
        mime_type=_optional_str(document_map.get("mime_type")),
        file_size=_optional_int(document_map.get("file_size")),
    )


def _require_dict(value: object | None, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TelegramApiError(f"Expected object for '{field_name}'")
    return cast(dict[str, object], value)


def _optional_dict(value: object | None) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TelegramApiError("Expected object")
    return cast(dict[str, object], value)


def _require_list(value: object | None, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise TelegramApiError(f"Expected list for '{field_name}'")
    return value


def _optional_list(value: object | None) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise TelegramApiError("Expected list")
    return value


def _require_int(value: object | None, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TelegramApiError(f"Expected integer for '{field_name}'")
    return value


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TelegramApiError("Expected integer")
    return value


def _require_str(value: object | None, field_name: str) -> str:
    if not isinstance(value, str):
        raise TelegramApiError(f"Expected string for '{field_name}'")
    return value


def _optional_str(value: object | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TelegramApiError("Expected string")
    return value


def _require_bool(value: object | None, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TelegramApiError(f"Expected boolean for '{field_name}'")
    return value
