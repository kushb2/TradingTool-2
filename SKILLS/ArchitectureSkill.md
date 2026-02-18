# ArchitectureSkill

## Goal
Define a simple, maintainable architecture for a single-user Python trading tool.

## Rules
1. Dependencies point inward: `presentation -> application -> domain`.
2. `domain` stays pure Python (no DB, HTTP, framework imports).
3. `application` defines ports (`Protocol`) and use cases.
4. `infrastructure` implements ports and owns external integrations.
5. All functions and methods use explicit type hints.

## Project Structure (V1)

```text
TradingTool-2/
├── src/
│   ├── main.py
│   ├── presentation/
│   │   └── cli/
│   │       └── run.py
│   ├── application/
│   │   ├── dtos/
│   │   │   └── trade_dto.py
│   │   ├── ports/
│   │   │   ├── market_data_port.py
│   │   │   └── order_port.py
│   │   └── services/
│   │       └── execute_trade_service.py
│   ├── domain/
│   │   ├── entities/
│   │   │   └── trade.py
│   │   ├── value_objects/
│   │   │   ├── price.py
│   │   │   └── symbol.py
│   │   └── rules/
│   │       └── risk_checks.py
│   ├── infrastructure/
│   │   ├── brokers/
│   │   │   └── groww_order_adapter.py
│   │   ├── market_data/
│   │   │   └── yahoo_market_data_adapter.py
│   │   └── persistence/
│   │       └── sqlite_trade_repository.py
│   └── shared/
│       ├── types.py
│       └── clock.py
├── tests/
│   ├── unit/
│   └── integration/
├── SKILLS/
│   └── ArchitectureSkill.md
└── pyproject.toml
```

## Layer Responsibilities

### `src/presentation`
- Parse input/output only.
- Call application services.
- No business rules or direct DB/API calls.

### `src/application`
- Coordinate use cases.
- Use `Protocol` ports for dependencies.
- Convert between DTOs and domain objects.

### `src/domain`
- Own trading rules and invariants.
- Keep models small and explicit.
- No third-party side effects.

### `src/infrastructure`
- Implement ports from `application`.
- Handle APIs, DB, files, retries, auth.
- Keep mapping code near adapter implementations.

## Coding Conventions
- Mandatory type hints for args and returns.
- Avoid `Any`; prefer concrete models or `Protocol`.
- Keep functions short and readable.
- Add complexity only when currently needed (YAGNI).

## Initial Build Order
1. Create domain models (`symbol`, `price`, `trade`) with validations.
2. Add application ports and one service (`execute_trade_service`).
3. Add one broker adapter and one market data adapter.
4. Wire CLI entrypoint to service.
5. Add unit tests for domain and service logic.
