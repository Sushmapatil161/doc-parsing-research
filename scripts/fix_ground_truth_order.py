"""One-off fix (Day 2): put facts in data/ground_truth.json into true
reading order. Order checked against scripts/make_test_docs/make_docs.js
(02_table: line 49 before 50; 06_header_footer: lines 85, 91, 94, 95, 99).
Same facts, new order only, so fact scores do not change.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "ground_truth.json"

NEW_ORDER = {
    "02_table": ["Zentrix Corp", "Q3 2026", "Bengaluru Office",
                 "48,213", "16,050", "Mumbai Office", "39,870",
                 "Delhi Office", "27,645"],
    "06_header_footer": ["Nimbus Ltd", "Rohan Das",
                         "renegotiated vendor contracts", "2,15,000",
                         "14 January 2027"],
}

data = PATH.read_bytes()
bom = data.startswith(b"\xef\xbb\xbf")
raw = data.decode("utf-8-sig")
nl = "\r\n" if "\r\n" in raw else "\n"
truth = json.loads(raw)

for doc, facts in NEW_ORDER.items():
    if sorted(facts) != sorted(truth[doc]):
        raise SystemExit("STOPPED: facts differ for " + doc
                         + ", nothing saved")
    truth[doc] = facts

items = list(truth.items())
lines = ["{"]
for k, (doc, facts) in enumerate(items):
    comma = "," if k < len(items) - 1 else ""
    lines.append("  " + json.dumps(doc) + ": "
                 + json.dumps(facts, ensure_ascii=False) + comma)
lines.append("}")
text = nl.join(lines) + nl
out = text.encode("utf-8")
if bom:
    out = b"\xef\xbb\xbf" + out
PATH.write_bytes(out)
print("done: reordered " + ", ".join(NEW_ORDER))