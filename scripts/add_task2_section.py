"""One-off Day 3 edit: add the hard-scan / OCR sweep results before the reproducibility notes."""
from pathlib import Path

p = Path("docs/report.md")
text = p.read_text(encoding="utf-8")
HEADING = "## Harder scans: where OCR breaks"
ANCHOR = "## Reproducibility notes"
if HEADING in text:
    raise SystemExit("STOPPED: section already exists, nothing changed")
if text.count(ANCHOR) != 1:
    raise SystemExit("STOPPED: could not find the reproducibility notes heading")

SECTION = f"""{HEADING}

Source page: `07_scanned.pdf` (6 facts). One change at a time, each OCR setup run once per file. Script: `scripts/ocr_sweep.py`; data: `results/sweep.csv`; files: `data/sweep/`. All pages are simulated from the clean scan; both the 20 degree and 36 dpi pages are still readable by eye [read]. MarkItDown is not included: it found 0/6 on every scan (no OCR for PDFs).

| Page | Docling + RapidOCR | Docling + RapidOCR, full-page OCR | Docling + EasyOCR | PyMuPDF4LLM (RapidOCR) |
|---|---|---|---|---|
| tilt 0 deg | 5 | 5 | 4 | 5 |
| tilt 4 deg | 6 | 6 | 5 | 6 |
| tilt 8 deg | 6 | 6 | 3 | 6 |
| tilt 12 deg | **0** | **0** | **0** | 6 |
| tilt 20 deg | **0** | **0** | **0** | 6 |
| 150 dpi | 6 | 5 | 6 | 5 |
| 100 dpi | 6 | 6 | 5 | 6 |
| 72 dpi | 6 | 5 | 6 | 6 |
| 50 dpi | 6 | 5 | 2 | 6 |
| 36 dpi | **0** | **0** | **0** | 6 |
| Median s/page | 3.83 | 5.82 | 4.07 | 2.49 |

* **[measured]** Docling does not degrade gradually: it goes from 6/6 at 8 degrees to 0/6 at 12 degrees, and from 6/6 at 50 dpi to 0/6 at 36 dpi. The failed outputs contain only `<!-- image -->` (14 characters), with no error or warning.
* **[measured]** `force_full_page_ocr=True` does not fix these cases, and costs about 2 s more per page.
* **[inferred]** Docling's layout model classifies the whole tilted or tiny page as a picture, so its text never reaches the Markdown output. Not proven.
* **[measured]** PyMuPDF4LLM uses the same OCR engine (RapidOCR) and found 5-6/6 on every page, including 20 degrees and 36 dpi. So how a tool passes the page to the OCR engine matters as much as which engine it uses.
* **[measured]** Docling + EasyOCR is the weakest and least consistent setup (2-6/6 on pages that Docling + RapidOCR read fully).
* The 5/6 results are the lost space in "Annual Summary 2026" (read as "AnnualSummary"). One fact on one page decides 5 vs 6, so differences of one fact are noise.
* Limitation: one page, one run per setup, simulated damage. A real phone photo is still to be added.

"""

text = text.replace(ANCHOR, SECTION + ANCHOR)
p.write_text(text, encoding="utf-8")
print("Added the hard-scan section to docs/report.md")