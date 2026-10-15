"""Report whether each PDF has real text, or only images (needs OCR).

Usage:  python scripts/check_text_layer.py [folder]     (default: data)
Writes: results/text_layer.csv
"""
import csv
import sys
from pathlib import Path
import pymupdf

MIN_CHARS = 20      # fewer real characters than this = page has no usable text
COVER = 0.8         # an image covering 80%+ of the page = looks like a scan


def check_pdf(path):
    doc = pymupdf.open(path)
    n = len(doc)
    text_pages = scan_like_pages = 0
    for page in doc:
        if len(page.get_text().strip()) >= MIN_CHARS:
            text_pages += 1
        page_area = page.rect.width * page.rect.height
        img_area = 0
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                img_area += r.width * r.height
        if page_area and img_area / page_area >= COVER:
            scan_like_pages += 1

    if text_pages == 0:
        verdict = "IMAGE_ONLY: send to OCR"
    elif scan_like_pages == n:
        verdict = "SCAN_WITH_TEXT_LAYER: check text quality"
    elif text_pages < n:
        verdict = "MIXED: OCR the pages without text"
    else:
        verdict = "TEXT: no OCR needed"
    return {"file": Path(path).name, "pages": n, "text_pages": text_pages,
            "scan_like_pages": scan_like_pages, "verdict": verdict}


def needs_ocr(path):
    """Safety guard for the parsing service: True if any OCR is needed."""
    return not check_pdf(path)["verdict"].startswith("TEXT")


if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    rows = [check_pdf(p) for p in sorted(folder.rglob("*.pdf"))]
    Path("results").mkdir(exist_ok=True)
    with open("results/text_layer.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "pages", "text_pages", "scan_like_pages", "verdict"])
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['file']:28} {r['verdict']}")
    print("Wrote results/text_layer.csv")