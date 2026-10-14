"""Regenerate all scores and the report tables, in the right order.

Does NOT re-run the benchmark. Run scripts/run_benchmark.py first
if you want new timings.
Usage: python scripts/regenerate_report.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    "check_facts.py",         # facts found       -> results/facts.csv
    "score_tables.py",        # table cells       -> results/table_scores.csv
    "reading_order.py",       # reading order     -> results/reading_order.csv
    "make_headline.py",       # headline numbers  -> top of docs/report.md
    "make_results_table.py",  # full table        -> section 3 of report
]

for step in STEPS:
    print()
    print("=====", step, "=====", flush=True)
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / step)],
                       cwd=ROOT)
    if r.returncode != 0:
        sys.exit("STOPPED: " + step + " failed")
print()
print("All done. Check with: git diff --stat")