"""Day 3 Task 2: find where OCR breaks. One change at a time: tilt, then resolution.

Makes data/sweep/*.pdf from data/07_scanned.pdf, runs each OCR setup once on each file,
and scores facts with the same normalise() as check_facts.py.
Setups: Docling + RapidOCR (default), Docling + RapidOCR with force_full_page_ocr,
        Docling + EasyOCR, PyMuPDF4LLM (uses RapidOCR).
Usage:  python scripts/ocr_sweep.py
Writes: results/sweep.csv, outputs in results/sweep/<engine>/
"""
import csv
import json
import time
from pathlib import Path
import pymupdf
from PIL import Image
from check_facts import normalise

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "07_scanned.pdf"
SWEEP = ROOT / "data" / "sweep"
OUT = ROOT / "results" / "sweep"
TILTS = [0, 4, 8, 12, 20]          # degrees, at 200 dpi
DPIS = [150, 100, 72, 50, 36]      # resolution, no tilt
BASE_DPI = 200


def make_files():
    SWEEP.mkdir(parents=True, exist_ok=True)
    pix = pymupdf.open(SRC)[0].get_pixmap(dpi=BASE_DPI)
    base = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    files = []
    for t in TILTS:
        f = SWEEP / f"tilt_{t:02d}.pdf"
        base.rotate(t, expand=True, fillcolor="white").save(f, "PDF", resolution=BASE_DPI)
        files.append(("tilt", t, f))
    for d in DPIS:
        f = SWEEP / f"dpi_{d:03d}.pdf"
        small = base.resize((round(base.width * d / BASE_DPI), round(base.height * d / BASE_DPI)))
        small.save(f, "PDF", resolution=d)
        files.append(("dpi", d, f))
    return files


def docling_engine(ocr_name, full_page=False):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions, EasyOcrOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    if ocr_name == "rapidocr":
        ocr = RapidOcrOptions(force_full_page_ocr=full_page)
    else:
        ocr = EasyOcrOptions(force_full_page_ocr=full_page)
    opts = PdfPipelineOptions(do_ocr=True, ocr_options=ocr)
    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    return lambda p: conv.convert(str(p)).document.export_to_markdown()


def pymupdf4llm_engine():
    import pymupdf4llm
    return lambda p: pymupdf4llm.to_markdown(str(p))


ENGINES = {
    "docling_rapidocr": lambda: docling_engine("rapidocr"),
    "docling_rapidocr_fullpage": lambda: docling_engine("rapidocr", full_page=True),
    "docling_easyocr": lambda: docling_engine("easyocr"),
    "pymupdf4llm": pymupdf4llm_engine,
}

if __name__ == "__main__":
    files = make_files()
    print(f"made {len(files)} files in data/sweep/")
    facts = json.loads((ROOT / "data" / "ground_truth.json").read_text(encoding="utf-8"))["07_scanned"]

    rows = []
    for name, factory in ENGINES.items():
        print(f"\n=== {name} (loading) ===", flush=True)
        run = factory()
        (OUT / name).mkdir(parents=True, exist_ok=True)
        for kind, level, f in files:
            t = time.perf_counter()
            try:
                md = run(f)
                status = "ok"
            except Exception as e:
                md, status = "", "error: " + str(e)[:80]
            secs = round(time.perf_counter() - t, 2)
            (OUT / name / (f.stem + ".md")).write_text(md, encoding="utf-8")
            text = normalise(md)
            missing = [x for x in facts if normalise(x) not in text]
            found = len(facts) - len(missing)
            rows.append({"engine": name, "kind": kind, "level": level, "file": f.name,
                         "found": found, "total": len(facts), "chars": len(md.strip()),
                         "seconds": secs, "status": status, "missing": "; ".join(missing)})
            print(f"{name:26} {f.name:14} {found}/{len(facts)}  {secs:6.2f}s  {status}", flush=True)

    with open(ROOT / "results" / "sweep.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    names = list(ENGINES)
    width = max(len(n) for n in names) + 2
    print("\nFacts found (out of 6):")
    print(f"{'file':14}" + "".join(f"{n:>{width}}" for n in names))
    for kind, level, f in files:
        cells = [next(r["found"] for r in rows if r["engine"] == n and r["file"] == f.name) for n in names]
        print(f"{f.name:14}" + "".join(f"{c:>{width}}" for c in cells))

    print("\nMedian seconds per page:")
    for n in names:
        secs = sorted(r["seconds"] for r in rows if r["engine"] == n)
        print(f"  {n:26} {secs[len(secs) // 2]:.2f}")
    print("\nWrote results/sweep.csv")