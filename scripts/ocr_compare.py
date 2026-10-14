"""Compare OCR engines inside Docling on the scanned page.

Each engine runs in a fresh Python process (fair cold start).
In each process: first conversion (includes OCR model loading),
then a second warm conversion. Facts are scored against
data/ground_truth.json. Outputs and logs go to results/ocr/.

Usage:
  python scripts/ocr_compare.py                    all engines, 3 repeats
  python scripts/ocr_compare.py --repeats 1        quick test
  python scripts/ocr_compare.py --engines easyocr  one engine only
"""
import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN = ROOT / "data" / "07_scanned.pdf"
TRUTH = ROOT / "data" / "ground_truth.json"
OUT = ROOT / "results" / "ocr"
ENGINES = ["auto", "rapidocr", "easyocr"]


def ocr_options(engine):
    from docling.datamodel import pipeline_options as po
    if engine == "auto":
        return None  # Docling default, as used on Day 1
    if engine == "rapidocr":
        return po.RapidOcrOptions(force_full_page_ocr=True)
    if engine == "easyocr":
        return po.EasyOcrOptions(lang=["en"], force_full_page_ocr=True)
    raise ValueError("unknown engine " + engine)


def worker(engine):
    """Runs inside a fresh process. Prints one JSON line at the end."""
    import psutil
    t0 = time.perf_counter()
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter
    from docling.document_converter import PdfFormatOption
    t1 = time.perf_counter()

    opts = PdfPipelineOptions()
    opts.do_ocr = True
    custom = ocr_options(engine)
    if custom is not None:
        opts.ocr_options = custom
    fmt = PdfFormatOption(pipeline_options=opts)
    conv = DocumentConverter(format_options={InputFormat.PDF: fmt})

    md1 = conv.convert(str(SCAN)).document.export_to_markdown()
    t2 = time.perf_counter()
    md2 = conv.convert(str(SCAN)).document.export_to_markdown()
    t3 = time.perf_counter()

    mem = psutil.Process().memory_info()
    peak = getattr(mem, "peak_wset", mem.rss) / (1024 * 1024)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("docling_" + engine + ".md")).write_text(md2, encoding="utf-8")
    print(json.dumps({
        "import_s": round(t1 - t0, 2),
        "first_s": round(t2 - t1, 2),
        "warm_s": round(t3 - t2, 2),
        "peak_mb": round(peak),
        "same_output": md1 == md2,
        "markdown": md2,
    }))


def score(md, facts):
    from score_tables import clean
    text = clean(md)
    found = [f for f in facts if clean(f) in text]
    missing = [f for f in facts if clean(f) not in text]
    return found, missing


def run_one(engine, repeat):
    cmd = [sys.executable, str(Path(__file__)), "--worker", engine]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    log = OUT / ("docling_" + engine + "_run" + str(repeat) + "_log.txt")
    OUT.mkdir(parents=True, exist_ok=True)
    log.write_text(p.stderr, encoding="utf-8")
    lines = [x for x in p.stdout.splitlines() if x.startswith("{")]
    if p.returncode != 0 or not lines:
        return None, log
    return json.loads(lines[-1]), log


def mean(xs):
    return round(sum(xs) / len(xs), 2) if xs else None


def driver(engines, repeats):
    from score_tables import grid
    with open(TRUTH, encoding="utf-8-sig") as f:
        facts = json.load(f)["07_scanned"]
    rows = []
    for engine in engines:
        for r in range(1, repeats + 1):
            print("running", engine, "repeat", r, "of", repeats, "...",
                  flush=True)
            res, log = run_one(engine, r)
            if res is None:
                print("   FAILED - see", log.relative_to(ROOT))
                rows.append({"engine": engine, "repeat": r,
                             "status": "failed"})
                continue
            found, missing = score(res["markdown"], facts)
            print("   facts", len(found), "/", len(facts),
                  "| first", res["first_s"], "s | warm", res["warm_s"],
                  "s | peak", res["peak_mb"], "MB")
            rows.append({
                "engine": engine, "repeat": r, "status": "ok",
                "facts_found": len(found), "facts_total": len(facts),
                "missing": "; ".join(missing),
                "import_s": res["import_s"], "first_s": res["first_s"],
                "warm_s": res["warm_s"], "peak_mb": res["peak_mb"],
                "same_output": res["same_output"],
            })
    keys = ["engine", "repeat", "status", "facts_found", "facts_total",
            "missing", "import_s", "first_s", "warm_s", "peak_mb",
            "same_output"]
    csv_path = ROOT / "results" / "ocr_compare.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    table = [["Engine", "Runs OK", "Facts found", "Missing",
              "First run s (mean)", "Warm s (mean)", "Peak MB (max)"]]
    for engine in engines:
        ok = [x for x in rows if x["engine"] == engine
              and x["status"] == "ok"]
        if not ok:
            table.append([engine, "0/" + str(repeats), "-", "-",
                          "-", "-", "-"])
            continue
        table.append([
            engine, str(len(ok)) + "/" + str(repeats),
            str(ok[0]["facts_found"]) + "/" + str(ok[0]["facts_total"]),
            ok[0]["missing"] or "none",
            str(mean([x["first_s"] for x in ok])),
            str(mean([x["warm_s"] for x in ok])),
            str(max(x["peak_mb"] for x in ok)),
        ])
    print()
    print("\n".join(grid(table)))
    print()
    print("Wrote", csv_path.relative_to(ROOT),
          "and outputs/logs in", OUT.relative_to(ROOT))


def main():
    sys.stdout.reconfigure(errors="replace")
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--engines", nargs="+", default=ENGINES,
                   choices=ENGINES)
    p.add_argument("--worker", help=argparse.SUPPRESS)
    args = p.parse_args()
    if args.worker:
        worker(args.worker)
    else:
        driver(args.engines, args.repeats)


if __name__ == "__main__":
    main()