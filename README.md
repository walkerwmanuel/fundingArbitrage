# Funding Arbitrage ML (Hyperliquid)

An open-source, ML-driven funding-rate arbitrage system that predicts future funding rates and rebalances a delta-neutral portfolio (spot + perp) to capture funding edge.

This strategy can **add liquidity** to the market by taking the *unfavorable* side of crowded trades (e.g., receiving funding when others pay it) while **hedging price risk away** via spot/perp neutrality.

## What it does

- **Trains an ML model** (GradientBoostingRegressor) on hourly funding/premium data
- Predicts **10-day mean future funding**
- **Rotates/rebalances** into the top expected funding opportunities (net of fees)
- Runs on a schedule using **Docker + cron**

## Repo layout (typical)

- `logic/ml.py` — loads saved model + builds features + returns predictions per coin
- `logic/trade.py` — enter/exit positions (spot + perp)
- `services/spot.py`, `services/futures.py` — exchange wrappers (ccxt/hyperliquid)
- `app/main_hourly_funding.py` — pulls/stores hourly funding history
- `app/main_rebalance.py` — selects top coins and rebalances
- `models/` — saved pipeline + metadata (`gb_funding_pipeline.joblib`, `gb_funding_meta.json`)
- `historic_data/` — CSV data used for features/predictions

## Requirements

- Docker
- A `.env` file with required API keys / wallet info (see below)
- A local `historic_data/` folder mounted into the container

## Environment variables

Create a `.env` file in the repo root. Common ones (adjust to your code):

- `HYPERLIQUID_WALLET_PUBKEY=...`
- `HYPERLIQUID_PRIVATE_KEY=...`

## Running with Docker (cron mode)

Build the image:

```bash
docker build -t funding-arb-cron:latest .
