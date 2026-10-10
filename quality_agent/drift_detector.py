"""Schema-drift and anomaly detector for the silver layer.

Rule-based core (runs anywhere). `explain_with_llm()` is an optional hook where you
can send the findings to Snowflake Cortex (SNOWFLAKE.CORTEX.COMPLETE) or any LLM to get
a plain-English summary and fix recommendations. Keep the detection deterministic;
use the LLM only to explain and recommend.
"""
import argparse
import json
from pathlib import Path
import pandas as pd


def load_df(path: str) -> pd.DataFrame:
    p = Path(path)
    if p.is_dir():
        return pd.concat((pd.read_parquet(f) for f in p.rglob("*.parquet")), ignore_index=True)
    return pd.read_csv(p) if p.suffix == ".csv" else pd.read_parquet(p)


def profile(df: pd.DataFrame) -> dict:
    out = {"row_count": int(len(df)), "columns": {}}
    for c in df.columns:
        s = df[c]
        info = {"dtype": str(s.dtype), "null_rate": round(float(s.isna().mean()), 4)}
        if pd.api.types.is_numeric_dtype(s):
            info.update(mean=float(s.mean()), std=float(s.std()))
        out["columns"][c] = info
    return out


def detect(baseline: dict, current: dict, null_tol=0.02, z_tol=3.0) -> list[dict]:
    findings = []
    b, c = baseline["columns"], current["columns"]
    for col in b.keys() - c.keys():
        findings.append({"type": "column_removed", "column": col, "severity": "high"})
    for col in c.keys() - b.keys():
        findings.append({"type": "column_added", "column": col, "severity": "medium"})
    for col in b.keys() & c.keys():
        if b[col]["dtype"] != c[col]["dtype"]:
            findings.append({"type": "dtype_changed", "column": col,
                             "from": b[col]["dtype"], "to": c[col]["dtype"], "severity": "high"})
        if c[col]["null_rate"] - b[col]["null_rate"] > null_tol:
            findings.append({"type": "null_rate_spike", "column": col,
                             "from": b[col]["null_rate"], "to": c[col]["null_rate"], "severity": "medium"})
        if "mean" in b[col] and "mean" in c[col] and b[col]["std"]:
            z = abs(c[col]["mean"] - b[col]["mean"]) / b[col]["std"]
            if z > z_tol:
                findings.append({"type": "mean_shift", "column": col, "z": round(z, 2), "severity": "medium"})
    return findings


def explain_with_llm(findings: list[dict]) -> str:  # optional hook
    return "LLM explanation not configured. Findings: " + json.dumps(findings, indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--write-baseline", action="store_true", help="save current profile as baseline")
    a = ap.parse_args()
    cur = profile(load_df(a.data))
    bp = Path(a.baseline)
    if a.write_baseline or not bp.exists():
        bp.write_text(json.dumps(cur, indent=2))
        print(f"baseline written to {bp}")
    else:
        found = detect(json.loads(bp.read_text()), cur)
        print(explain_with_llm(found) if found else "no drift detected")
