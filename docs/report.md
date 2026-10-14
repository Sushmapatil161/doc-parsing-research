# Document Parsing Research Report



## 1. Landscape Brief
### 1.1 Why parsing quality matters for AI systems
AI systems that answer questions from documents (for example, a chatbot over company files) never see the original file. They only see the text a parser extracts from it. If a table comes out scrambled, numbers end up in the wrong rows and the AI quotes the wrong value. If a two-column page is read line by line across both columns, sentences from unrelated topics get mixed together. If a scanned page produces no text, the AI simply says the information does not exist. These errors are silent: the AI still answers confidently, so nobody notices that the problem happened earlier, at the parsing step. Parser quality therefore sets an upper limit on the quality of the whole AI system.
### 1.2 Digital PDFs vs scanned PDFs
A digital PDF (for example, exported from Word) stores the actual text characters together with their positions on the page, so a tool can read the text directly. A scanned PDF stores only a picture of the page; it contains no text at all. To get text out of a scan, a tool needs OCR (Optical Character Recognition), which recognises letters in the image. OCR is slower and can make mistakes, such as reading "0" as "O" or dropping commas in numbers. Quick test: open the PDF and try to select text with the mouse. If nothing can be selected, it is a scan.
### 1.3 The main tools
- MarkItDown (Microsoft): converts many formats (PDF, Word, PowerPoint, Excel, HTML and more) to Markdown. Very fast and lightweight, but has no built-in OCR and uses simple text extraction for PDFs, so complex layouts and scans are weak points.
- Docling (originally IBM Research, now hosted by the LF AI & Data Foundation): uses AI models for page layout and table structure, keeps reading order, and includes OCR for scans. Handles PDF, Office files, HTML and images. Much better on complex PDFs, but slower and needs more memory, especially without a GPU.
- PyMuPDF4LLM (Artifex): converts PDFs to Markdown using the PyMuPDF library. Fast, good at headings, tables and multi-column pages, but reads PDFs only (Office formats need the paid PyMuPDF Pro).
- Unstructured: splits documents of many formats into typed elements (titles, paragraphs, tables), aimed at AI data pipelines. Not tested yet in this research.
- OCR tools for scans: Tesseract (classic open-source OCR engine), EasyOCR and RapidOCR (deep-learning OCR). Docling and PyMuPDF4LLM can call OCR engines like these; MarkItDown cannot on its own.
### 1.4 Licences
| Tool | Licence | Commercial use allowed? | Verified |
|---|---|---|---|
| MarkItDown | MIT | Yes | to check on GitHub LICENSE file |
| Docling | MIT (code); downloaded models Apache-2.0 / CDLA-Permissive-2.0 | Yes | Yes (GitHub README, model notices) |
| PyMuPDF4LLM | AGPL-3.0 or commercial licence from Artifex | Only if the whole service is released as open source under AGPL, otherwise a paid commercial licence is needed | Yes (PyPI / project pages) |
| Unstructured | Apache-2.0 | Yes | to check on GitHub LICENSE file |
| Tesseract | Apache-2.0 | Yes | to check on GitHub LICENSE file |
| EasyOCR / RapidOCR | Apache-2.0 | Yes | to check on GitHub LICENSE file |
Key point: AGPL also applies when software is offered as a network service (for example, a parsing API), not only when it is distributed. This makes PyMuPDF4LLM a licensing risk for business use without a commercial licence.
## 2. Method

* Test set: 13 files covering 7 document types (basic text, table with merged cells, two-column page, slides, spreadsheet, headers/footers, scanned page). All dummy content; see data/README.md.
* Tools: markitdown 0.1.8, docling 2.138.0, pymupdf4llm 1.28.2, all with default settings.
* Each document was run 3 times per tool, each run in a fresh Python process (scripts/run_benchmark.py).
* First run = first conversion in a new process, including model loading. Warm run = second conversion in the same process (models already loaded, like a running service).
* Evidence tags: **[measured]** = seen in our own test runs (source file named); **[read]** = taken from documentation or licence pages, not tested by us. Section 1 (landscape and licences) is [read] unless marked otherwise.
* Peak RAM = peak working set of the process (psutil).
* Facts found = automatic check against data/ground_truth.json (scripts/check_facts.py).
* Table intact / reading order = checked by eye; ratings and reasons in results/manual_checks.csv.
* Hardware: Intel i5-1135G7 (4 cores / 8 threads), 8 GB RAM (7.8 GB usable), no dedicated GPU; Windows 11 Home Single Language 23H2 (build 22631); see docs/setup.md.
* Coverage [measured, results/summary.csv]: data/ has 13 files, but scan.png is only the source image used to create 07_scanned.pdf, so the benchmark ran on 12 documents: 12 documents x 3 tools = 36 rows. Of these, 30 are real results. PyMuPDF4LLM opens only PDFs, so its 6 rows for .docx, .pptx and .xlsx files have status `unsupported` (0 successful runs). Docling and MarkItDown succeeded on all 12 documents.

## 3. Results

Times are the mean of 3 runs. "unsupported" = the tool cannot read that format.

|Document|Tool|First run (s)|Warm run (s)|Peak RAM (MB)|Facts found|Table intact?|Reading order OK?|
|-|-|-|-|-|-|-|-|
|01_basic.docx|docling|0.183|0.076|324.033|8/8 (100%)|n/a|Yes|
|01_basic.docx|markitdown|0.032|0.025|114.933|8/8 (100%)|n/a|Yes|
|01_basic.docx|pymupdf4llm||||unsupported|n/a|n/a|
|01_basic.pdf|docling|20.866|4.204|884.133|8/8 (100%)|n/a|Yes|
|01_basic.pdf|markitdown|0.049|0.043|115.0|8/8 (100%)|n/a|Yes|
|01_basic.pdf|pymupdf4llm|1.937|0.296|311.5|8/8 (100%)|n/a|Yes|
|02_table.docx|docling|0.19|0.096|323.7|9/9 (100%)|Partial|Yes|
|02_table.docx|markitdown|0.063|0.052|115.033|9/9 (100%)|Partial|Yes|
|02_table.docx|pymupdf4llm||||unsupported|n/a|n/a|
|02_table.pdf|docling|25.333|6.813|953.833|9/9 (100%)|Yes|Yes|
|02_table.pdf|markitdown|0.042|0.036|114.9|9/9 (100%)|Partial|Yes|
|02_table.pdf|pymupdf4llm|1.121|0.285|311.633|9/9 (100%)|Partial|Yes|
|03_two_column.docx|docling|0.176|0.074|323.167|9/9 (100%)|n/a|Yes|
|03_two_column.docx|markitdown|0.029|0.026|114.967|9/9 (100%)|n/a|Yes|
|03_two_column.docx|pymupdf4llm||||unsupported|n/a|n/a|
|03_two_column.pdf|docling|20.026|4.248|1009.367|9/9 (100%)|n/a|Yes|
|03_two_column.pdf|markitdown|0.071|0.056|115.067|9/9 (100%)|n/a|Partial|
|03_two_column.pdf|pymupdf4llm|1.119|0.243|311.267|9/9 (100%)|n/a|Yes|
|04_slides.pdf|docling|31.497|11.825|1116.7|8/8 (100%)|?|?|
|04_slides.pdf|markitdown|0.051|0.049|114.867|8/8 (100%)|?|?|
|04_slides.pdf|pymupdf4llm|1.555|0.971|311.167|8/8 (100%)|?|?|
|04_slides.pptx|docling|0.181|0.064|325.833|8/8 (100%)|Yes|Yes|
|04_slides.pptx|markitdown|0.024|0.019|114.867|8/8 (100%)|Yes|Yes|
|04_slides.pptx|pymupdf4llm||||unsupported|n/a|n/a|
|05_sheet.xlsx|docling|0.137|0.03|322.967|7/7 (100%)|?|?|
|05_sheet.xlsx|markitdown|0.036|0.027|114.833|7/7 (100%)|?|?|
|05_sheet.xlsx|pymupdf4llm||||unsupported|n/a|n/a|
|06_header_footer.docx|docling|0.19|0.086|323.333|5/5 (100%)|n/a|Yes|
|06_header_footer.docx|markitdown|0.034|0.026|114.967|5/5 (100%)|n/a|Yes|
|06_header_footer.docx|pymupdf4llm||||unsupported|n/a|n/a|
|06_header_footer.pdf|docling|25.342|19.865|1261.367|5/5 (100%)|n/a|Yes|
|06_header_footer.pdf|markitdown|0.073|0.066|115.1|5/5 (100%)|n/a|Yes|
|06_header_footer.pdf|pymupdf4llm|1.33|0.488|311.5|5/5 (100%)|n/a|Yes|
|07_scanned.pdf|docling|114.806|6.082|997.9|6/6 (100%)|n/a|Yes|
|07_scanned.pdf|markitdown|0.016|0.009|115.1|0/6 (0%)|n/a|n/a|
|07_scanned.pdf|pymupdf4llm|4.521|3.387|663.3|5/6 (83%)|n/a|Yes|

## 4. Observations (Day 1)

1. Fact count alone does not separate the tools on digital documents: all three found 100% of facts in every digital file they could open. [measured, results/facts.csv]
2. Structure does separate them. Only Docling (on the PDF) rebuilt the merged table header correctly ("Q3 2026 - July / Q3 2026 - August"). MarkItDown also pulled a sentence below the table into the table. On the two-column PDF, MarkItDown placed the "Delta 9" heading in the wrong position, yet still scored 100% on facts. A fact check misses structural errors. [measured, checked by eye, results/manual_checks.csv]
3. Scanned page: MarkItDown 0/6 (returned empty text with no error), PyMuPDF4LLM 5/6, Docling 6/6. [measured, results/facts.csv] MarkItDown has no built-in OCR. [read, MarkItDown docs]
4. Cost: on PDFs Docling is about 100x slower than MarkItDown (warm 4.2 s vs 0.043 s on 01_basic.pdf) and uses about 8x more memory (0.9-1.3 GB vs 115 MB). Each new process also pays about 15 s of model loading (estimated as first run minus warm run, not timed separately yet). [measured, results/summary.csv]
5. Docling is fast on Word, PowerPoint and Excel files (under 0.2 s), because these formats already contain structure and no AI models are needed. [time measured, results/summary.csv; reason read from Docling docs]
6. The original Office file is not always the best input: Docling handled the merged table header better from the PDF than from the DOCX, and Docling produced better slide headings from the slides PDF than from the PPTX (PyMuPDF4LLM cannot open PPTX, so for slides it was only tested on the PDF). [measured, checked by eye]
7. Spreadsheets: both tools output the formula result (36450) and dropped thousands separators. MarkItDown keeps sheet names but writes "NaN" for empty cells; Docling loses sheet names. [measured, outputs in results/markitdown and results/docling]

## 5. Preliminary recommendation (to be confirmed)

* Office files (DOCX/PPTX/XLSX) and simple digital PDFs where speed matters: MarkItDown (MIT licence, fastest, lightest), but it must never be used alone on scanned documents. [speed and scan failure measured; licence read]
* PDFs with complex tables, multi-column layouts, or scans: Docling (MIT licence), accepting higher time and memory cost. [quality, time and memory measured; licence read]
* PyMuPDF4LLM: good quality and fast on PDFs, but PDF-only and AGPL-3.0 licensed, so it needs a commercial licence or full source disclosure for business use. [quality, speed and PDF-only measured; licence read]

## 6. Limitations and open questions

* Small test set (12 documents, plus scan.png as the source image; 1 page in most files); results may differ on long or real-world documents.
* PDFs were exported with LibreOffice, not Microsoft Word.
* CPU only; Docling would probably be faster with a GPU. [read, not tested]
* Docling's first run on the scanned page (114.8 s) was much slower than warm (6.1 s); possibly one-time OCR model loading. To investigate.
* Docling warm time on 06_header_footer.pdf (19.9 s) was unusually close to its first run; possibly an outlier or thermal throttling. To investigate.
* PyMuPDF4LLM read the scan without Tesseract installed; which OCR engine it used still needs to be confirmed. [score measured; engine unknown]



