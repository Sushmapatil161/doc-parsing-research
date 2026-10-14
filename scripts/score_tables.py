"""Score tables cell by cell against the answer keys in data/expected_tables/.

For each tool output that should contain a table, find the Markdown table
that best matches the expected table and count exactly matching cells.

Usage:
  python scripts/score_tables.py
      score all tables, write results/table_scores.csv
  python scripts/score_tables.py --show docling 02_table.pdf
      show one table side by side with the answer key
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = ROOT / "data" / "expected_tables"
RESULTS = ROOT / "results"
DETAILS = RESULTS / "table_details"
TOOLS = ["markitdown", "pymupdf4llm", "docling"]

# Which answer keys belong to which document
DOC_TABLES = {
    "02_table.docx": ["02_table.csv"],
    "02_table.pdf": ["02_table.csv"],
    "04_slides.pptx": ["04_slides.csv"],
    "04_slides.pdf": ["04_slides.csv"],
    "05_sheet.xlsx": ["05_sheet_Invoices.csv", "05_sheet_Staff.csv"],
}
SEP = re.compile(r"^:?-+:?$")


def clean(text):
    """Drop Markdown bold, backslash escapes and <br>; collapse spaces."""
    text = text.replace("**", "").replace("\\", "")
    text = re.sub(r"<br\s*/?>", " ", text)
    return " ".join(text.split())


def clean_header(text):
    """Headers also ignore spaces, '-' and '/'."""
    return re.sub(r"[\s\-/]", "", clean(text)).lower()


def is_separator(row):
    cells = [c for c in row if c]
    return bool(cells) and all(SEP.match(c) for c in cells)


def read_expected(name):
    path = EXPECTED / name
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def find_tables(md_text):
    """Return every Markdown table as (header_row, body_rows)."""
    tables = []
    block = []
    for line in md_text.splitlines() + [""]:
        s = line.strip()
        if s.startswith("|"):
            cells = [clean(c) for c in s.strip("|").split("|")]
            block.append(cells)
        elif block:
            rows = [r for r in block if not is_separator(r)]
            if rows:
                tables.append((rows[0], rows[1:]))
            block = []
    return tables


def score(exp_header, exp_body, out_header, out_body):
    """Compare one output table with the answer key.
    Returns (cells, extra_rows).
    Each cell is (part, row_label, column, expected, got, ok)."""
    cells = []
    for j, e in enumerate(exp_header):
        got = out_header[j] if j < len(out_header) else ""
        ok = clean_header(e) == clean_header(got)
        cells.append(("header", "header", j, e, got, ok))
    used = set()
    for row in exp_body:
        key = clean(row[0])
        match = None
        for i, r in enumerate(out_body):
            if i not in used and r and clean(r[0]) == key:
                match = i
                break
        out = []
        if match is not None:
            out = out_body[match]
            used.add(match)
        label = row[0] or "(blank)"
        for j, e in enumerate(row):
            if match is None:
                got = "(row missing)"
            elif j < len(out):
                got = out[j]
            else:
                got = "(no cell)"
            ok = match is not None and clean(e) == clean(got)
            cells.append(("body", label, j, e, got, ok))
    extra = []
    for i, r in enumerate(out_body):
        if i not in used and any(r):
            extra.append(r)
    return cells, extra


def n_ok(cells):
    return sum(1 for c in cells if c[5])


def evaluate(tool, doc, key):
    """Score the best-matching table in one tool output.
    Returns None if the tool has no output for this document."""
    md_path = RESULTS / tool / (doc + ".md")
    if not md_path.exists():
        return None
    exp_header, exp_body = read_expected(key)
    text = md_path.read_text(encoding="utf-8", errors="replace")
    tables = find_tables(text)
    best = None
    for out_header, out_body in tables:
        res = score(exp_header, exp_body, out_header, out_body)
        if best is None or n_ok(res[0]) > n_ok(best[0]):
            best = res
    if best is None:
        best = score(exp_header, exp_body, [], [])
    return best[0], best[1], len(tables)


def totals(cells):
    h = [c for c in cells if c[0] == "header"]
    b = [c for c in cells if c[0] == "body"]
    return n_ok(h), len(h), n_ok(b), len(b)


def score_all():
    rows = []
    head = "{:12} {:16} {:22} {:>7} {:>7} {:>13} {:>5}"
    print(head.format("tool", "file", "table", "header",
                      "body", "cells", "extra"))
    line = "{:12} {:16} {:22} {:>3}/{:<3} {:>3}/{:<3} {:>3}/{:<3} ({:>3}%) {:>5}"
    for doc, keys in DOC_TABLES.items():
        for key in keys:
            for tool in TOOLS:
                res = evaluate(tool, doc, key)
                if res is None:
                    continue
                cells, extra, n_tables = res
                h_ok, h_n, b_ok, b_n = totals(cells)
                ok = h_ok + b_ok
                n = h_n + b_n
                pct = round(100 * ok / n)
                rows.append({
                    "tool": tool, "file": doc, "table": key,
                    "tables_in_output": n_tables,
                    "header_ok": h_ok, "header_total": h_n,
                    "body_ok": b_ok, "body_total": b_n,
                    "cells_ok": ok, "cells_total": n,
                    "percent": pct, "extra_rows": len(extra),
                })
                print(line.format(tool, doc, key, h_ok, h_n, b_ok, b_n,
                                  ok, n, pct, len(extra)))
    out = RESULTS / "table_scores.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print()
    print("Wrote", out.relative_to(ROOT), "(" + str(len(rows)) + " rows)")


def grid(rows):
    """Format rows as an aligned Markdown table (first row = header)."""
    ncol = max(len(r) for r in rows)
    rows = [list(r) + [""] * (ncol - len(r)) for r in rows]
    widths = []
    for j in range(ncol):
        widths.append(max(3, max(len(r[j]) for r in rows)))
    lines = []
    for i, r in enumerate(rows):
        parts = [r[j].ljust(widths[j]) for j in range(ncol)]
        lines.append("| " + " | ".join(parts) + " |")
        if i == 0:
            dashes = ["-" * (w + 2) for w in widths]
            lines.append("|" + "|".join(dashes) + "|")
    return lines


def show(tool, doc):
    if doc not in DOC_TABLES:
        print(doc, "has no expected table. Choose from:")
        print(", ".join(DOC_TABLES))
        return
    DETAILS.mkdir(parents=True, exist_ok=True)
    for key in DOC_TABLES[doc]:
        res = evaluate(tool, doc, key)
        if res is None:
            print(tool, "has no output for", doc,
                  "(unsupported or failed).")
            return
        cells, extra, n_tables = res
        exp_header, exp_body = read_expected(key)
        ncol = len(exp_header)
        h_ok, h_n, b_ok, b_n = totals(cells)
        ok = h_ok + b_ok
        n = h_n + b_n
        pct = round(100 * ok / n)

        # Tool output in the answer key's layout; wrong cells marked [X]
        got_rows = []
        for i in range(0, len(cells), ncol):
            row = []
            for c in cells[i:i + ncol]:
                got, good = c[4], c[5]
                if good:
                    row.append(got)
                else:
                    row.append("[X] " + (got or "(empty)"))
            got_rows.append(row)

        out = []
        out.append("=== " + tool + " / " + doc + "  vs  answer key "
                   + key + "  (" + str(n_tables) + " table(s) in output) ===")
        out.append("Score: header " + str(h_ok) + "/" + str(h_n)
                   + ", body " + str(b_ok) + "/" + str(b_n)
                   + ", total " + str(ok) + "/" + str(n)
                   + " cells correct (" + str(pct) + "%)")
        out.append("")
        out.append("ANSWER KEY (correct table):")
        out.append("")
        out.extend(grid([exp_header] + exp_body))
        out.append("")
        out.append("TOOL OUTPUT (same layout, [X] = wrong cell):")
        out.append("")
        out.extend(grid(got_rows))
        out.append("")
        wrong = [c for c in cells if not c[5]]
        if wrong:
            out.append("WRONG CELLS:")
        else:
            out.append("WRONG CELLS: none")
        for c in wrong:
            label, j, e, got = c[1], c[2], c[3], c[4]
            out.append("  - " + label + ", column " + str(j + 1)
                       + ": expected '" + e + "', got '" + got + "'")
        if extra:
            out.append("")
            out.append("EXTRA ROWS in the tool's table"
                       " (not in the original table):")
            for r in extra:
                out.append("  - " + " | ".join(r))
        print()
        print("\n".join(out))
        name = tool + "__" + doc + "__" + key.replace(".csv", "") + ".md"
        path = DETAILS / name
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
        print()
        print("(saved to " + str(path.relative_to(ROOT)) + ")")


def main():
    sys.stdout.reconfigure(errors="replace")
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--show", nargs=2, metavar=("TOOL", "FILE"),
                   help="show one table side by side with the answer key")
    args = p.parse_args()
    if args.show:
        show(args.show[0], args.show[1])
    else:
        score_all()


if __name__ == "__main__":
    main()