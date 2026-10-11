"""Firm-name matching must be strict: near-miss companies are not the firms."""
import pytest

from src.common import firm_of


@pytest.mark.parametrize("name,expected", [
    ("MCKINSEY  COMPANY, INC UNITED STATES", "McKinsey"),
    ("McKinsey & Company, Inc. United States", "McKinsey"),
    ("MCKINSEY &AMP; COMPANY, INC.", "McKinsey"),
    ("THE BOSTON CONSULTING GROUP, INC.", "BCG"),
    ("The Boston Consulting Group UK LLP", "BCG"),
    ("BAIN & COMPANY, INC.", "Bain"),
    ("BAIN  COMPANY, INC", "Bain"),
    ("Bain and Company, Inc.", "Bain"),
    ("BAIN &AMP; COMPANY, INC.", "Bain"),
    ("MCKINSEY FENCING", None),
    ("MIO Partners, Inc. (McKinsey & Company)", None),
    ("Boston Consulting Solutions Inc", None),
    ("BAIN & SCHINDELE TAX CONSULTING LLC", None),
    ("Bain & Collins LLC", None),
    ("Bain Capital", None),
    (None, None),
])
def test_firm_of(name, expected):
    assert firm_of(name) == expected
