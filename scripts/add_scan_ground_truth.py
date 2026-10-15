"""Day 3: the hard scans show the same page as 07_scanned, so copy its 6 facts."""
import json
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "data" / "ground_truth.json"
truth = json.loads(p.read_text(encoding="utf-8"))

for key in ["13_scan_phone", "14_scan_tilted", "15_scan_lowres"]:
    truth[key] = list(truth["07_scanned"])
    print("added", key, "->", len(truth[key]), "facts")

p.write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")