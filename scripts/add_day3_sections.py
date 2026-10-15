"""One-off Day 3 edit: add real-document results, failure catalogue and recommendations to the report."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "docs" / "report.md"
text = p.read_text(encoding="utf-8")
ANCHOR = "## Reproducibility notes"
if "## Real public-domain documents" in text:
    raise SystemExit("STOPPED: sections already exist, nothing changed")
if text.count(ANCHOR) != 1:
    raise SystemExit("STOPPED: could not find the reproducibility notes heading")

catalogue = (ROOT / "results" / "failure_catalogue.md").read_text(encoding="utf-8")
by_type = (ROOT / "results" / "by_doc_type.md").read_text(encoding="utf-8")

SECTIONS = f"""## Real public-domain documents

Five real documents, cut to 1-3 pages: IRS Form W-9 (p1), IRS Form 1040 (p1), CDC MMWR Vol. 74 No. 14 (p1-3), a CDC supplementary table (p1), and a 1958 NASA report (pages 24, 38, 259). Sources, licences and SHA-256 hashes: `data/real/SOURCES.csv`. Facts were typed by hand from the visible page, not copied from the text layer (`scripts/add_real_ground_truth.py`; 19 facts for W-9, MMWR and the CDC table). The 1040 and NASA documents have no facts yet.

* **[measured]** On the two-column MMWR, all three tools found 7/7 facts and kept the correct reading order, including the jump from the bottom of the left column to the top of the right. Real two-column text was handled better than expected.
* **[measured]** On the W-9 form, PyMuPDF4LLM found only 2/6 facts. **[read]** It turned the whole form into a table: some text is only split by `<br>` inside cells (a matching effect, the words are present), but other text is damaged: words are cut at cell borders ("Social se|curity number"), characters are lost ("rint or typ"), and "send to the IRS." is missing. Open question for the mentor: should `normalise()` treat `<br>` as a space?
* **[measured]** MarkItDown missed only the rotated margin text "Print or type" on the W-9 (5/6). Docling found 6/6 but failed reading order on the form; on a form with side-by-side boxes the correct order is debatable.
* **[measured]** `check_text_layer.py` flagged the NASA report as SCAN_WITH_TEXT_LAYER: an old scan with an invisible OCR text layer. The quality of that old text layer has not been checked yet.

## Failure catalogue

Script: `scripts/make_failure_catalogue.py`; data: `results/failure_catalogue.csv`. The counts show what was tested, not which tool is worst: PyMuPDF4LLM was tested more deeply on Day 3, and two of its high-severity entries are setup risks (OCR switched off, no OCR engine installed), not failures under default settings.

{catalogue}
## Recommendation

Rule: accuracy first; if tied, the faster tool; licence as a final check. Numbers per document type (`scripts/make_recommendation_inputs.py`, `results/by_doc_type.md`):

{by_type}
| Document type | Best tool | Why | If AGPL is not acceptable |
|---|---|---|---|
| Digital PDF, simple | MarkItDown | All 8/8; fastest (0.03 s vs 0.22 s, 2.02 s) | Same |
| PDF with tables | Docling | Table cells 94% vs 88%, 81% (8.5 s vs 0.1 s) | Same |
| Two-column PDF | PyMuPDF4LLM | Order 2/2 (MarkItDown 1/2); 0.84 s vs Docling 5.62 s | Docling (2/2) |
| PDF with header/footer | MarkItDown | All 5/5; fastest | Same |
| PDF form | Docling | 6/6 facts vs 5/6, 2/6 | Same |
| Scanned PDF | PyMuPDF4LLM | 17/18 vs 18/18 (one lost space), but 6/6 at 12, 20 degrees and 36 dpi where Docling got 0/6; 2.16 s vs 3.21 s | Docling, only for straight, clear scans |
| Word (.docx) | Docling | Table cells 88% vs 75% | Same |
| Slides (.pptx) | Tie | Both 8/8, 100% table cells | Same |
| Spreadsheet (.xlsx) | Docling (narrowly) | Table cells 86% vs 84% | Same |

Caveats: 1-3 documents per type, so one-fact or few-percent differences are not reliable; PDF table cell scores come from `02_table.pdf` only; licences as recorded in section 1 (to verify). Always run `check_text_layer.py` first: MarkItDown returns empty output on scans with no warning (0/18).

Proposed routing for the parsing service: image-only PDF -> PyMuPDF4LLM with OCR; Word, slides, spreadsheets -> Docling; digital PDF -> MarkItDown, or Docling if it contains tables or forms.

"""

p.write_text(text.replace(ANCHOR, SECTIONS + ANCHOR), encoding="utf-8")
print("Added 3 Day 3 sections to docs/report.md")