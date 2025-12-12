# main_rebalance.py
import os
from datetime import datetime, timezone

from logic.trade import exit_position, enter_position
from logic.ml import get_expected_return
from logic.helper import (
    unmap_from_hl_spot,
    get_filtered_spot_balances,
)

# Universe of coins to consider
ALL_COINS = ["BTC", "ETH", "SOL", "DOGE", "kPEPE"]


def rotate_coin(old_coin, new_coin, spot_amount, leverage):
    exit_position(old_coin)
    enter_position(new_coin, spot_amount, leverage)
    print(f"Switched out ({old_coin}) for ({new_coin})")

def rebalance_portfolio(all_coins, fees, spot_amount, leverage):
    
    print(f"Beginnint to rebalance portfolio at ({spot_amount}) dollars with ({leverage}) leverage\n")
    balances = get_filtered_spot_balances()
    owned_tokens = [
        unmap_from_hl_spot(b["coin"])
        for b in balances
        if b["coin"] != "USDC" and float(b["total"]) > 0
    ]
    print(f"We currently own ({owned_tokens})\n")

    expected_returns = {}
    for coin in all_coins:
        ten_days_return = (get_expected_return(coin) / 365) * 10
        net = ten_days_return if coin in owned_tokens else ten_days_return - fees
        expected_returns[coin] = net

    top3 = sorted(expected_returns, key=expected_returns.get, reverse=True)[:3]
    print(f"We want to own ({top3})\n")
    current = owned_tokens[:]  # working copy so we can update as we rotate

    for target in top3:
        if target not in current:
            old_coin = next((c for c in current if c not in top3), None)
            if old_coin:
                rotate_coin(old_coin, target, spot_amount, leverage)
                # update working holdings to prevent reusing the same coin
                current.remove(old_coin)
                current.append(target)
            else:
                print(f"No coin to rotate out for {target}, opening new position.")
                enter_position(target, spot_amount, leverage)
                current.append(target)
        else:
            # already own it; nothing to do
            continue
    print(f"Just finished rebalancing, the new coins are ({current})")


if __name__ == "__main__":
    # Read config from env so cron can control behavior
    fees = .0023
    spot_amount = 100
    leverage = 2

    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    print(
        f"[{now}] Running portfolio rebalance on coins: {ALL_COINS} "
        f"(spot_amount={spot_amount}, leverage={leverage}, fees={fees})"
    )

    rebalance_portfolio(ALL_COINS, fees, spot_amount, leverage)
