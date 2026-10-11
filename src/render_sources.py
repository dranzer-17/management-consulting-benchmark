"""Render sources.md from sources.csv so the two cannot drift apart. Run: python -m src.render_sources"""
import pandas as pd
from src.common import ROOT

s = pd.read_csv(ROOT / "sources.csv")
lines = ["# Sources", "", "*Generated from [sources.csv](sources.csv). Do not edit by hand.*", "",
         "Every chart and table in this study cites a source ID below. Retrieval date for all sources: 2026-10-11 unless noted.", ""]
for _, r in s.iterrows():
    lines += [f"## {r.source_id}: {r.dataset}", "",
              f"- **Publisher:** {r.publisher}", f"- **URL:** {r.url}", f"- **Date range:** {r.date_range}",
              f"- **Fields used:** {r.fields_used}", f"- **License / usage:** {r.license_or_usage}",
              f"- **Access method:** {r.access_method}", f"- **Raw file:** {r.raw_file}", f"- **Limitations:** {r.limitations}", ""]
(ROOT / "sources.md").write_text("\n".join(lines))
print("sources.md written:", len(s), "sources")
