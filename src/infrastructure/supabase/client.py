"""Typed Supabase client provider and health checks."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from httpx import HTTPError, Response
from supabase import Client, create_client

from .config import SupabaseConfig
from .models import SupabaseHealthStatus


class SupabaseClientError(RuntimeError):
    """Raised when Supabase configuration or API calls fail."""


@dataclass
class SupabaseClientProvider:
    """Create and reuse a single Supabase client instance."""

    config: SupabaseConfig
    _client: Client | None = None

    @classmethod
    def from_env(
        cls,
        url_env_var: str = "SUPABASE_URL",
        key_env_var: str = "SUPABASE_KEY",
    ) -> SupabaseClientProvider:
        """Build provider from environment variables."""
        load_dotenv()

        raw_url: str | None = os.getenv(url_env_var)
        url: str | None = _clean_env_value(raw_url)
        if url is None:
            raise SupabaseClientError(
                f"Missing Supabase URL. Set environment variable '{url_env_var}'."
            )

        raw_key: str | None = os.getenv(key_env_var)
        key: str | None = _clean_env_value(raw_key)
        if key is None:
            fallback_key: str | None = _clean_env_value(
                os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            )
            if fallback_key is None:
                raise SupabaseClientError(
                    "Missing Supabase key. Set environment variable "
                    f"'{key_env_var}' or 'SUPABASE_SERVICE_ROLE_KEY'."
                )
            key = fallback_key

        config: SupabaseConfig = SupabaseConfig(url=url, key=key)
        return cls(config=config)

    def get_client(self) -> Client:
        """Return memoized Supabase client."""
        if self._client is None:
            self._client = create_client(self.config.url, self.config.key)
        return self._client

    def check_connection(self) -> SupabaseHealthStatus:
        """Check Data API reachability and return typed health status."""
        client: Client = self.get_client()
        rest_url: str = str(client.rest_url)
        endpoint: str = f"{rest_url}/"

        try:
            response: Response = client.postgrest.session.get(
                endpoint,
                timeout=self.config.request_timeout_seconds,
            )
        except HTTPError as error:
            raise SupabaseClientError(
                f"Supabase connection failed: {error}"
            ) from error

        if response.status_code != 200:
            raise SupabaseClientError(
                "Supabase health check failed with status "
                f"{response.status_code}: {response.text}"
            )

        project_ref: str | None = _clean_env_value(
            response.headers.get("sb-project-ref")
        )
        schema_version: str | None = _extract_schema_version(response=response)

        return SupabaseHealthStatus(
            ok=True,
            status_code=response.status_code,
            project_ref=project_ref,
            schema_version=schema_version,
        )


def _clean_env_value(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    cleaned_value: str = raw_value.strip()
    if cleaned_value == "":
        return None
    return cleaned_value


def _extract_schema_version(response: Response) -> str | None:
    payload: object
    try:
        payload = response.json()
    except ValueError:
        return None

    if not isinstance(payload, dict):
        return None

    info: object = payload.get("info")
    if not isinstance(info, dict):
        return None

    raw_version: object = info.get("version")
    if isinstance(raw_version, str) and raw_version.strip() != "":
        return raw_version
    return None
