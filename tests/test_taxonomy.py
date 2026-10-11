"""Taxonomy rules are explicit; these tests pin the behavior that analyses depend on."""
import pytest

from src.taxonomy import REGION, INDUSTRY_MAP, CAPABILITY_MAP, sic_to_industry, topic_of


@pytest.mark.parametrize("sic,expected", [
    ("2834", "Healthcare and pharma"), ("7372", "Technology and telecom"), ("6021", "Financial services and real estate"),
    ("1311", "Energy, utilities and resources"), ("5411", "Consumer, retail and leisure"), ("3714", "Industrials and transport"),
    ("6770", "Blank-check / SPAC"), ("8742", "Professional services"), ("9999", "Public sector"), (None, None), ("", None)])
def test_sic_to_industry(sic, expected):
    assert sic_to_industry(sic) == expected


@pytest.mark.parametrize("slug,expected", [
    ("global-private-equity-report-2024", "Private capital"), ("supply-chain-resilience", "Operations and supply chain"),
    ("climate-net-zero", "Sustainability and energy"), ("generative-ai-in-banking", "Technology and AI")])
def test_topic_of(slug, expected):
    assert topic_of(slug) == expected


def test_region_map_has_no_duplicates_across_regions():
    assert len(REGION) == len(set(REGION))


def test_taxonomy_maps_use_known_groups():
    assert "Healthcare and pharma" in INDUSTRY_MAP.values()
    assert "Technology, data and AI" in CAPABILITY_MAP.values()
