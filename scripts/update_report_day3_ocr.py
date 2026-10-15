"""One-off Day 3 edit: replace the two 'inferred' OCR sentences with measured results."""
from pathlib import Path

p = Path("docs/report.md")
text = p.read_text(encoding="utf-8")

CHANGES = [
    ("* PyMuPDF4LLM most likely also used RapidOCR [inferred: it is the only OCR engine "
     "installed, and it makes the same spacing error]. Not proven.",
     "* PyMuPDF4LLM used RapidOCR [measured]: with `use_ocr=False` it found 0/6 facts "
     "(0 characters, no error or warning, 0.19 s); with the default `use_ocr=True` it found "
     "5/6 (5.79 s) and printed \"Using RapidOCR for OCR processing\". In the source, "
     "`select_ocr_function()` in `helpers/document_layout.py` picks RapidOCR when the "
     "`rapidocr` package is installed [read]. Scripts: `scripts/noocr_test.py`, "
     "`scripts/count_noocr_facts.py`; data: `results/noocr_facts.csv`."),
    ("* PyMuPDF4LLM read the scan without Tesseract installed; it most likely used RapidOCR "
     "[inferred, see 3b.3], not proven.",
     "* PyMuPDF4LLM read the scan without Tesseract installed because it used RapidOCR "
     "[measured, see 3b.3]. If no OCR engine is installed, it skips OCR silently "
     "[read: `select_ocr_function()` returns None], which gives empty output on scans. "
     "`scripts/check_text_layer.py` now flags image-only PDFs before parsing."),
]

for old, new in CHANGES:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"STOPPED, nothing changed: found {count} matches for:\n{old[:70]}...")
    text = text.replace(old, new)

p.write_text(text, encoding="utf-8")
print("Updated 2 sentences in docs/report.md")