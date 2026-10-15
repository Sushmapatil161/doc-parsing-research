"""Day 3, Task 2: score the real phone photo (13_scan_phone.pdf) with every tool and OCR setup.

Same setups as ocr_sweep.py, plus MarkItDown and PyMuPDF4LLM with force_ocr=True; one run each.
Same normalise() as check_facts.py.
Writes: results/phone_photo.csv, outputs in results/phone_photo/
"""
import csv
import json
import time
from pathlib import Path
from check_facts import normalise
from ocr_sweep import docling_engine, pymupdf4llm_engine

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "13_scan_phone.pdf"
OUT = ROOT / "results" / "phone_photo"
OUT.mkdir(parents=True, exist_ok=True)
facts = json.loads((ROOT / "data" / "ground_truth.json").read_text(encoding="utf-8"))["13_scan_phone"]


def markitdown_engine():
    from markitdown import MarkItDown
    md = MarkItDown()
    return lambda p: md.convert(str(p)).text_content


def pymupdf4llm_force_engine():
    import pymupdf4llm
    return lambda p: pymupdf4llm.to_markdown(str(p), force_ocr=True)


ENGINES = {
    "markitdown": markitdown_engine,
    "docling_rapidocr": lambda: docling_engine("rapidocr"),
    "docling_rapidocr_fullpage": lambda: docling_engine("rapidocr", full_page=True),
    "docling_easyocr": lambda: docling_engine("easyocr"),
    "pymupdf4llm": pymupdf4llm_engine,
    "pymupdf4llm_force_ocr": pymupdf4llm_force_engine,
}

rows = []
for name, factory in ENGINES.items():
    run = factory()
    t = time.perf_counter()
    md = run(PDF)
    secs = round(time.perf_counter() - t, 2)
    (OUT / f"{name}.md").write_text(md, encoding="utf-8")
    text = normalise(md)
    missing = [f for f in facts if normalise(f) not in text]
    rows.append({"engine": name, "found": len(facts) - len(missing), "total": len(facts),
                 "chars": len(md.strip()), "seconds": secs, "missing": "; ".join(missing)})

with open(ROOT / "results" / "phone_photo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print("\nReal phone photo (13_scan_phone.pdf):")
for r in rows:
    print(f"  {r['engine']:26} {r['found']}/{r['total']}  {r['chars']:5} chars  {r['seconds']:6.2f}s  missing: {r['missing'] or '-'}")
print("Wrote results/phone_photo.csv")