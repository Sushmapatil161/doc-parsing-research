\# Document Parsing Research Report



\## 1. Landscape Brief



\### 1.1 Why parsing quality matters for AI systems

(3–5 sentences)



\### 1.2 Digital PDFs vs scanned PDFs

(3–5 sentences + how to tell them apart)



\### 1.3 The main tools

(one short paragraph per tool)



\### 1.4 Licences

(table)



\## 2. Method

\- 13 test documents (7 types), all dummy content, see data/README.md

\- Each tool run with default settings, 3 repeats, each run in a fresh process

\- "First run" includes model loading; "Warm run" is a second conversion in the same process

\- Facts found: automatic check against data/ground\_truth.json (scripts/check\_facts.py)

\- Table and reading order: checked by eye

\- Hardware: see docs/setup.md (CPU only, no GPU)

## 2\. Method

* Test set: 13 files covering 7 document types (basic text, table with merged cells, two-column page, slides, spreadsheet, headers/footers, scanned page). All dummy content; see data/README.md.
* Tools: markitdown 0.1.8, docling 2.138.0, pymupdf4llm 1.28.2, all with default settings.
* Each document was run 3 times per tool, each run in a fresh Python process (scripts/run\_benchmark.py).
* First run = first conversion in a new process, including model loading. Warm run = second conversion in the same process (models already loaded, like a running service).
* Peak RAM = peak working set of the process (psutil).
* Facts found = automatic check against data/ground\_truth.json (scripts/check\_facts.py).
* Table intact / reading order = checked by eye; ratings and reasons in results/manual\_checks.csv.
* Hardware: Intel i5-1135G7 (4 cores / 8 threads), no dedicated GPU; see docs/setup.md.

## 3\. Results

Times are the mean of 3 runs. "unsupported" = the tool cannot read that format.

|Document|Tool|First run (s)|Warm run (s)|Peak RAM (MB)|Facts found|Table intact?|Reading order OK?|
|-|-|-|-|-|-|-|-|
|01\_basic.docx|docling|0.183|0.076|324.033|8/8 (100%)|n/a|Yes|
|01\_basic.docx|markitdown|0.032|0.025|114.933|8/8 (100%)|n/a|Yes|
|01\_basic.docx|pymupdf4llm||||unsupported|n/a|n/a|
|01\_basic.pdf|docling|20.866|4.204|884.133|8/8 (100%)|n/a|Yes|
|01\_basic.pdf|markitdown|0.049|0.043|115.0|8/8 (100%)|n/a|Yes|
|01\_basic.pdf|pymupdf4llm|1.937|0.296|311.5|8/8 (100%)|n/a|Yes|
|02\_table.docx|docling|0.19|0.096|323.7|9/9 (100%)|Partial|Yes|
|02\_table.docx|markitdown|0.063|0.052|115.033|9/9 (100%)|Partial|Yes|
|02\_table.docx|pymupdf4llm||||unsupported|n/a|n/a|
|02\_table.pdf|docling|25.333|6.813|953.833|9/9 (100%)|Yes|Yes|
|02\_table.pdf|markitdown|0.042|0.036|114.9|9/9 (100%)|Partial|Yes|
|02\_table.pdf|pymupdf4llm|1.121|0.285|311.633|9/9 (100%)|Partial|Yes|
|03\_two\_column.docx|docling|0.176|0.074|323.167|9/9 (100%)|n/a|Yes|
|03\_two\_column.docx|markitdown|0.029|0.026|114.967|9/9 (100%)|n/a|Yes|
|03\_two\_column.docx|pymupdf4llm||||unsupported|n/a|n/a|
|03\_two\_column.pdf|docling|20.026|4.248|1009.367|9/9 (100%)|n/a|Yes|
|03\_two\_column.pdf|markitdown|0.071|0.056|115.067|9/9 (100%)|n/a|Partial|
|03\_two\_column.pdf|pymupdf4llm|1.119|0.243|311.267|9/9 (100%)|n/a|Yes|
|04\_slides.pdf|docling|31.497|11.825|1116.7|8/8 (100%)|?|?|
|04\_slides.pdf|markitdown|0.051|0.049|114.867|8/8 (100%)|?|?|
|04\_slides.pdf|pymupdf4llm|1.555|0.971|311.167|8/8 (100%)|?|?|
|04\_slides.pptx|docling|0.181|0.064|325.833|8/8 (100%)|Yes|Yes|
|04\_slides.pptx|markitdown|0.024|0.019|114.867|8/8 (100%)|Yes|Yes|
|04\_slides.pptx|pymupdf4llm||||unsupported|n/a|n/a|
|05\_sheet.xlsx|docling|0.137|0.03|322.967|7/7 (100%)|?|?|
|05\_sheet.xlsx|markitdown|0.036|0.027|114.833|7/7 (100%)|?|?|
|05\_sheet.xlsx|pymupdf4llm||||unsupported|n/a|n/a|
|06\_header\_footer.docx|docling|0.19|0.086|323.333|5/5 (100%)|n/a|Yes|
|06\_header\_footer.docx|markitdown|0.034|0.026|114.967|5/5 (100%)|n/a|Yes|
|06\_header\_footer.docx|pymupdf4llm||||unsupported|n/a|n/a|
|06\_header\_footer.pdf|docling|25.342|19.865|1261.367|5/5 (100%)|n/a|Yes|
|06\_header\_footer.pdf|markitdown|0.073|0.066|115.1|5/5 (100%)|n/a|Yes|
|06\_header\_footer.pdf|pymupdf4llm|1.33|0.488|311.5|5/5 (100%)|n/a|Yes|
|07\_scanned.pdf|docling|114.806|6.082|997.9|6/6 (100%)|n/a|Yes|
|07\_scanned.pdf|markitdown|0.016|0.009|115.1|0/6 (0%)|n/a|n/a|
|07\_scanned.pdf|pymupdf4llm|4.521|3.387|663.3|5/6 (83%)|n/a|Yes|

## 4\. Observations (Day 1)

1. Fact count alone does not separate the tools on digital documents: all three found 100% of facts in every digital file.
2. Structure does separate them. Only Docling (on the PDF) rebuilt the merged table header correctly ("Q3 2026 - July / Q3 2026 - August"). MarkItDown also pulled a sentence below the table into the table. On the two-column PDF, MarkItDown placed the "Delta 9" heading in the wrong position, yet still scored 100% on facts. A fact check misses structural errors.
3. Scanned page: MarkItDown 0/6 (no OCR, returns empty text silently), PyMuPDF4LLM 5/6, Docling 6/6.
4. Cost: on PDFs Docling is about 100x slower than MarkItDown (warm 4.2 s vs 0.043 s on 01\_basic.pdf) and uses about 8x more memory (0.9-1.3 GB vs 115 MB). Each new process also pays about 15 s of model loading.
5. Docling is fast on Word, PowerPoint and Excel files (under 0.2 s), because these formats already contain structure and no AI models are needed.
6. The original Office file is not always the best input: Docling handled the merged table header better from the PDF than from the DOCX, and Docling and PyMuPDF4LLM produced better slide headings from the slides PDF than from the PPTX.
7. Spreadsheets: both tools output the formula result (36450) and dropped thousands separators. MarkItDown keeps sheet names but writes "NaN" for empty cells; Docling loses sheet names.

## 5\. Preliminary recommendation (to be confirmed)

* Office files (DOCX/PPTX/XLSX) and simple digital PDFs where speed matters: MarkItDown (MIT licence, fastest, lightest), but it must never be used alone on scanned documents.
* PDFs with complex tables, multi-column layouts, or scans: Docling (MIT licence), accepting higher time and memory cost.
* PyMuPDF4LLM: good quality and fast on PDFs, but PDF-only and AGPL-3.0 licensed, so it needs a commercial licence or full source disclosure for business use.

## 6\. Limitations and open questions

* Small test set (13 files, 1 page in most files); results may differ on long or real-world documents.
* PDFs were exported with LibreOffice, not Microsoft Word.
* CPU only; Docling would be faster with a GPU.
* Docling's first run on the scanned page (114.8 s) was much slower than warm (6.1 s); possibly one-time OCR model loading. To investigate.
* Docling warm time on 06\_header\_footer.pdf (19.9 s) was unusually close to its first run; possibly an outlier or thermal throttling. To investigate.
* PyMuPDF4LLM read the scan without Tesseract installed; which OCR engine it used still needs to be confirmed.

