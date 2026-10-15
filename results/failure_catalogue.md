| # | Tool | Document | Type | Severity | Expected | Got | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | markitdown | 07_scanned.pdf, 14_scan_tilted.pdf, 15_scan_lowres.pdf | empty_output | high | 6 facts | 0 facts, no OCR for PDFs, no warning | [measured] results/facts.csv |
| 2 | pymupdf4llm | 07_scanned.pdf (use_ocr=False) | empty_output | high | 6 facts | 0 characters, no warning | [measured] results/noocr_facts.csv |
| 3 | pymupdf4llm | any scan, no OCR engine installed | empty_output | high | OCR text | OCR skipped silently | [read] select_ocr_function() returns None |
| 4 | pymupdf4llm | 07_scanned.pdf | ocr_error | low | Annual Summary 2026 | AnnualSummary 2026 | [measured] results/facts.csv |
| 5 | docling (RapidOCR, EasyOCR, full-page OCR) | sweep tilt_12.pdf, tilt_20.pdf | empty_output | high | 6 facts | <!-- image --> only (0/6), no warning | [measured] results/sweep.csv |
| 6 | docling (RapidOCR, EasyOCR, full-page OCR) | sweep dpi_036.pdf | empty_output | high | 6 facts | <!-- image --> only (0/6), no warning | [measured] results/sweep.csv |
| 7 | docling + EasyOCR | sweep tilt_08.pdf, dpi_050.pdf | ocr_error | medium | 6 facts | 3/6 and 2/6 facts | [measured] results/sweep.csv |
| 8 | markitdown | 02_table.docx | broken_table | medium | 4 header cells | 0/4 header cells correct (merged header cells) | [measured] results/table_scores.csv |
| 9 | pymupdf4llm | 02_table.pdf | broken_table | medium | 4 header cells | 1/4 header cells correct | [measured] results/table_scores.csv |
| 10 | markitdown | 03_two_column.pdf | wrong_order | medium | heading before its column text | heading placed in the wrong position (Day 2) | [measured] results/reading_order.csv |
| 11 | markitdown | 21_irs_w9_p1.pdf | dropped_text | medium | Print or type | missing (rotated margin text) | [measured] results/facts.csv |
| 12 | pymupdf4llm | 21_irs_w9_p1.pdf | broken_table | high | Social security number | Social se\|curity number (form turned into a fake table, words cut at cell borders) | [measured] 2/6 facts; [read] results/pymupdf4llm/21_irs_w9_p1.pdf.md |
| 13 | pymupdf4llm | 21_irs_w9_p1.pdf | dropped_text | high | Give form to the requester. Do not send to the IRS. | 'send to the IRS.' missing; 'Print or type' -> 'rint or typ' | [read] results/pymupdf4llm/21_irs_w9_p1.pdf.md |
| 14 | docling | 21_irs_w9_p1.pdf | wrong_order | low | Exempt payee code before Part I heading | out of order (form columns, order debatable) | [measured] results/reading_order.csv |

| Tool | Failures | of which high severity |
|---|---|---|
| docling | 4 | 2 |
| markitdown | 4 | 1 |
| pymupdf4llm | 6 | 4 |

| Failure type | Count |
|---|---|
| empty_output | 5 |
| broken_table | 3 |
| ocr_error | 2 |
| wrong_order | 2 |
| dropped_text | 2 |
