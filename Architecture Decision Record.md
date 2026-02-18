# Architecture Decision Record: Personal Trading Tool

**Status:** Decided

## 1. Context

The goal is to build a personal trading tool for the Indian stock market with a primary constraint of keeping operational costs at or near zero. The system must be cloud-native and support a web-based user interface, a persistent database, automated execution of tasks (cron jobs), and real-time notifications.

## 2. Decision

We will adopt a modular, cloud-native architecture using Python for backend services and a static web frontend. The core components will be the **Groww Trading API** for brokerage, **PostgreSQL on Supabase** for the database, **FastAPI** for the backend, a **JavaScript frontend hosted on GitHub Pages** for the UI, **Render** for backend deployment and cron, **Telegram** for notifications, and a **library-first backtesting stack** instead of building a custom backtesting engine.

This stack was chosen because it leverages services with generous free tiers, aligning with the primary goal of zero cost, while providing a modern, scalable, and maintainable structure.

## 3. Component Breakdown and Justification

| Component              | Chosen Technology                               | Justification                                                                                                                                                                                                                                                                                       |
| ---------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Broker API**         | **Groww Trading API**                           | **Primary Reason: Cost.** It is completely free, saving a significant monthly fee compared to alternatives. It provides an official Python SDK and a high-rate-limit historical data API, which is ideal for backtesting stock strategies.                                                              |
| **Cloud Database**     | **PostgreSQL via Supabase**                     | **Primary Reason: Cloud-Native & Free.** Supabase offers a generous free tier for a professional-grade PostgreSQL database. It's cloud-hosted from day one and includes an auto-generated REST API, simplifying backend development.                                                                   |
| **Backend Logic**      | **Python with FastAPI**                         | **Primary Reason: Performance & Simplicity.** Python is the de facto standard for data science and algorithmic trading. FastAPI is a modern, high-performance web framework for building the robust API needed to handle trading logic and serve data to the UI.                                    |
| **Frontend UI**        | **Static SPA (HTML/CSS/JS, e.g., React) on GitHub Pages** | **Primary Reason: Real-time UX & Cost.** A browser-native frontend handles low-latency UI updates better than Streamlit for frequent tick-level refresh. GitHub Pages provides free static hosting and simple CI-based deployment. |
| **Deployment & Cron**  | **Render (Backend + Workers + Cron)**           | **Primary Reason: Operational Fit.** Render will host FastAPI services and scheduled jobs (data fetch, signals, housekeeping). This keeps execution logic and schedulers in one managed platform. |
| **Live Data Handling** | **WebSocket/SSE for UI + REST for queries**     | **Primary Reason: Responsive and scalable updates.** Backend ingests market ticks via WebSocket from Groww, persists to database, and pushes incremental updates to the frontend over WebSocket (or SSE). REST remains for historical data, snapshots, and configuration endpoints. |
| **Notifications**      | **Telegram Bot**                                | **Primary Reason: Simplicity & Immediacy.** A Telegram bot is extremely easy to set up and provides free, instant push notifications to a mobile device for critical events like order executions, system errors, or daily summaries.                                                              |

## 4. Consequences

*   **Positive:**
    *   The entire stack can be run with **zero monthly cost**.
    *   The architecture is **modular and scalable**.
    *   The architecture cleanly separates backend services from a real-time web UI.
*   **Accepted Trade-offs:**
    *   By choosing Groww over Kite Connect, we lose access to advanced order types like GTT (Good Till Triggered) and a larger developer community. This is an acceptable trade-off to meet the zero-cost requirement.
    *   Moving from Streamlit to a JavaScript frontend increases frontend implementation complexity.

## 5. Backtesting Engine Strategy

### 5.1 Decision

We will **not** build a backtesting engine from scratch in v1. We will use mature Python libraries for data handling, indicators, execution simulation, and portfolio accounting.

### 5.2 Tool Selection

| Scope | Chosen Tool | Why |
| --- | --- | --- |
| Primary research and large parameter sweeps | **vectorbt** (or vectorbtpro if needed later) | Fast, vectorized computation with NumPy/Pandas; ideal for long historical runs and systematic strategy exploration. |
| Strategy prototyping and readability | **backtesting.py** | Lightweight and intuitive API; good for clear strategy iteration and validation. |
| Event-driven or complex broker-like behavior (optional fallback) | **Backtrader** | Feature-rich framework for cases that are hard to express in vectorized form. |

### 5.3 Rationale

For a 20-year backtest horizon, **accuracy and scalability** matter more than writing custom plumbing code. A library-first approach reduces implementation risk, shortens delivery time, and lets us focus on strategy logic and risk controls.

### 5.4 Consequences

*   **Positive:**
    *   Faster time-to-market and less maintenance burden.
    *   Better-tested core mechanics for OHLC handling, indicators, and portfolio state.
    *   Easier benchmarking across multiple strategy styles.
*   **Accepted Trade-offs:**
    *   We depend on third-party library behavior and upgrade cycles.
    *   Some highly custom execution semantics may require framework-specific workarounds.
