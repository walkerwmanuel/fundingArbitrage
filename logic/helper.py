
from services.spot import get_user_spot_balances

def map_to_hl_spot(ticker: str) -> str:
    ticker = ticker.upper()
    mapping = {
        "BTC": "BTC",
        "ETH": "ETH",
        "SOL": "SOL",
        "XRP": "WXRP",
        "DOGE": "DOGE",
        "kPEPE": "PEPE",
        "USDT": "USDT0",
        "ENA": "UENA",
        "WLD": "UWLD",
        "FARTCOIN": "UFART",
        "BONK": "UBONK",
    }
    return mapping.get(ticker, f"U{ticker}")


def unmap_from_hl_spot(hl_ticker: str) -> str:
    hl_ticker = hl_ticker.upper()
    reverse_mapping = {
        "UBTC": "BTC",
        "UETH": "ETH",
        "USOL": "SOL",
        "kPEPE": "PEPE",
        "WXRP": "XRP",
        "UDOGE": "DOGE",
        "USDT0": "USDT",
        "UENA": "ENA",
        "UWLD": "WLD",
        "UFART": "FARTCOIN",
        "UBONK": "BONK",
    } 
    return reverse_mapping.get(hl_ticker, hl_ticker)

def map_to_hl_futures(ticker: str) -> str:
    ticker = ticker.upper()
    mapping = {
        "BTC": "BTC",
        "ETH": "ETH",
        "SOL": "SOL",
        "XRP": "XRP",
        "DOGE": "DOGE",
        "kPEPE": "kPEPE",
        "USDT": "USDT",
        "ENA": "ENA",
        "WLD": "WLD",
        "FARTCOIN": "FARTCOIN",
        "BONK": "kBONK",  # ✅ BONK futures ticker
    }
    coin = mapping.get(ticker, ticker)
    return f"{coin}/USDC:USDC"

def get_filtered_spot_balances():
    balances = get_user_spot_balances()
    return [b for b in balances if float(b.get("entryNtl", "0")) >= 1]