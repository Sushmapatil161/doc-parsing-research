"""Day 3, Task 4: failure catalogue. One entry per failure, with type, tool, document and a short example.

Types: empty_output, wrong_order, broken_table, dropped_header_footer, merged_columns, ocr_error,
       dropped_text (added Day 3: text missing that is not a header/footer, e.g. rotated margin text).
Severity: high = content silently lost; medium = content damaged; low = debatable or cosmetic.
Writes: results/failure_catalogue.csv, results/failure_catalogue.md
"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
F = [
    # (tool, document, type, severity, expected, got, evidence)
    ("markitdown", "07_scanned.pdf, 14_scan_tilted.pdf, 15_scan_lowres.pdf", "empty_output", "high",
     "6 facts", "0 facts, no OCR for PDFs, no warning", "[measured] results/facts.csv"),
    ("pymupdf4llm", "07_scanned.pdf (use_ocr=False)", "empty_output", "high",
     "6 facts", "0 characters, no warning", "[measured] results/noocr_facts.csv"),
    ("pymupdf4llm", "any scan, no OCR engine installed", "empty_output", "high",
     "OCR text", "OCR skipped silently", "[read] select_ocr_function() returns None"),
    ("pymupdf4llm", "07_scanned.pdf", "ocr_error", "low",
     "Annual Summary 2026", "AnnualSummary 2026", "[measured] results/facts.csv"),
    ("docling (RapidOCR, EasyOCR, full-page OCR)", "sweep tilt_12.pdf, tilt_20.pdf", "empty_output", "high",
     "6 facts", "<!-- image --> only (0/6), no warning", "[measured] results/sweep.csv"),
    ("docling (RapidOCR, EasyOCR, full-page OCR)", "sweep dpi_036.pdf", "empty_output", "high",
     "6 facts", "<!-- image --> only (0/6), no warning", "[measured] results/sweep.csv"),
    ("docling + EasyOCR", "sweep tilt_08.pdf, dpi_050.pdf", "ocr_error", "medium",
     "6 facts", "3/6 and 2/6 facts", "[measured] results/sweep.csv"),
    ("markitdown", "02_table.docx", "broken_table", "medium",
     "4 header cells", "0/4 header cells correct (merged header cells)", "[measured] results/table_scores.csv"),
    ("pymupdf4llm", "02_table.pdf", "broken_table", "medium",
     "4 header cells", "1/4 header cells correct", "[measured] results/table_scores.csv"),
    ("markitdown", "03_two_column.pdf", "wrong_order", "medium",
     "heading before its column text", "heading placed in the wrong position (Day 2)",
     "[measured] results/reading_order.csv"),
    ("markitdown", "21_irs_w9_p1.pdf", "dropped_text", "medium",
     "Print or type", "missing (rotated margin text)", "[measured] results/facts.csv"),
    ("pymupdf4llm", "21_irs_w9_p1.pdf", "broken_table", "high",
     "Social security number", "Social se|curity number (form turned into a fake table, words cut at cell borders)",
     "[measured] 2/6 facts; [read] results/pymupdf4llm/21_irs_w9_p1.pdf.md"),
    ("pymupdf4llm", "21_irs_w9_p1.pdf", "dropped_text", "high",
     "Give form to the requester. Do not send to the IRS.", "'send to the IRS.' missing; 'Print or type' -> 'rint or typ'",
     "[read] results/pymupdf4llm/21_irs_w9_p1.pdf.md"),
    ("docling", "21_irs_w9_p1.pdf", "wrong_order", "low",
     "Exempt payee code before Part I heading", "out of order (form columns, order debatable)",
     "[measured] results/reading_order.csv"),
    ("pymupdf4llm", "13_scan_phone.pdf (real photo)", "empty_output", "high",
     "6 facts", "0 characters, no warning: auto-detection skipped OCR; force_ocr=True gives 6/6",
     "[measured] results/phone_photo.csv"),
    ("docling + EasyOCR", "13_scan_phone.pdf (real photo)", "ocr_error", "medium",
     "Kestrel Systems; 9,84,000", "both missing (4/6)", "[measured] results/phone_photo.csv"),
]

rows = [{"id": i, "tool": t, "document": d, "failure_type": ft, "severity": s,
         "expected": e, "got": g, "evidence": ev}
        for i, (t, d, ft, s, e, g, ev) in enumerate(F, start=1)]

with open(ROOT / "results" / "failure_catalogue.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

md = ["| # | Tool | Document | Type | Severity | Expected | Got | Evidence |",
      "|---|---|---|---|---|---|---|---|"]
for r in rows:
    cells = [str(r[k]).replace("|", "\\|") for k in
             ["id", "tool", "document", "failure_type", "severity", "expected", "got", "evidence"]]
    md.append("| " + " | ".join(cells) + " |")

md += ["", "| Tool | Failures | of which high severity |", "|---|---|---|"]
main_tool = lambda t: t.split()[0]
by_tool = Counter(main_tool(r["tool"]) for r in rows)
high = Counter(main_tool(r["tool"]) for r in rows if r["severity"] == "high")
for tool, n in sorted(by_tool.items()):
    md.append(f"| {tool} | {n} | {high[tool]} |")

md += ["", "| Failure type | Count |", "|---|---|"]
for ft, n in Counter(r["failure_type"] for r in rows).most_common():
    md.append(f"| {ft} | {n} |")

(ROOT / "results" / "failure_catalogue.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"Wrote {len(rows)} failures to results/failure_catalogue.csv and .md")
for tool, n in sorted(by_tool.items()):
    print(f"  {tool:12} {n} failures, {high[tool]} high severity")