"""Run one tool N times on one file, each in a fresh process, and compare output hashes.

Usage: python scripts/determinism_check.py markitdown data/02_table.pdf 5
"""
import subprocess
import sys

CODE = {
    "markitdown": "from markitdown import MarkItDown; t = MarkItDown().convert(p).text_content",
    "docling": ("from docling.document_converter import DocumentConverter; "
                "t = DocumentConverter().convert(p).document.export_to_markdown()"),
}

tool, path, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
child = f"import hashlib; p = r'{path}'; {CODE[tool]}; print(hashlib.sha256(t.encode('utf-8')).hexdigest()[:12], len(t))"

hashes = []
for i in range(1, n + 1):
    out = subprocess.run([sys.executable, "-c", child], capture_output=True, text=True)
    line = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else "ERROR " + out.stderr[-200:]
    hashes.append(line.split()[0])
    print(f"run {i}: {line}")

print("DETERMINISTIC" if len(set(hashes)) == 1 else f"NOT deterministic: {len(set(hashes))} different outputs")