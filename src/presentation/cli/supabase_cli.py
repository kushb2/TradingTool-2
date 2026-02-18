"""CLI commands for Supabase checks."""

from __future__ import annotations

import argparse
import json
import sys

from src.infrastructure.supabase import SupabaseClientError, SupabaseClientProvider


def main() -> None:
    """Run Supabase CLI."""
    parser = argparse.ArgumentParser(description="Supabase CLI")
    parser.add_argument(
        "command",
        choices=["health"],
        help="Command to execute.",
    )
    parser.add_argument(
        "--url-env-var",
        default="SUPABASE_URL",
        help="Environment variable name for Supabase URL.",
    )
    parser.add_argument(
        "--key-env-var",
        default="SUPABASE_KEY",
        help="Environment variable name for Supabase key.",
    )
    args = parser.parse_args()

    if args.command == "health":
        _run_health(
            url_env_var=args.url_env_var,
            key_env_var=args.key_env_var,
        )


def _run_health(url_env_var: str, key_env_var: str) -> None:
    try:
        provider: SupabaseClientProvider = SupabaseClientProvider.from_env(
            url_env_var=url_env_var,
            key_env_var=key_env_var,
        )
        health_status = provider.check_connection()
    except SupabaseClientError as error:
        print(f"[supabase] health check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    print(json.dumps(health_status.model_dump(), indent=2))


if __name__ == "__main__":
    main()
