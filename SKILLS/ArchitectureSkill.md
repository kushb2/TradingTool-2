# ArchitectureSkill

## Goal
Define a simple, maintainable architecture for a single-user Python trading tool.

## Architecture Rules
1. Dependencies point inward: `presentation -> application -> domain`.
2. `domain` stays pure Python (no DB, HTTP, framework imports).
3. `application` defines ports (`Protocol`) and use cases.
4. `infrastructure` implements ports and owns external integrations.
5. All functions and methods use explicit type hints.

## Current Structure (Phase 1: Telegram + Webhook)
This is the real structure today. `application` and `domain` are intentionally deferred (YAGNI) until trading use cases are added.

```text
TradingTool-2/
├── src/
│   ├── main.py
│   ├── presentation/
│   │   ├── api/
│   │   │   └── telegram_webhook_app.py
│   │   └── cli/
│   │       ├── telegram_cli.py
│   │       └── telegram_webhook_cli.py
│   └── infrastructure/
│       └── telegram/
│           ├── client.py
│           ├── config.py
│           ├── models.py
│           └── module.py
├── tests/
├── SKILLS/
│   └── ArchitectureSkill.md
└── pyproject.toml
```

## Layer Responsibilities (Current)
### `src/presentation`
- Owns I/O concerns (CLI args, HTTP request/response handling).
- Delegates Telegram operations to infrastructure module.
- Must not hold trading decision logic.

### `src/infrastructure`
- Owns Telegram API client, parsing, retries, downloads, webhook helpers.
- Contains integration-specific models/config.
- Keeps external API details out of presentation code.

## Target Structure (Phase 2+)
When trading logic is implemented, introduce `application` and `domain`:

```text
src/
├── presentation/
├── application/
│   ├── ports/
│   └── services/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   └── rules/
└── infrastructure/
```

## Migration Plan
1. Add `domain` models first (`symbol`, `price`, `trade`) with validation.
2. Add `application` use cases and `Protocol` ports.
3. Move trading workflows from presentation into application services.
4. Keep infrastructure as adapter implementations for those ports.
5. Add unit tests for domain/application and integration tests for infrastructure.

## Coding Conventions
- Mandatory type hints for args and returns.
- Avoid `Any`; prefer concrete models or `Protocol`.
- Keep functions short and readable.
- Readability over optimization.
- Add complexity only when currently needed (YAGNI).
