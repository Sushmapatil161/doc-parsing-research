"""Reading-order check: do the expected facts appear in the output
in the same order as in the original document?

Facts in data/ground_truth.json are listed in human reading order.
For each output we find the first position of every fact, then count
the largest number of facts that appear in the correct order.
Facts outside that sequence are reported as OUT OF ORDER.

Usage:
  python scripts/reading_order.py
      check all outputs, write results/reading_order.csv
  python scripts/reading_order.py --show markitdown 03_two_column.pdf
      show one document as a table, fact by fact
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from score_tables import clean, grid

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DETAILS = RESULTS / "order_details"
TRUTH = ROOT / "data" / "ground_truth.json"
TOOLS = ["markitdown", "pymupdf4llm", "docling"]


def load_truth():
    with open(TRUTH, encoding="utf-8-sig") as f:
        return json.load(f)


def positions(text, facts):
    """First character position of each fact in the text (None = missing)."""
    return [text.find(clean(fact)) if clean(fact) in text else None
            for fact in facts]


def longest_in_order(pos):
    """Indexes of the largest set of facts whose positions increase."""
    found = [(i, p) for i, p in enumerate(pos) if p is not None]
    n = len(found)
    if n == 0:
        return set()
    best = [1] * n
    prev = [-1] * n
    for i in range(n):
        for k in range(i):
            if found[k][1] < found[i][1] and best[k] + 1 > best[i]:
                best[i] = best[k] + 1
                prev[i] = k
    i = max(range(n), key=lambda x: best[x])
    keep = set()
    while i != -1:
        keep.add(found[i][0])
        i = prev[i]
    return keep


def check(tool, doc, truth):
    """Returns (facts, pos, in_order_set, text) or None if no output."""
    md_path = RESULTS / tool / (doc + ".md")
    if not md_path.exists():
        return None
    stem = doc.split(".")[0]
    facts = truth.get(stem, [])
    raw = md_path.read_text(encoding="utf-8", errors="replace")
    text = clean(raw)
    pos = positions(text, facts)
    return facts, pos, longest_in_order(pos), text


def verdict(found, in_order):
    if found < 2:
        return "n/a"
    return "PASS" if in_order == found else "FAIL"


def check_all():
    truth = load_truth()
    rows = []
    fmt = "{:12} {:24} {:>9} {:>9} {:>6}  {}"
    print(fmt.format("tool", "file", "found", "in order",
                     "order", "out of order"))
    for tool in TOOLS:
        folder = RESULTS / tool
        if not folder.exists():
            continue
        for md in sorted(folder.glob("*.md")):
            doc = md.name[:-3]
            res = check(tool, doc, truth)
            if res is None:
                continue
            facts, pos, keep, text = res
            found = sum(1 for p in pos if p is not None)
            wrong = [facts[i] for i, p in enumerate(pos)
                     if p is not None and i not in keep]
            v = verdict(found, len(keep))
            rows.append({
                "tool": tool, "file": doc, "facts_total": len(facts),
                "found": found, "in_order": len(keep),
                "order_ok": v, "out_of_order": "; ".join(wrong),
            })
            print(fmt.format(tool, doc,
                             str(found) + "/" + str(len(facts)),
                             str(len(keep)) + "/" + str(found),
                             v, ", ".join(wrong)))
    out = RESULTS / "reading_order.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print()
    print("Wrote", out.relative_to(ROOT), "(" + str(len(rows)) + " rows)")


def show(tool, doc):
    truth = load_truth()
    res = check(tool, doc, truth)
    if res is None:
        print(tool, "has no output for", doc, "(unsupported or failed).")
        return
    facts, pos, keep, text = res
    found = sum(1 for p in pos if p is not None)
    v = verdict(found, len(keep))

    table = [["#", "Expected fact (reading order)", "Found at char",
              "Status"]]
    for i, fact in enumerate(facts):
        if pos[i] is None:
            status = "missing"
            where = "-"
        elif i in keep:
            status = "in order"
            where = str(pos[i])
        else:
            status = "OUT OF ORDER"
            where = str(pos[i])
        table.append([str(i + 1), fact, where, status])

    seen = sorted((p, facts[i]) for i, p in enumerate(pos) if p is not None)

    out = []
    out.append("=== " + tool + " / " + doc + " ===")
    out.append("Facts found " + str(found) + "/" + str(len(facts))
               + ", in order " + str(len(keep)) + "/" + str(found)
               + "  ->  reading order: " + v)
    out.append("")
    out.extend(grid(table))
    out.append("")
    out.append("Order in the tool output (top to bottom):")
    out.append("  " + " -> ".join(f for p, f in seen))
    wrong = [i for i, p in enumerate(pos)
             if p is not None and i not in keep]
    if wrong:
        out.append("")
        out.append("Text around each out-of-order fact:")
        for i in wrong:
            a = max(0, pos[i] - 60)
            b = pos[i] + len(clean(facts[i])) + 60
            out.append("  - " + facts[i] + ": ..." + text[a:b] + "...")
    print()
    print("\n".join(out))
    DETAILS.mkdir(parents=True, exist_ok=True)
    path = DETAILS / (tool + "__" + doc + ".md")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print()
    print("(saved to " + str(path.relative_to(ROOT)) + ")")


def main():
    sys.stdout.reconfigure(errors="replace")
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--show", nargs=2, metavar=("TOOL", "FILE"),
                   help="show one document fact by fact")
    args = p.parse_args()
    if args.show:
        show(args.show[0], args.show[1])
    else:
        check_all()


if __name__ == "__main__":
    main()