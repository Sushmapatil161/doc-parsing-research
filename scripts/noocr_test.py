import sys, time
from pathlib import Path
import pymupdf4llm

pdf = sys.argv[1]
ocr_on = sys.argv[2] == "on"
out = Path("results/noocr")
out.mkdir(parents=True, exist_ok=True)

t = time.perf_counter()
md = pymupdf4llm.to_markdown(pdf, use_ocr=ocr_on)
secs = time.perf_counter() - t

name = Path(pdf).stem + ("_ocr_on" if ocr_on else "_ocr_off") + ".md"
(out / name).write_text(md, encoding="utf-8")
print(f"use_ocr={ocr_on}  chars={len(md.strip())}  seconds={secs:.2f}")