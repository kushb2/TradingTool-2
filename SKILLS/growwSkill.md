# GrowwSkill

## Metadata
* **Skill Name:** GrowwSkill
* **Version:** 1.0
* **Scope:** Infrastructure Layer (External Adapters)
* **Target:** Groww Trading API (Python SDK / Wrapper)

## Purpose
To encapsulate all interactions with the Groww Broker API. This skill acts as a strict **Anti-Corruption Layer**, preventing vendor-specific objects (like Groww's raw JSON or dicts) from leaking into the Domain or Application layers. It also enforces safety mechanisms to prevent accidental financial loss during development.

## Core Principles

### 1. The Adapter Pattern (Strict Isolation)
* **Rule:** The rest of the application must **NEVER** import the `groww` SDK directly.
* **Mechanism:** * Define an abstract interface in `src/application/interfaces/broker.py` (e.g., `BrokerClient`).
    * Implement the Groww logic in `src/infrastructure/external/groww_client.py`.

### 2. Safety First (Paper Trading Mode)
* **Rule:** All order placement methods must respect a global `PAPER_TRADING_MODE` config flag.
* **Behavior:**
    * If `PAPER_TRADING_MODE = True`: Log the order intention to the console/DB but **DO NOT** send it to Groww. Return a fake "Success" ID.
    * If `PAPER_TRADING_MODE = False`: Execute the real trade.

### 3. Data Normalization
* Groww (like many brokers) returns data in non-standard formats (e.g., list of lists for candles, specific keys for quotes).
* **Mandate:** Convert raw responses into your strict **Domain Entities** (Pydantic models) *immediately* inside the adapter before returning.

## Coding Standards

### Authentication & Session Management
* **Login Logic:** Encapsulate the login flow (TOTP / Pin) inside the `__init__` or a `connect()` method. 
* **Token Refresh:** Handle session expiry automatically within the adapter. The Application layer should not know that a token expired; it should just work.

### Error Handling
* **Map Errors:** Catch Groww-specific exceptions (e.g., `GrowwAPIError`, `ConnectTimeout`) and raise clean **Domain Exceptions** (e.g., `BrokerConnectionError`, `InsufficientFundsError`).

### Example Implementation

**Interface (Application Layer):**
```python
# src/application/interfaces/broker.py
from typing import Protocol
from src.domain.models.order import OrderRequest, OrderResponse

class BrokerClient(Protocol):
    def place_order(self, order: OrderRequest) -> OrderResponse:
        ...
    
    def get_ltp(self, symbol: str) -> float:
        ...