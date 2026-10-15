"""Day 3, Task 5: summarise all results by document type, as input for the recommendation table.

Reads results/facts.csv, reading_order.csv, table_scores.csv, summary.csv
Writes results/by_doc_type.md
"""
import csv
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
TOOLS = ["markitdown", "docling", "pymupdf4llm"]
TYPES = {
    "Digital PDF, simple": ["01_basic.pdf"],
    "PDF with tables": ["02_table.pdf", "24_cdc_table_p1.pdf"],
    "Two-column PDF": ["03_two_column.pdf", "23_cdc_mmwr_p1-3.pdf"],
    "PDF with header/footer": ["06_header_footer.pdf"],
    "PDF form": ["21_irs_w9_p1.pdf"],
    "Scanned PDF": ["07_scanned.pdf", "14_scan_tilted.pdf", "15_scan_lowres.pdf"],
    "Word (.docx)": ["01_basic.docx", "02_table.docx", "03_two_column.docx", "06_header_footer.docx"],
    "Slides (.pptx)": ["04_slides.pptx"],
    "Spreadsheet (.xlsx)": ["05_sheet.xlsx"],
}


def read(name):
    with open(R / name, encoding="utf-8") as f:
        return list(csv.reader(f))[1:]


facts = {(r[0], r[1]): (int(r[2]), int(r[3])) for r in read("facts.csv")}
order = {(r[0], r[1]): r[5] for r in read("reading_order.csv")}
tables = {}
for r in read("table_scores.csv"):
    tables.setdefault((r[0], r[1]), []).append(float(r[10]))
with open(R / "summary.csv", encoding="utf-8") as f:
    summary = {(r["tool"], r["file"]): r for r in csv.DictReader(f)}

lines = ["| Document type | Tool | Facts found | Reading order PASS | Table cells | Median warm s |",
         "|---|---|---|---|---|---|"]
for dtype, files in TYPES.items():
    for tool in TOOLS:
        found = sum(facts[(tool, f)][0] for f in files if (tool, f) in facts)
        total = sum(facts[(tool, f)][1] for f in files if (tool, f) in facts)
        if total == 0 and not any((tool, f) in summary and summary[(tool, f)]["status"] == "ok" for f in files):
            lines.append(f"| {dtype} | {tool} | unsupported | | | |")
            continue
        o = [order.get((tool, f)) for f in files if order.get((tool, f)) in ("PASS", "FAIL")]
        t = [v for f in files for v in tables.get((tool, f), [])]
        w = [float(summary[(tool, f)]["warm_s"]) for f in files
             if (tool, f) in summary and summary[(tool, f)].get("warm_s")]
        lines.append(f"| {dtype} | {tool} | {found}/{total} | "
                     f"{o.count('PASS')}/{len(o) if o else '-'} | "
                     f"{f'{sum(t) / len(t):.0f}%' if t else '-'} | "
                     f"{f'{median(w):.2f}' if w else '-'} |")

(R / "by_doc_type.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))