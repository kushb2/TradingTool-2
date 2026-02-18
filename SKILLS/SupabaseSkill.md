# SupabaseSkill

## Metadata
* **Skill Name:** SupabaseSkill
* **Version:** 1.0
* **Scope:** Infrastructure Layer (Persistence)
* **Target Stack:** `supabase-py` (Python Client), Pydantic

## Purpose
To standardize interactions with Supabase, ensuring that "Schemaless" JSON responses from the database are immediately converted into strict, typed Pydantic models before entering the Application layer. This skill treats Supabase as a "dumb" data store and prevents vendor lock-in leakage into the Domain.

## Setup & Configuration
* **Environment Variables:**
    * `SUPABASE_URL`: The API URL.
    * `SUPABASE_KEY`: The Service Role Key (since this is a backend script/bot, use Service Role to bypass RLS for simplicity, or Anon Key if RLS is configured).
* **Client Initialization:**
    * Use a Singleton or Dependency Injection to initialize `create_client` once.
    * **Location:** `src/infrastructure/external/supabase_client.py`.

## Core Integration Rules

### 1. Isolation (Architecture Enforcement)
* **Strict Boundary:** The `supabase` library must **NEVER** be imported in `domain` or `application` layers.
* **Gateway:** All Supabase logic resides in `src/infrastructure/repositories/`.

### 2. The "No-Dict" Policy (Strict Typing)
* Supabase returns raw Python dictionaries (`dict`).
* **Rule:** You must convert these `dicts` to **Pydantic Models** (Domain Entities) *immediately* upon fetching.
* **Prohibited:** Returning `response.data` directly to a Service.

### 3. Error Handling
* Wrap `postgrest.exceptions.APIError` or network errors into custom Domain Exceptions (e.g., `RepositoryError`).

## Coding Standards (Simplicity + Typing)

### Fetching Data
Use the method-chaining syntax for readability.

**Bad (Untyped, leaky):**
```python
# Returns dict, caller doesn't know structure
def get_trades():
    return supabase.table("trades").select("*").execute().data




