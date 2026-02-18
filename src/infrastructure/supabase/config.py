"""Supabase configuration models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SupabaseConfig:
    """Configuration required to initialize a Supabase client."""

    url: str
    key: str
    request_timeout_seconds: float = 10.0
