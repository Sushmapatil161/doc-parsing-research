"""Live demo: run all three tools on one PDF and show facts found + the start of each output.

Usage: python scripts/demo_live.py data/21_irs_w9_p1.pdf
Times include loading the tool (one fresh run each, not the benchmark method).
"""
import json
import sys
import time
from pathlib import Path
from check_facts import normalise

ROOT = Path(__file__).resolve().parent.parent
pdf = Path(sys.argv[1])
facts = json.loads((ROOT / "data" / "ground_truth.json").read_text(encoding="utf-8")).get(pdf.stem, [])
out_dir = ROOT / "results" / "demo"
out_dir.mkdir(parents=True, exist_ok=True)


def markitdown(p):
    from markitdown import MarkItDown
    return MarkItDown().convert(str(p)).text_content


def docling(p):
    from docling.document_converter import DocumentConverter
    return DocumentConverter().convert(str(p)).document.export_to_markdown()


def pymupdf4llm(p):
    import pymupdf4llm as m
    return m.to_markdown(str(p))


for name, run in [("markitdown", markitdown), ("docling", docling), ("pymupdf4llm", pymupdf4llm)]:
    print(f"\n{'=' * 20} {name} {'=' * 20}", flush=True)
    t = time.perf_counter()
    md = run(pdf)
    secs = time.perf_counter() - t
    (out_dir / f"{pdf.stem}_{name}.md").write_text(md, encoding="utf-8")
    text = normalise(md)
    missing = [f for f in facts if normalise(f) not in text]
    print(f"{len(facts) - len(missing)}/{len(facts)} facts  |  {len(md)} chars  |  {secs:.1f} s (incl. loading)")
    for f in missing:
        print(f"   missed: {f}")
    print("--- first lines ---")
    for line in [l for l in md.splitlines() if l.strip()][:6]:
        print("   " + line[:110])
print(f"\nFull outputs saved in results/demo/")