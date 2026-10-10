"""Generate synthetic insurance-claims data (no real or client data).

Usage: python src/generate_claims.py --rows 1000000 --out data/raw/claims.csv
Deliberately injects dirty records (nulls, negative amounts, duplicates,
bad dates) so the silver layer has real cleaning and validation work to do.
"""
import argparse
import os
import numpy as np
import pandas as pd

LINES = ["WORKERS_COMP", "COMMERCIAL_AUTO", "COMMERCIAL_UMBRELLA", "GENERAL_LIABILITY"]
STATES = ["TX", "CA", "NY", "FL", "IA", "IL", "OH", "WA", "GA", "PA"]
STATUS = ["OPEN", "CLOSED", "REOPENED", "DENIED"]


def generate(rows: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    loss = pd.to_datetime("2022-01-01") + pd.to_timedelta(rng.integers(0, 1400, rows), unit="D")
    report = loss + pd.to_timedelta(rng.integers(0, 60, rows), unit="D")
    df = pd.DataFrame({
        "claim_id": np.arange(1, rows + 1),
        "policy_id": rng.integers(100000, 150000, rows),
        "line_of_business": rng.choice(LINES, rows, p=[0.4, 0.3, 0.1, 0.2]),
        "state": rng.choice(STATES, rows),
        "loss_date": loss.strftime("%Y-%m-%d"),
        "report_date": report.strftime("%Y-%m-%d"),
        "status": rng.choice(STATUS, rows, p=[0.35, 0.5, 0.05, 0.1]),
        "incurred_amount": np.round(rng.lognormal(8.5, 1.2, rows), 2),
        "paid_amount": np.round(rng.lognormal(8.0, 1.2, rows), 2),
    })
    # --- inject dirt (about 3% of rows) ---
    n = max(1, rows // 100)
    df.loc[rng.choice(rows, n, replace=False), "state"] = None
    df.loc[rng.choice(rows, n, replace=False), "incurred_amount"] = -1 * df["incurred_amount"]
    df.loc[rng.choice(rows, n, replace=False), "report_date"] = "not-a-date"
    dupes = df.sample(n, random_state=seed)
    return pd.concat([df, dupes], ignore_index=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=100_000)
    ap.add_argument("--out", default="data/raw/claims.csv")
    a = ap.parse_args()
    out = generate(a.rows)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    out.to_csv(a.out, index=False)
    print(f"wrote {len(out):,} rows to {a.out}")
