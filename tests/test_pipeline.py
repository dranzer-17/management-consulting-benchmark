"""End-to-end checks on the committed outputs: validation passes and every registered claim matches its metric."""
import json

import pandas as pd
import pytest

from src import validate
from src.common import ROOT, TABLES


def test_validation_has_no_failures():
    validate.FAILURES.clear(); validate.PASSED.clear()
    assert validate.run() == []


def _claims():
    return pd.read_csv(ROOT / "claims.csv")


@pytest.mark.parametrize("claim_id", _claims().claim_id.tolist())
def test_claim_matches_metrics(claim_id):
    """claims.csv carries the expected value for each number in a claim; a drift in the data fails here."""
    m = pd.read_csv(TABLES / "metrics.csv")
    row = _claims().set_index("claim_id").loc[claim_id]
    for chk in json.loads(row.checks):
        q = m[(m.metric_id == chk["metric"]) & (m.firm == chk["firm"])]
        assert len(q) >= 1, f"{claim_id}: no metric {chk}"
        actual = float(q.value.iloc[0])
        assert abs(actual - chk["value"]) <= chk["tol"], f"{claim_id} {chk['metric']} {chk['firm']}: claim {chk['value']} vs data {actual}"


def test_every_claim_has_a_limitation_and_source():
    c = _claims()
    assert c.limitation.notna().all() and (c.limitation.str.len() > 20).all()
    assert c.source_ids.notna().all()
    assert set(c.status) <= {"verified", "needs review", "rejected"}


def test_metrics_document_their_definitions():
    m = pd.read_csv(TABLES / "metrics.csv", keep_default_na=False)   # "n/a" is a deliberate entry, not a missing value
    for col in ["definition", "numerator", "denominator", "filters", "missing_data", "source_ids", "basis"]:
        assert (m[col].astype(str).str.strip() != "").all(), f"metrics.csv column {col} has blanks"


def test_cagr_formula():
    from src.metrics import cagr
    assert cagr(100, 200, 1) == pytest.approx(1.0)
    assert cagr(100, 121, 2) == pytest.approx(0.10)
