"""Typed Supabase models."""

from pydantic import BaseModel


class SupabaseHealthStatus(BaseModel):
    """Structured result from a Supabase connectivity check."""

    ok: bool
    status_code: int
    project_ref: str | None
    schema_version: str | None
