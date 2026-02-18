# SimplicitySkill

## Metadata
* **Skill Name:** SimplicitySkill
* **Version:** 1.0
* **Scope:** Personal Python Trading Tool
* **Target User:** Single Developer/Trader (You)

## Purpose
To aggressively prioritize code **readability** and **maintainability** over optimization or clever abstractions. The primary goal is to minimize the time spent on "software engineering" so the user can focus on "trading logic."

## Core Principles
1.  **Readability > Optimization:** We are not building a High-Frequency Trading (HFT) system where microseconds matter. We are building a personal tool where **understanding the code 6 months from now** matters most.
2.  **Explicit > Implicit:** Avoid "magic" (complex decorators, metaclasses, dynamic imports). Code should be easy to trace by reading it top-to-bottom.
3.  **YAGNI (You Ain't Gonna Need It):** Do not build features or abstractions for hypothetical future use cases. Build only what is needed *today*.
4.  **Low Cognitive Load:** A weary developer should be able to understand a function without jumping through 5 different files.

## Coding Standards (Strict Rules)

### 1. Size Limits
* **Class Length:** **MAXIMUM 200 LINES.**
    * *Enforcement:* If a class hits 200 lines, it acts as a trigger to refactor. Split it into smaller, focused helpers or distinct services.
* **Function Length:** **Target < 50 LINES.**
    * *Enforcement:* Long functions usually mean mixed responsibilities. Extract logic into private `_helper_methods`.

### 2. Style & Syntax
* **Descriptive Naming:**
    * ✅ `calculate_moving_average(prices)`
    * ❌ `calc_ma(p)`
* **Type Hints:** Mandatory for all function arguments and return types. This serves as documentation.
    * `def get_price(symbol: str) -> float:`
* **Inline Code:** Always provide full, copy-pasteable blocks for the specific context. Avoid incomplete snippets like `... rest of code ...` unless explicitly requested.

### 3. Comments & Docs
* **Docstrings:** Every public class and method must have a brief docstring explaining *what* it does.
* **"Why" Comments:** Use inline comments to explain *why* a specific logic is used (e.g., specific trading rule or API quirk), not just what the code is doing.

## Anti-Patterns (Reject These)
* **Premature Optimization:** Writing complex caching logic before profiling proves it's necessary.
* **Over-Abstraction:** Creating a `BaseAbstractFactoryStrategyBuilder` when a simple `Strategy` class works.
* **"Clever" One-Liners:** Complex list comprehensions that are hard to read. Break them into loops if it improves clarity.
* **Deep Inheritance:** Avoid inheritance chains deeper than 2 levels. Prefer Composition over Inheritance.

## Behavior Instructions
* **If the user asks for code:** Generate simple, linear, and verbose implementations.
* **If the user provides complex code:** Propose a refactor to simplify it (e.g., "This function is doing too much; let's split it into X and Y").
* **If a file grows too large:** proactively suggest splitting it.
* **Library Choice:** Prefer standard libraries (Python `stdlib`) and standard data science stacks (`pandas`, `numpy`) over obscure dependencies.

## Example Refactor
**Bad (Too condensed, hard to read):**
```python
# Hard to debug, logic hidden in list comp
def get_signals(data):
    return [1 if x > y else -1 for x, y in zip(data['close'], data['ma']) if x != y]