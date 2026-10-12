"""Run every test document through every tool and record time and memory.

Usage (from the repo root, with the virtual environment active):
    python scripts/run_benchmark.py                      # all tools, 3 repeats
    python scripts/run_benchmark.py --repeats 1          # quicker
    python scripts/run_benchmark.py --tools markitdown pymupdf4llm

Writes:
    results/<tool>/<file>.md   the Markdown output of each tool
    results/runs.csv           every single run
    results/summary.csv        mean time and memory per tool and file
    results/run_info.json      hardware, Python and tool versions, settings
"""
import argparse
import csv
import datetime
import json
import os
import platform
import statistics
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
TOOLS = ["markitdown", "docling", "pymupdf4llm"]
DOC_TYPES = {".pdf", ".docx", ".pptx", ".xlsx"}
TIMEOUT_S = 900


def run_once(tool, doc):
    """Run parse_one.py in a fresh process and return its result dict."""
    out = RESULTS / tool / (doc.name + ".md")
    cmd = [sys.executable, str(ROOT / "scripts" / "parse_one.py"), tool, str(doc), str(out)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=TIMEOUT_S, env=env)
    except subprocess.TimeoutExpired:
        return {"tool": tool, "file": doc.name, "status": "timeout"}
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith("RESULT_JSON:"):
            return json.loads(line[len("RESULT_JSON:"):])
    return {"tool": tool, "file": doc.name, "status": "error",
            "error": (proc.stderr or "no output")[-300:]}


def tool_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools", nargs="+", default=TOOLS, choices=TOOLS)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    docs = sorted(p for p in DATA.iterdir() if p.suffix.lower() in DOC_TYPES)
    RESULTS.mkdir(exist_ok=True)

    info = {
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "os": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "repeats": args.repeats,
        "tools": {t: tool_version(t) for t in args.tools},
        "documents": [d.name for d in docs],
        "notes": "Each run is a fresh process. first_s includes lazy model loading; "
                 "warm_s is a second conversion in the same process. Default settings for every tool.",
    }
    (RESULTS / "run_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    # Warm-up: one untimed run per tool so first-time downloads (Docling models) don't count.
    for tool in args.tools:
        print(f"Warm-up: {tool} ...", flush=True)
        run_once(tool, DATA / "01_basic.pdf")

    rows = []
    for tool in args.tools:
        for doc in docs:
            for rep in range(1, args.repeats + 1):
                res = run_once(tool, doc)
                res["repeat"] = rep
                rows.append(res)
                msg = res["status"]
                if msg == "ok":
                    msg = f"first {res['first_s']}s, warm {res['warm_s']}s, peak {res['peak_mb']} MB"
                elif msg == "error":
                    msg = "ERROR " + res.get("error", "")[:80]
                print(f"{tool:12} {doc.name:24} run {rep}: {msg}", flush=True)
                if res["status"] == "unsupported":
                    break  # no point repeating

    fields = ["tool", "file", "repeat", "status", "load_s", "first_s", "warm_s", "peak_mb", "chars", "error"]
    with open(RESULTS / "runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    summary = []
    for tool in args.tools:
        for doc in docs:
            runs = [r for r in rows if r["tool"] == tool and r["file"] == doc.name]
            ok = [r for r in runs if r["status"] == "ok"]
            row = {"tool": tool, "file": doc.name,
                   "status": "ok" if ok else (runs[0]["status"] if runs else "missing"),
                   "ok_runs": f"{len(ok)}/{len(runs)}"}
            for key in ("first_s", "warm_s", "peak_mb"):
                vals = [r[key] for r in ok]
                row[key] = round(statistics.mean(vals), 3) if vals else ""
                row[key + "_sd"] = round(statistics.stdev(vals), 3) if len(vals) > 1 else ""
            summary.append(row)
    with open(RESULTS / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    print("\nDone. See results/summary.csv, then run: python scripts/check_facts.py")


if __name__ == "__main__":
    main()
