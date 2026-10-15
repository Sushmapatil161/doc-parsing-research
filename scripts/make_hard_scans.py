"""Make harder scan test files from data/07_scanned.pdf (Day 3, Task 2).

13_scan_phone.pdf  : REAL phone photo of the printed page (only if data/raw/phone_photo.jpg exists)
14_scan_tilted.pdf : SIMULATED, page rotated 4 degrees
15_scan_lowres.pdf : SIMULATED, page shrunk to 72 dpi + slight blur
Usage: python scripts/make_hard_scans.py
"""
from pathlib import Path
import pymupdf
from PIL import Image, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "07_scanned.pdf"
PHOTO = ROOT / "data" / "raw" / "phone_photo.jpg"
OUT = ROOT / "data"
TILT_DEG = 4
LOW_DPI = 72


def render(pdf, dpi):
    pix = pymupdf.open(pdf)[0].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


# Tilted page
tilted = render(SRC, 200).rotate(TILT_DEG, expand=True, fillcolor="white")
tilted.save(OUT / "14_scan_tilted.pdf", "PDF", resolution=200)
print("made 14_scan_tilted.pdf")

# Low resolution
img = render(SRC, 200)
small = img.resize((round(img.width * LOW_DPI / 200), round(img.height * LOW_DPI / 200)))
small = small.filter(ImageFilter.GaussianBlur(0.5))
small.save(OUT / "15_scan_lowres.pdf", "PDF", resolution=LOW_DPI)
print("made 15_scan_lowres.pdf")

# Real phone photo (EXIF such as location is not copied into the PDF)
if PHOTO.exists():
    photo = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")
    photo.save(OUT / "13_scan_phone.pdf", "PDF", resolution=150)
    print("made 13_scan_phone.pdf")
else:
    print("skipped 13_scan_phone.pdf (no data/raw/phone_photo.jpg yet)")