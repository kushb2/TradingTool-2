"""ASGI entrypoint compatibility module for Render dashboard start command."""

from src.presentation.api.telegram_webhook_app import app

__all__ = ["app"]
