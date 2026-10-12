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

