### 10. Day 2: automatic checks and regenerating the report

```powershell
python scripts\make_expected_tables.py   # table answer keys, checked against the generators
python scripts\regenerate_report.py      # facts, table cells, reading order, headline, results table
python scripts\score_tables.py --show docling 02_table.pdf          # one table, cell by cell
python scripts\reading_order.py --show markitdown 03_two_column.pdf # one document, fact by fact
python scripts\ocr_compare.py            # Docling OCR engines on the scan (about 15-20 min)
```

Long Python code is saved as .py files with Notepad and then run; pasting long code into PowerShell can get stuck.

﻿# Document Parsing Research
Which tools turn PDFs, Word files, slides, spreadsheets and scanned pages into clean text and tables for AI systems most reliably, and at what cost in speed and memory?
This repository compares **MarkItDown**, **Docling** and **PyMuPDF4LLM** on a small, controlled test set. Everything needed to repeat the measurements is included: test documents, ground truth, scripts, raw results and the report.
- Full report: [docs/report.md](docs/report.md)
- Setup details and hardware used: [docs/setup.md](docs/setup.md)
- Daily progress and problems: [docs/research-log.md](docs/research-log.md)
- Every command run on Day 1, in order: [docs/commands-log.md](docs/commands-log.md)
## Key results (Day 1, CPU-only laptop)
| | MarkItDown | Docling | PyMuPDF4LLM |
|---|---|---|---|
| Formats | PDF, DOCX, PPTX, XLSX | PDF, DOCX, PPTX, XLSX | PDF only |
| Facts found, digital documents | 100% | 100% | 100% |
| Facts found, scanned page | 0% (no OCR) | 100% | 83% |
| Merged table header (PDF) | Partial | Correct | Partial |
| Two-column reading order (PDF) | Heading misplaced | Correct | Correct |
| Warm time per PDF | about 0.05 s | 4 to 20 s | 0.2 to 1 s |
| Peak memory on PDF | about 115 MB | 0.9 to 1.3 GB | about 310 MB |
| Licence | MIT | MIT (models Apache-2.0 / CDLA-Permissive-2.0) | AGPL-3.0 or commercial |
See [docs/report.md](docs/report.md) for the full table, method, observations and limitations.
## Repository layout
```
data/                       test documents (dummy content only)
  ground_truth.json         facts that must appear in each tool's output
  README.md                 what each test document checks
scripts/
  run_benchmark.py          runs every document through every tool, records time and memory
  parse_one.py              helper: parses one file with one tool in a fresh process
  check_facts.py            counts ground-truth facts found, builds the results table
  make_test_docs/           scripts that generated the test documents
results/
  markitdown/ docling/ pymupdf4llm/   Markdown output per tool and document
  runs.csv                  every single run
  summary.csv               mean time and memory per tool and document
  facts.csv                 facts found and the list of missing facts
  manual_checks.csv         by-eye ratings (table intact, reading order) with reasons
  results_table.md          final combined table (generated)
  run_info.json             Python, OS, tool versions and settings of the last run
docs/                       report, setup guide, research log, command log
requirements.txt            exact package versions used
```
## Requirements
- Windows 10 or 11 (tested on Windows 11; macOS/Linux should also work, but commands differ slightly)
- Python 3.10 or newer (tested with 3.10.3)
- Git
- About 5 GB free disk space (Docling installs PyTorch and downloads AI models)
- Internet connection for installation and for Docling's first run
- No GPU needed; all results in this repository were measured on CPU only
## How to run it, step by step
All commands are for **PowerShell**, run from the repository folder. For the full history of every command actually run (including mistakes and fixes), see [docs/commands-log.md](docs/commands-log.md).
### 1. Get the code
```powershell
git clone https://github.com/Sushmapatil161/doc-parsing-research.git
cd doc-parsing-research
```
Tip: do not clone into a OneDrive-synced folder (such as Desktop or Documents). OneDrive syncing slows down and can break Python virtual environments. A folder like `C:\Users\<you>\projects` works well.
### 2. Create and activate a virtual environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Your prompt should now start with `(.venv)`. If you see "running scripts is disabled on this system", run this once and try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
### 3. Install the tools
To reproduce the exact versions used in this research:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Or, to install the latest versions instead:
```powershell
pip install "markitdown[pdf,docx,pptx,xlsx]" docling pymupdf4llm psutil
```
Installation takes 10 to 20 minutes because Docling installs PyTorch (over 1 GB).
### 4. Check that each tool works
```powershell
markitdown data\01_basic.docx
docling data\01_basic.pdf --to md --output results\smoke_test
python -c "import pymupdf4llm; print(pymupdf4llm.to_markdown('data/01_basic.pdf'))"
```
Each command should print or save the "Project Falcon Overview" text. Docling's first run downloads its AI models (about 2 minutes); later runs reuse them. Warnings about "unauthenticated requests to the HF Hub" and "symlinks" are harmless.
### 5. Record your hardware and tool versions
Speed and memory numbers only mean something if the hardware is known. Record these in `docs/setup.md` before running the benchmark:
```powershell
systeminfo | findstr /C:"OS Name" /C:"OS Version" /C:"Total Physical Memory"
Get-CimInstance Win32_Processor | Select Name, NumberOfCores, NumberOfLogicalProcessors
Get-CimInstance Win32_VideoController | Select Name
Get-PSDrive C
python --version
```
Record the tool versions:
```powershell
pip show markitdown docling pymupdf4llm | findstr /B "Name Version"
```
To save your full package list without overwriting the original `requirements.txt`:
```powershell
pip freeze > requirements-mine.txt
```
The benchmark also saves Python, OS and tool versions automatically in `results/run_info.json`.
### 6. Run the benchmark
Quick run (1 repeat, about 10 to 20 minutes on a laptop CPU):
```powershell
python scripts/run_benchmark.py --repeats 1
```
Full run as used in the report (3 repeats, about 30 to 40 minutes):
```powershell
python scripts/run_benchmark.py
```
Only some tools:
```powershell
python scripts/run_benchmark.py --tools markitdown pymupdf4llm
```
What the script does:
- Runs one warm-up conversion per tool first, so model downloads are not timed.
- Runs every document with every tool, each run in a fresh Python process so memory numbers do not mix.
- Converts each file twice per run: "first" time includes model loading; "warm" time is a second conversion with models already loaded (like a running service).
- Marks unsupported combinations (for example PyMuPDF4LLM with a .docx file) as "unsupported".
- Records errors and timeouts (15 minutes per run) instead of crashing.
During the run, keep the laptop plugged in, do not let it sleep, and avoid other heavy work. All of these change the timing numbers.
### 7. Check facts and build the results table
```powershell
python scripts/check_facts.py
```
This compares every output with `data/ground_truth.json` (case-insensitive; Markdown symbols and extra spaces are ignored), writes `results/facts.csv`, and builds `results/results_table.md`.
### 8. By-eye checks (table intact, reading order)
These two columns cannot be measured automatically. Look at the outputs, for example all three tools on the table document:
```powershell
foreach ($t in "markitdown","docling","pymupdf4llm") { "===== $t =====" ; Get-Content "results\$t\02_table.pdf.md" -Encoding UTF8 }
```
Record your rating for every document and tool in `results/manual_checks.csv`:
- `table_intact`: Yes (rows and columns correct, merged header understood), Partial (values correct but headers broken), No (table lost), n/a (no table)
- `reading_order`: Yes, Partial, No, or n/a
Then build the table again. The ratings are merged in automatically:
```powershell
python scripts/check_facts.py
```
Check that every cell has been rated (prints nothing when complete):
```powershell
Select-String -Path results\results_table.md -Pattern "\?"
```
Tip: edit `.md` and `.csv` files in Notepad's **Syntax** mode, not "Formatted" mode. Formatted mode adds backslashes such as `\#` that break the Markdown.
### 9. Add the results to the report and save to GitHub
```powershell
Get-Content results\results_table.md -Encoding UTF8 | Add-Content docs\report.md -Encoding UTF8
git add .
git commit -m "Describe what you changed"
git push
```
## Useful commands for analysing results
Mean time and memory per tool and document:
```powershell
Import-Csv results\summary.csv | Format-Table tool, file, status, first_s, warm_s, peak_mb
```
Which facts each tool missed:
```powershell
Import-Csv results\facts.csv | Where-Object { $_.missing } | Format-Table tool, file, missing
```
Failed, unsupported or timed-out runs:
```powershell
Import-Csv results\runs.csv | Where-Object { $_.status -ne "ok" } | Format-Table tool, file, status, error
```
Every individual run of one tool on one document (useful to spot outliers):
```powershell
Import-Csv results\runs.csv | Where-Object { $_.file -eq "07_scanned.pdf" -and $_.tool -eq "docling" } | Format-Table repeat, first_s, warm_s, peak_mb
```
Check that the scanned test PDF really has no text layer (should print 0):
```powershell
python -c "import pymupdf; print(len(pymupdf.open('data/07_scanned.pdf')[0].get_text().strip()))"
```
## Adding your own test document
1. Put the file in `data/` (supported: .pdf, .docx, .pptx, .xlsx). Use dummy content only.
2. Add its facts to `data/ground_truth.json`, using the file name without extension as the key, for example `"08_invoice": ["INV-9001", "Acme Ltd"]`.
3. Add rating rows for it in `results/manual_checks.csv`.
4. Repeat steps 6 to 9.
Tip: use unusual, made-up values (such as "QX-7741") as facts, so they cannot appear in an output by accident.
## Regenerating the test documents (optional)
The test documents are already in `data/`. You only need this to rebuild them.
Extra requirements: Node.js, LibreOffice, and the Python packages openpyxl and pillow.
```powershell
npm install docx pptxgenjs
pip install openpyxl pillow
node scripts/make_test_docs/make_docs.js
node scripts/make_test_docs/make_slides.js
python scripts/make_test_docs/make_sheet.py
soffice --headless --convert-to pdf --outdir data data\01_basic.docx data\02_table.docx data\03_two_column.docx data\04_slides.pptx data\06_header_footer.docx data\_scan_source.docx
```
Then open `data\05_sheet.xlsx` once in Excel or LibreOffice and save it, so the Total formula gets a stored value (openpyxl writes formulas without results).
The scanned page is made by turning `data\_scan_source.pdf` into a 150 dpi image (greyscale, rotated 0.6 degrees) and saving it as an image-only PDF:
```powershell
python -c "import pymupdf; pymupdf.open('data/_scan_source.pdf')[0].get_pixmap(dpi=150).save('data/scan.png')"
python -c "from PIL import Image; Image.open('data/scan.png').convert('L').rotate(0.6, expand=True, fillcolor=255).convert('RGB').save('data/07_scanned.pdf', resolution=150)"
```
Delete `data\_scan_source.docx` and `data\_scan_source.pdf` afterwards, and check that no text can be selected in `07_scanned.pdf`.
Note: the original test set's PDFs were exported with LibreOffice, not Microsoft Word, and the original scan was rendered with pdftoppm. Different tools can produce slightly different files.
## Troubleshooting
| Problem | Fix |
|---|---|
| "running scripts is disabled" when activating `.venv` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `git push`: "Password authentication is not supported" | Use the "Sign in with your browser" popup (Git Credential Manager), not your password |
| Docling warnings about "unauthenticated requests to the HF Hub" or "symlinks" | Harmless; models still download and work |
| Docling is very slow | Expected on CPU: about 15 s model loading per new process, plus 4 to 20 s per PDF. Use `--repeats 1` or `--tools` to shorten the run |
| `check_facts.py` shows "?" in the table | That document/tool pair has no rating in `results/manual_checks.csv` yet |
| Markdown files show backslashes (`\#`, `\-`) on GitHub | Notepad "Formatted" mode escaped them. Switch Notepad to "Syntax" mode before editing `.md` files |
| Downloaded files are not in Downloads | Your browser may save to `OneDrive\Documents\Downloads` |
## Licences of the tools
| Tool | Licence | Commercial use |
|---|---|---|
| MarkItDown | MIT | Yes |
| Docling | MIT (code); downloaded models Apache-2.0 / CDLA-Permissive-2.0 | Yes |
| PyMuPDF4LLM | AGPL-3.0 or commercial licence from Artifex | Only if the whole service is published under AGPL; otherwise a paid licence is needed |
Details and verification status: [docs/report.md](docs/report.md), section 1.4.
## Ground rules followed
- Only self-made documents with dummy content; no real documents.
- Every result is reproducible: versions in `requirements.txt` and `results/run_info.json`, settings and scripts in this repository.
- Test documents and benchmark scripts were created with AI assistance (Claude) and reviewed by the author.

Updated numbers (Day 2): see **Headline numbers** at the top of docs/report.md, generated by scripts/make_headline.py.
