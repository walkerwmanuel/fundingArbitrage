from pathlib import Path
from functools import lru_cache
import json
import joblib
import pandas as pd

# must match training
N_2D, N_6D, N_18D = 24*2, 24*6, 24*18
NEEDED = [
    "funding_avg_2d","funding_avg_6d","funding_avg_18d",
    "premium_avg_2d","premium_avg_6d","premium_avg_18d",
]

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("time").copy()

    df["funding_avg_2d"]  = df["funding"].rolling(N_2D,  min_periods=N_2D).mean()
    df["funding_avg_6d"]  = df["funding"].rolling(N_6D,  min_periods=N_6D).mean()
    df["funding_avg_18d"] = df["funding"].rolling(N_18D, min_periods=N_18D).mean()

    df["premium_avg_2d"]  = df["premium"].rolling(N_2D,  min_periods=N_2D).mean()
    df["premium_avg_6d"]  = df["premium"].rolling(N_6D,  min_periods=N_6D).mean()
    df["premium_avg_18d"] = df["premium"].rolling(N_18D, min_periods=N_18D).mean()

    return df

@lru_cache(maxsize=1)
def _load_model():
    # if this file is root/logic/ml.py, repo root is parents[1]
    root = Path(__file__).resolve().parents[1]
    models_dir = root / "models"   # <-- models folder in repo root

    pipe = joblib.load(models_dir / "gb_funding_pipeline.joblib")
    meta = json.loads((models_dir / "gb_funding_meta.json").read_text())
    featureCols = meta["featureCols"]
    return pipe, featureCols

def get_expected_return(coin: str) -> float:
    pipe, featureCols = _load_model()

    # read coin history
    data_path = Path(__file__).resolve().parents[1] / "historic_data" / f"{coin}_funding_data.csv"
    df = pd.read_csv(data_path, parse_dates=["time"]).sort_values("time")

    df = add_features(df)

    last = df.dropna(subset=NEEDED).tail(1)
    if last.empty:
        raise ValueError(f"{coin}: not enough history (need >= {N_18D} rows)")

    # build exact model row (incl coin dummies)
    row = {c: 0.0 for c in featureCols}
    for c in NEEDED:
        row[c] = float(last.iloc[0][c])

    coin_col = f"coin_{coin}"
    if coin_col not in row:
        raise ValueError(f"Unknown coin '{coin}' for this model (missing {coin_col})")
    row[coin_col] = 1.0

    X = pd.DataFrame([row], columns=featureCols)
    pred = float(pipe.predict(X)[0])
    return pred * 24 * 265
