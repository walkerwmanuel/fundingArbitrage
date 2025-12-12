import csv
import os
from datetime import datetime, timezone, timedelta
import subprocess
import pandas as pd

from services.futures import get_live_asset_context

def append_live_funding_row(coin: str):
    print("Running append_live_funding_row function")
    live_ctx = get_live_asset_context(coin)
    if not live_ctx:
        print(f"Could not fetch asset context for {coin}")
        return

    # Prepare the row, matching the historical data format
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    row = {
        "time": now,
        "coin": coin,
        "funding": live_ctx.get("funding", ""),
        "open_interest": live_ctx.get("openInterest", ""),
        "prev_day_px": live_ctx.get("prevDayPx", ""),
        "day_ntl_vlm": live_ctx.get("dayNtlVlm", ""),
        "premium": live_ctx.get("premium", ""),
        "oracle_px": live_ctx.get("oraclePx", ""),
        "mark_px": live_ctx.get("markPx", ""),
        "mid_px": live_ctx.get("midPx", ""),
        "impact_bid_px": "",
        "impact_ask_px": "",
    }
    # Parse impactPxs as bid/ask if present
    impact_pxs = live_ctx.get("impactPxs", [])
    if isinstance(impact_pxs, list):
        if len(impact_pxs) > 0:
            row["impact_bid_px"] = impact_pxs[0]
        if len(impact_pxs) > 1:
            row["impact_ask_px"] = impact_pxs[1]

    csv_file = os.path.join("historic_data", f"{coin}_funding_data.csv")
    headers = [
        "time", "coin", "funding", "open_interest", "prev_day_px", "day_ntl_vlm",
        "premium", "oracle_px", "mark_px", "mid_px", "impact_bid_px", "impact_ask_px"
    ]

    file_exists = os.path.isfile(csv_file)
    try:
        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists or os.stat(csv_file).st_size == 0:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"Error writing to CSV: {e}")