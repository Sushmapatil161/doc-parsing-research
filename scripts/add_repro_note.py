"""One-off Day 3 edit: add a reproducibility note at the end of the report."""
from pathlib import Path

p = Path("docs/report.md")
text = p.read_text(encoding="utf-8")
HEADING = "## Reproducibility notes"
if HEADING in text:
    raise SystemExit("STOPPED: section already exists, nothing changed")

NOTE = f"""

{HEADING}

* **[measured]** On Day 3 the full benchmark was re-run (all documents, 3 repeats) to include the new scans. Fact counts and reading-order results for all Day 1 documents were identical; timings differ slightly, as expected. Day 2 results are kept under the git tag `before-day3-benchmark`.
* **[measured]** MarkItDown's output for `02_table.pdf` differed from Day 1: the footer line "Prepared by the Zentrix finance team." moved out of the table (extra rows 2 -> 1), with the same cell score (14/16). Docling's output for the same file also changed, with the same score. The input file, the tool versions and the PDF libraries were unchanged, and MarkItDown gave identical output in 5 fresh runs (`scripts/determinism_check.py`). The cause was not found: most likely an unrecorded package change on Day 1 between recording `requirements.txt` (commit `ff44102`) and running the benchmark (commit `07c603b`).
* **Lesson:** record `pip freeze` at the moment of every benchmark run, not only after installing tools. Also, the Day 1 `requirements.txt` was saved as UTF-16 (PowerShell `>`), which git treats as binary; `scripts/compare_requirements.py` reads both encodings.
"""

p.write_text(text.rstrip() + NOTE, encoding="utf-8")
print("Added reproducibility notes to docs/report.md")