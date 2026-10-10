import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.generate_claims import generate
from quality_agent.drift_detector import profile, detect


def test_generator_injects_dirty_rows():
    df = generate(2000)
    assert df["state"].isna().any()
    assert (df["incurred_amount"] < 0).any()
    assert df["claim_id"].duplicated().any()


def test_drift_detector_flags_removed_column_and_dtype_change():
    base = profile(generate(2000))
    cur = profile(generate(2000).drop(columns=["state"]).assign(policy_id=lambda d: d.policy_id.astype(str)))
    types = {f["type"] for f in detect(base, cur)}
    assert "column_removed" in types
    assert "dtype_changed" in types


def test_no_drift_on_identical_profile():
    p = profile(generate(2000))
    assert detect(p, p) == []
