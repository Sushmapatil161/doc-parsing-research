"""Cut the real public-domain PDFs down to a few pages (Day 3, Task 3).

Page numbers are 1-based, as shown in a PDF viewer. Sources: data/real/SOURCES.csv
Usage: python scripts/cut_real_pages.py
"""
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "real" / "raw"
OUT = ROOT / "data"

CUTS = {
    "21_irs_w9_p1.pdf":      ("fw9.pdf", [1]),
    "22_irs_1040_p1.pdf":    ("f1040.pdf", [1]),
    "23_cdc_mmwr_p1-3.pdf":  ("cdc_mmwr_v74n14.pdf", [1, 2, 3]),
    "24_cdc_table_p1.pdf":   ("cdc_mmwr_v74n14_table.pdf", [1]),
    "25_nasa_scan.pdf":      ("nasa_19740074640.pdf", [24,38,259]),   # fill in 2-3 page numbers
}

for new_name, (source, pages) in CUTS.items():
    if not pages:
        print(f"skipped {new_name}: no pages chosen yet")
        continue
    doc = pymupdf.open(RAW / source)
    doc.select([p - 1 for p in pages])
    doc.save(OUT / new_name, garbage=3, deflate=True)
    print(f"made {new_name} from {source}, pages {pages}")