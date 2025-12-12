# logic/trade.py

import json

from services.spot import buy_spot, sell_spot
from services.futures import open_futures_position, close_futures_position
from logic.helper import map_to_hl_spot, get_filtered_spot_balances

def enter_position(coin, spot_amount, leverage): # Spot amount is amount of spot bought to hedge
    if spot_amount <= 10:
        print(f"Error: Spot amount too small ({spot_amount}). Minimum required is 10.")
        return  # Stop the function here
    lev_amount = spot_amount / leverage

    spot_symbol = map_to_hl_spot(coin)
    spot_order = buy_spot(spot_symbol, spot_amount)
    print(f"Spot order ({spot_symbol}):", spot_order)

    fut_order = open_futures_position(coin, usd_amount=lev_amount, side="short", leverage=leverage)
    print(f"Futures order ({coin} short):", fut_order)

def exit_position(coin):
    spot_symbol = map_to_hl_spot(coin)

    balances = get_filtered_spot_balances()  # returns only >0 totals
    print(json.dumps(balances, indent=2))
    spot_amt = 0.0
    for b in balances:
        if b.get("coin") == spot_symbol:
            # 'total' is in UNITS of the spot coin (e.g., UETH amount), not USD
            spot_amt = float(b.get("total", "0"))
            break
    # print both values for clarity
    print(f"\nAttempting to sell {spot_amt} {spot_symbol}")

    spot_result = None
    if spot_amt > 0:
        spot_result = sell_spot(spot_symbol, spot_amt)
        print(f"Sold spot ({spot_symbol}) amount {spot_amt}:", spot_result)
    else:
        print(f"No spot balance to sell for {spot_symbol}")

    # 3) Close futures short (reduceOnly)
    fut_result = close_futures_position(coin, side="short")
    print(f"Closed futures ({coin} short):", fut_result)

    return {"spot": spot_result, "futures": fut_result}
