# QuantStackSkill

## Metadata
* **Skill Name:** QuantStackSkill
* **Version:** 1.0
* **Scope:** Domain & Application Layers (Analysis & Backtesting)
* **Target Stack:** `pandas-ta`, `vectorbt`, `pandas`, `numpy`

## Purpose
To strictly forbid the manual implementation of standard financial algorithms. If a metric (RSI, Drawdown, Sharpe Ratio) or a mechanism (Backtesting engine, Order matching) exists in a standard library, **WE USE THE LIBRARY.** Writing custom "for-loops" for financial math is an immediate failure mode.

## Approved Toolset

| Category | Primary Library | Fallback |
| :--- | :--- | :--- |
| **Technical Indicators** | **`pandas-ta`** | `ta` (Technical Analysis Lib) |
| **Vectorized Backtesting** | **`vectorbt`** | `backtesting.py` |
| **Data Manipulation** | **`pandas`** | `polars` (only if perf critical) |
| **Math/Stats** | **`numpy`** | - |

## Core Principles

### 1. The "Import, Don't Write" Rule
* **Rule:** Never write a function to calculate SMA, RSI, MACD, Bollinger Bands, or Max Drawdown manually.
* **Why:** Library implementations are tested against millions of data points and handle edge cases (NaNs, zero division) better than custom code.

### 2. Vectorization over Iteration
* **Rule:** Avoid iterating through rows (`for index, row in df.iterrows():`) to calculate signals.
* **Standard:** Use column-wise operations provided by `pandas` and `vectorbt`.
* **Exception:** Iteration is allowed *only* in the `infrastructure` layer if the Broker API requires it (e.g., placing orders one by one).

### 3. Metric Standardization
* Use `vectorbt` (or `empyrical`) to calculate performance metrics (Sharpe, Sortino, Max Drawdown). Do not write your own formulas for these.

## Coding Standards

### Indicators (`pandas-ta`)
Use the "DataFrame Extension" syntax for readability.

**Bad (Manual Calculation):**
```python
# ❌ REJECT: Prone to off-by-one errors
def calculate_sma(prices, window):
    return [sum(prices[i:i+window])/window for i in range(len(prices)-window)]