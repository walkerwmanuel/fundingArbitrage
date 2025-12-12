# main_hourly_funding.py
import os
from datetime import datetime, timezone
from logic.data import append_live_funding_row  # adjust path if needed

COINS = ["BTC", "ETH", "SOL", "DOGE", "kPEPE"]

if __name__ == "__main__":
    os.makedirs("historic_data", exist_ok=True)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    print(f"[{now}] Running hourly funding append for coins: {COINS}")

    for coin in COINS:
        print(f"Appending live funding row for {coin}...")
        append_live_funding_row(coin)
