"""Count ground-truth facts in the OCR on/off outputs (Day 3, Task 1).

Uses the same normalise() as check_facts.py, so the matching rule is identical.
Reads:  data/ground_truth.json, results/noocr/*.md
Writes: results/noocr_facts.csv
"""
import csv
import json
from pathlib import Path
from check_facts import normalise

ROOT = Path(__file__).resolve().parent.parent
truth = json.loads((ROOT / "data" / "ground_truth.json").read_text(encoding="utf-8"))

rows = []
for out in sorted((ROOT / "results" / "noocr").glob("*.md")):
    key, setting = out.stem.split("_ocr_")        # "07_scanned", "off" / "on"
    facts = truth[key]
    text = normalise(out.read_text(encoding="utf-8"))
    missing = [f for f in facts if normalise(f) not in text]
    found = len(facts) - len(missing)
    rows.append({"tool": "pymupdf4llm", "file": key, "ocr": setting,
                 "chars": len(text.strip()), "found": found, "total": len(facts),
                 "missing": "; ".join(missing)})
    print(f"ocr={setting:3}  found {found}/{len(facts)}  missing: {missing}")

with open(ROOT / "results" / "noocr_facts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print("Wrote results/noocr_facts.csv")