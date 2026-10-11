"""Shared settings for the ingestion scripts.

Public APIs (SEC EDGAR in particular) ask clients to identify themselves. By default requests identify the project by
its repository URL. To use a personal contact address instead, set the CONTACT environment variable before running.
"""
import os

REPO = "https://github.com/dranzer-17/management-consulting-benchmark"
CONTACT = os.environ.get("CONTACT", REPO)
USER_AGENT = f"management-consulting-benchmark analysis project ({CONTACT})"
HEADERS = {"User-Agent": USER_AGENT}

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANUAL = ROOT / "data" / "manual"
CLEAN = ROOT / "data" / "clean"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
FIRMS = ["McKinsey", "BCG", "Bain"]
COLORS = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}


import re

# One strict name matcher for every source. Strict on purpose: "BAIN & SCHINDELE TAX CONSULTING" and "MCKINSEY FENCING"
# are different companies. Tolerates spacing, "and" for "&", HTML-escaped "&amp;" and DOL records that dropped the ampersand.
FIRM_PATTERNS = {
    "McKinsey": r"^mckinsey\s*(?:&(?:amp;)?|and)?\s*company\b",
    "BCG": r"\bboston consulting group\b",
    "Bain": r"^bain\s+(?:&(?:amp;)?\s*|and\s+|et\s+)?(?:company|co\b)",
}


def firm_of(name):
    """Return 'McKinsey' / 'BCG' / 'Bain' for a legal-entity name, else None."""
    for firm, pat in FIRM_PATTERNS.items():
        if re.search(pat, str(name or ""), re.I):
            return firm
    return None
