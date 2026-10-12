\# Setup



\## Hardware

\- CPU: (name), (X) cores / (Y) logical processors

\- RAM: (X) GB

\- GPU: (name) (write "integrated, no NVIDIA GPU" if it's Intel/AMD graphics only)

\- Free disk space: (X) GB on C:

\- OS: (OS Name), version (OS Version)

\- Python: (version)

\- Power: plugged in during all benchmarks





\## Software

\- Python 3.10.3 (virtual environment in .venv)

\- markitdown 0.1.8

\- docling 2.138.0

\- pymupdf4llm 1.28.2

\- Full package list: requirements.txt



\## Installation

python -m venv .venv

.venv\\Scripts\\Activate.ps1

pip install "markitdown\[pdf,docx,pptx,xlsx]" docling pymupdf4llm psutil





\- Docling first run downloads AI models from Hugging Face (docling-layout-heron etc.).

&#x20; First run took about \_\_ minutes. Models are cached in C:\\Users\\sushm\\.cache\\huggingface.

\- Warnings on first run: unauthenticated HF Hub requests (harmless) and

&#x20; "symlinks not supported" on Windows (harmless, uses slightly more disk space).

## How to run the benchmark
1. Activate the environment: .venv\Scripts\Activate.ps1
2. Run all tools on all documents (3 repeats, about 30-40 minutes on this laptop):
   python scripts/run_benchmark.py
3. Check facts and build the results table:
   python scripts/check_facts.py
4. Outputs: results/<tool>/*.md, results/runs.csv, results/summary.csv,
   results/facts.csv, results/results_table.md, results/run_info.json
5. By-eye ratings are stored in results/manual_checks.csv and merged into the table automatically.
Notes:
- Docling downloads its AI models on first use (about 2 minutes, cached in C:\Users\sushm\.cache\huggingface).
- Keep the laptop plugged in and avoid other heavy work during runs.
- Test documents can be regenerated with the scripts in scripts/make_test_docs/.
