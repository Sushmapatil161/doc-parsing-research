"""One-off Day 3 edit: update the routing sentence after the real phone photo result."""
from pathlib import Path

p = Path("docs/report.md")
text = p.read_text(encoding="utf-8")
OLD = ("Proposed routing for the parsing service: image-only PDF -> PyMuPDF4LLM with OCR; "
       "Word, slides, spreadsheets -> Docling; digital PDF -> MarkItDown, or Docling if it contains tables or forms.")
NEW = ("Proposed routing for the parsing service: image-only PDF -> Docling + RapidOCR; if the output is only "
       "`<!-- image -->` or nearly empty, retry with PyMuPDF4LLM `force_ocr=True` (each covers the other's silent "
       "failure: Docling on tilted or tiny pages, PyMuPDF4LLM on the real photo). Word, slides, spreadsheets -> "
       "Docling; digital PDF -> MarkItDown, or Docling if it contains tables or forms. Never accept empty output "
       "without a check: every empty_output failure in the catalogue came with no error or warning.")
if text.count(OLD) != 1:
    raise SystemExit("STOPPED, nothing changed: routing sentence not found exactly once")
p.write_text(text.replace(OLD, NEW), encoding="utf-8")
print("Routing sentence updated")