"""Write data/real/SOURCES.csv: where each real PDF came from, its licence, and its SHA-256."""
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "real" / "raw"
US_GOV = "Work of the US federal government, public domain (17 U.S.C. 105)"

SOURCES = [
    ("fw9.pdf", "https://www.irs.gov/pub/irs-pdf/fw9.pdf", US_GOV,
     "IRS form published on irs.gov", "21_irs_w9_p1.pdf: page 1", "PowerShell Invoke-WebRequest"),
    ("f1040.pdf", "https://www.irs.gov/pub/irs-pdf/f1040.pdf", US_GOV,
     "IRS form published on irs.gov", "22_irs_1040_p1.pdf: page 1", "PowerShell Invoke-WebRequest"),
    ("cdc_mmwr_v74n14.pdf", "https://stacks.cdc.gov/view/cdc/177614/cdc_177614_DS1.pdf", "Public domain",
     "CDC Stacks record https://stacks.cdc.gov/view/cdc/177614 is labelled Public Domain",
     "23_cdc_mmwr_p1-3.pdf: pages 1-3", "Browser (CDC blocks scripted downloads: Access Denied)"),
    ("cdc_mmwr_v74n14_table.pdf", "https://stacks.cdc.gov/view/cdc/177614/cdc_177614_DS4.pdf", "Public domain",
     "Supporting file of the same CDC Stacks record (labelled Public Domain)",
     "24_cdc_table_p1.pdf: page 1", "Browser (CDC blocks scripted downloads: Access Denied)"),
    ("nasa_19740074640.pdf", "https://ntrs.nasa.gov/api/citations/19740074640/downloads/19740074640.pdf",
     US_GOV, "NTRS record https://ntrs.nasa.gov/citations/19740074640: 'Work of the US Gov. Public Use Permitted.'",
     "25_nasa_scan.pdf: pages 24, 38, 259", "PowerShell Invoke-WebRequest"),
]

rows = []
for name, url, licence, evidence, used, how in SOURCES:
    sha = hashlib.sha256((RAW / name).read_bytes()).hexdigest()
    rows.append({"raw_file": name, "url": url, "downloaded_on": "2026-10-15", "how": how,
                 "licence": licence, "licence_evidence": evidence, "used_as": used, "sha256": sha})
    print(f"{name:28} {sha[:16]}...")

with open(ROOT / "data" / "real" / "SOURCES.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print("Wrote data/real/SOURCES.csv")