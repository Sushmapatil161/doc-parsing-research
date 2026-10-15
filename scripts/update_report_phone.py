"""One-off Day 3 edit: add the real phone photo result, update catalogue and scanned-PDF recommendation."""
from pathlib import Path

PHOTO_KIND = "the laptop screen showing the PDF in Edge (no printer available)"   # or: "a printed page"

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "docs" / "report.md"
text = p.read_text(encoding="utf-8")
if "13_scan_phone" in text:
    raise SystemExit("STOPPED: phone photo already in the report, nothing changed")

old_cat = (ROOT / "results" / "failure_catalogue_old.md").read_text(encoding="utf-8")
new_cat = (ROOT / "results" / "failure_catalogue.md").read_text(encoding="utf-8")
OLD_ROW = ("| Scanned PDF | PyMuPDF4LLM | 17/18 vs 18/18 (one lost space), but 6/6 at 12, 20 degrees and 36 dpi "
           "where Docling got 0/6; 2.16 s vs 3.21 s | Docling, only for straight, clear scans |")
NEW_ROW = ("| Scanned PDF | Docling + RapidOCR (default) for normal scans and photos; PyMuPDF4LLM with "
           "`force_ocr=True` for badly tilted or very low-resolution pages | Docling: 18/18 on benchmark scans "
           "and 6/6 on the real phone photo. PyMuPDF4LLM by default: 0/6 on the real photo (OCR silently "
           "skipped), but with force_ocr=True 6/6; it also read 6/6 at 12, 20 degrees and 36 dpi where Docling "
           "got 0/6 (sweep run with default settings; force_ocr not yet tested on the sweep) | "
           "Docling only, and flag tilted or low-resolution pages for review |")
ANCHOR = "## Real public-domain documents"

PHONE = f"""### Real phone photo

`13_scan_phone.pdf`: a phone photo of {PHOTO_KIND}, sent via WhatsApp (compressed), converted to PDF without EXIF data. Script: `scripts/score_phone_photo.py`; data: `results/phone_photo.csv`. One run per setup.

| Setup | Facts found |
|---|---|
| MarkItDown | 0/6 |
| Docling + RapidOCR | 6/6 |
| Docling + RapidOCR, full-page OCR | 6/6 |
| Docling + EasyOCR | 4/6 |
| PyMuPDF4LLM (default) | **0/6, 0 characters** |
| PyMuPDF4LLM, `force_ocr=True` | 6/6 |

* **[measured]** The real photo reversed the simulated-scan result: PyMuPDF4LLM, the most robust tool in the sweep, returned nothing by default, with no error. Its log shows no "OCR on page" line, so its automatic check decided the page needed no OCR. With `force_ocr=True` it found 6/6.
* Simulated scans flattered PyMuPDF4LLM: they are clean white pages, unlike a real photo. One real photo is a small sample; more real photos are needed.

"""

for old, new in [(OLD_ROW, NEW_ROW), (old_cat.strip(), new_cat.strip()), (ANCHOR, PHONE + ANCHOR)]:
    if text.count(old) != 1:
        raise SystemExit(f"STOPPED, nothing changed: could not find exactly one:\n{old[:80]}...")
    text = text.replace(old, new)

p.write_text(text, encoding="utf-8")
print("Report updated: phone photo section, failure catalogue (16 entries), scanned-PDF recommendation")