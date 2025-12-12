# services/futures.py

from dotenv import load_dotenv
import os
import ccxt
import requests
from logic.helper import map_to_hl_futures

load_dotenv()
WALLET_ADDRESS = os.getenv("wallet_pub")
HYPERLIQUID_PRIVATE_KEY = os.getenv("priv")
hyperliquid_api_url = "https://api.hyperliquid.xyz/info"

dex = ccxt.hyperliquid({
    "walletAddress": WALLET_ADDRESS,
    "privateKey": HYPERLIQUID_PRIVATE_KEY,
})

def open_futures_position(coin, usd_amount, side, leverage=1):
    symbol = map_to_hl_futures(coin)
    dex.set_leverage(leverage, symbol, params={"marginMode": "isolated"})
    price = float(dex.load_markets()[symbol]["info"]["midPx"])
    coin_amount = (usd_amount * leverage) / price
    order_type = "market"
    order_side = "buy" if side == "long" else "sell"
    order = dex.create_order(symbol, order_type, order_side, coin_amount, price=price)
    return order

def close_futures_position(coin, side=None):
    symbol = map_to_hl_futures(coin)

    try:
        positions = dex.fetch_positions([symbol]) or []
    except Exception:
        positions = []
    pos = next((p for p in positions if p.get("symbol") == symbol), None)
    if not pos:
        return {"status": "no_position", "symbol": symbol}

    size = float(pos.get("contracts") or 0)
    if size == 0:
        return {"status": "no_position", "symbol": symbol}

    detected_side = (pos.get("side") or ("long" if size > 0 else "short")).lower()
    # Close long -> sell, close short -> buy
    order_side = "sell" if detected_side == "long" else "buy"

    price = float(dex.load_markets()[symbol]["info"]["midPx"])
    qty = abs(size)

    return dex.create_order(
        symbol, "market", order_side, qty, price=price, params={"reduceOnly": True}
    )

def get_live_asset_context(coin: str):
    headers = {"Content-Type": "application/json"}
    payload = {"type": "metaAndAssetCtxs"}
    resp = requests.post(hyperliquid_api_url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # data is [meta, asset_contexts], where asset_contexts is a list
    # The order matches between meta["universe"] and asset_contexts
    meta = data[0]
    asset_contexts = data[1]
    # Find the index for the given coin
    for i, coin_meta in enumerate(meta["universe"]):
        if coin_meta["name"].upper() == coin.upper():
            return asset_contexts[i]
    return None  # Not found