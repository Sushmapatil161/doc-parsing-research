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

