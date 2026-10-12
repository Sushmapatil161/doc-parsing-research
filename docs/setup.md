# Setup
## Hardware
- CPU: 11th Gen Intel Core i5-1135G7 @ 2.40GHz, 4 cores / 8 logical processors
- RAM: 7.8 GB
- GPU: Intel Iris Xe Graphics (integrated, no NVIDIA GPU, so all tools run on CPU)
- Free disk space: 290.87 GB on C:
- OS: Microsoft Windows 11 Home Single Language, version 23H2 (build 10.0.22631)
- Python: 3.10.3
- Power: plugged in during all benchmarks
## Software
- Python 3.10.3 (virtual environment in .venv)
- markitdown 0.1.8
- docling 2.138.0
- pymupdf4llm 1.28.2
- Full package list: requirements.txt
## Installation
Run these in PowerShell from the repo folder:
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install "markitdown[pdf,docx,pptx,xlsx]" docling pymupdf4llm psutil
If activation fails with "running scripts is disabled", run once:
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
## First-run notes
- Docling downloads its AI models from Hugging Face on first use (docling-layout-heron etc.). The first run took about 2 minutes. Models are cached in C:\Users\sushm\.cache\huggingface.
- Warnings on first run are harmless: "unauthenticated requests to the HF Hub" and "symlinks not supported" on Windows (uses slightly more disk space).
## How to run the benchmark
1. Activate the environment: .venv\Scripts\Activate.ps1
2. Run all tools on all documents (3 repeats, about 30-40 minutes on this laptop): python scripts/run_benchmark.py
3. Check facts and build the results table: python scripts/check_facts.py
4. Outputs: results/(tool)/*.md, results/runs.csv, results/summary.csv, results/facts.csv, results/results_table.md, results/run_info.json
5. By-eye ratings are stored in results/manual_checks.csv and merged into the results table automatically.
## Notes
- Keep the laptop plugged in and avoid other heavy work during runs.
- Test documents can be regenerated with the scripts in scripts/make_test_docs/.
