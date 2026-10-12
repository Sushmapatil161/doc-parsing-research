# Test set

All content is dummy data invented for this research.

| File | Tests |
|---|---|
| 01_basic (.docx/.pdf) | Headings, bullet list, numbered list |
| 02_table (.docx/.pdf) | Table with merged cells (horizontal "Q3 2026" span + vertical row spans) |
| 03_two_column (.docx/.pdf) | Two-column layout: reading order (Orion Labs left, Delta 9 right) |
| 04_slides (.pptx/.pdf) | 4 slides: title, bullets, table |
| 05_sheet.xlsx | 2 sheets (Invoices, Staff), SUM formula, number formatting |
| 06_header_footer (.docx/.pdf) | 3 pages with header, footer, "Page X of Y" |
| 07_scanned.pdf | Image-only page (150 dpi, slightly rotated, greyscale), no text layer |
| scan.png | Source image for 07_scanned.pdf |
| ground_truth.json | Facts that must appear in each tool's output |

Generated with the scripts in `scripts/make_test_docs/` (docx and pptxgenjs for Node, openpyxl for Python).
PDFs were exported with LibreOffice, not Microsoft Word.
The scanned PDF was made by rendering a page to PNG at 150 dpi (pdftoppm), rotating it 0.6° and saving it as an image-only PDF (Pillow).
