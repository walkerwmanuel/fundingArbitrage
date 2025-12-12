# Just does api call to buy

import requests
from dotenv import load_dotenv
import os
import ccxt

load_dotenv()
WALLET_ADDRESS = os.getenv("wallet_pub")
HYPERLIQUID_PRIVATE_KEY = os.getenv("priv")
hyperliquid_api_url = "https://api.hyperliquid.xyz/info"

dex = ccxt.hyperliquid({
    "walletAddress": WALLET_ADDRESS,
    "privateKey": HYPERLIQUID_PRIVATE_KEY,
})

def get_spot_meta_and_asset_ctxs():
    body = {"type": "spotMetaAndAssetCtxs"}
    resp = requests.post(hyperliquid_api_url, json=body)
    resp.raise_for_status()
    return resp.json()

def get_user_spot_balances():
    body = {"type": "spotClearinghouseState", "user": WALLET_ADDRESS}
    resp = requests.post(hyperliquid_api_url, json=body)
    resp.raise_for_status()
    data = resp.json()
    balances = data.get("balances", [])
    return [b for b in balances if float(b.get("total", "0")) > 0]

def buy_spot(coin, usdc_amount):
    symbol = f"{coin}/USDC"
    price = float(dex.load_markets()[symbol]["info"]["midPx"])
    amount = usdc_amount / price  # Amount of coin to buy
    order = dex.create_order(symbol, "market", "buy", amount, price=price)
    return order

def sell_spot(coin, coin_amount):
    symbol = f"{coin}/USDC"
    price = float(dex.load_markets()[symbol]["info"]["midPx"])
    order = dex.create_order(symbol, "market", "sell", coin_amount, price=price)
    return order

