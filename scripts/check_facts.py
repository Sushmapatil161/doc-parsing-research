"""Check how many ground-truth facts each tool's output contains, and build the results table.

Usage (from the repo root, after run_benchmark.py):
    python scripts/check_facts.py

Reads:  data/ground_truth.json, results/<tool>/<file>.md, results/summary.csv
Writes: results/facts.csv          found/total and the list of missing facts
        results/results_table.md   table for docs/report.md (fill the two "by eye" columns yourself)

Matching rule: case-insensitive, Markdown symbols (* _ # \\ `) removed, all whitespace
collapsed to single spaces, Unicode normalised (NFKC). A fact counts only if the whole
phrase appears. Rules are kept simple and identical for every tool.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
TOOLS = ["markitdown", "docling", "pymupdf4llm"]


def normalise(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[*_#`\\]", "", text)
    return re.sub(r"\s+", " ", text)


def main():
    truth = json.loads((ROOT / "data" / "ground_truth.json").read_text(encoding="utf-8"))
    summary = {}
    if (RESULTS / "summary.csv").exists():
        with open(RESULTS / "summary.csv", encoding="utf-8") as f:
            summary = {(r["tool"], r["file"]): r for r in csv.DictReader(f)}

    fact_rows, table_rows = [], []
    for tool in TOOLS:
        tool_dir = RESULTS / tool
        if not tool_dir.exists():
            continue
        for out in sorted(tool_dir.glob("*.md")):
            source = out.name[:-3]                 # e.g. 02_table.pdf
            key = source.split(".")[0]             # e.g. 02_table
            facts = truth.get(key)
            if facts is None:
                continue
            text = normalise(out.read_text(encoding="utf-8", errors="replace"))
            missing = [f for f in facts if normalise(f) not in text]
            found = len(facts) - len(missing)
            pct = round(100 * found / len(facts))
            fact_rows.append({"tool": tool, "file": source, "found": found, "total": len(facts),
                              "percent": pct, "missing": "; ".join(missing)})
            s = summary.get((tool, source), {})
            table_rows.append((source, tool, s.get("first_s", ""), s.get("warm_s", ""),
                               s.get("peak_mb", ""), f"{found}/{len(facts)} ({pct}%)"))

    with open(RESULTS / "facts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tool", "file", "found", "total", "percent", "missing"])
        w.writeheader()
        w.writerows(fact_rows)

    # Unsupported combinations (e.g. pymupdf4llm + docx) have no output file; list them too.
    for (tool, source), s in summary.items():
        if s["status"] != "ok" and not any(r[0] == source and r[1] == tool for r in table_rows):
            table_rows.append((source, tool, "", "", "", s["status"]))

    table_rows.sort()
    lines = ["| Document | Tool | First run (s) | Warm run (s) | Peak RAM (MB) | Facts found | Table intact? | Reading order OK? |",
             "|---|---|---|---|---|---|---|---|"]
    for r in table_rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " | ? | ? |")
    (RESULTS / "results_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"{'tool':12} {'file':24} found")
    for r in fact_rows:
        print(f"{r['tool']:12} {r['file']:24} {r['found']}/{r['total']}")
    print("\nWrote results/facts.csv and results/results_table.md")
    print("Now open the outputs and replace each '?' with Yes / Partial / No / n/a.")


if __name__ == "__main__":
    main()
