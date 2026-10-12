"""Parse ONE file with ONE tool, in its own process, and report time + peak memory.

Usage: python scripts/parse_one.py <tool> <input_file> <output_md>
Prints one line: RESULT_JSON:{...}

Running each parse in a fresh process means memory numbers are not mixed between tools.
The file is converted twice in the same process:
  first_s = first conversion (includes lazy model loading, e.g. Docling's AI models)
  warm_s  = second conversion of the same file (models already in memory, like a running API)
"""
import json
import platform
import sys
import time
import traceback
from pathlib import Path

SUPPORTED = {
    "markitdown": {".pdf", ".docx", ".pptx", ".xlsx"},
    "docling": {".pdf", ".docx", ".pptx", ".xlsx"},
    "pymupdf4llm": {".pdf"},
}


def peak_memory_mb():
    """Peak memory of this process in MB (includes C/C++ libraries, unlike tracemalloc)."""
    import psutil
    info = psutil.Process().memory_info()
    if hasattr(info, "peak_wset"):  # Windows: peak working set
        return info.peak_wset / 1024 ** 2
    import resource  # Linux / macOS
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / 1024 if platform.system() == "Linux" else rss / 1024 ** 2


def load_tool(tool):
    """Import the tool and return a function: path -> markdown text."""
    if tool == "markitdown":
        from markitdown import MarkItDown
        converter = MarkItDown()
        return lambda path: converter.convert(path).text_content
    if tool == "docling":
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()  # default settings: OCR on, table structure on
        return lambda path: converter.convert(path).document.export_to_markdown()
    if tool == "pymupdf4llm":
        import pymupdf4llm
        return lambda path: pymupdf4llm.to_markdown(path)
    raise ValueError(f"Unknown tool: {tool}")


def main():
    tool, in_path, out_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    result = {"tool": tool, "file": in_path.name}

    if in_path.suffix.lower() not in SUPPORTED[tool]:
        result["status"] = "unsupported"
        print("RESULT_JSON:" + json.dumps(result))
        return

    try:
        t0 = time.perf_counter()
        convert = load_tool(tool)
        result["load_s"] = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        text = convert(str(in_path))
        result["first_s"] = round(time.perf_counter() - t0, 3)

        t0 = time.perf_counter()
        convert(str(in_path))
        result["warm_s"] = round(time.perf_counter() - t0, 3)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text or "", encoding="utf-8")
        result["chars"] = len(text or "")
        result["status"] = "ok"
    except Exception as exc:  # record the failure instead of crashing the whole benchmark
        result["status"] = "error"
        result["error"] = " ".join(f"{type(exc).__name__}: {exc}".split())[:300]
        traceback.print_exc(file=sys.stderr)

    result["peak_mb"] = round(peak_memory_mb(), 1)
    print("RESULT_JSON:" + json.dumps(result))


if __name__ == "__main__":
    main()
