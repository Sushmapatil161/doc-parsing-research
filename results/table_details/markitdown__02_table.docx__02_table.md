=== markitdown / 02_table.docx  vs  answer key 02_table.csv  (1 table(s) in output) ===
Score: header 0/4, body 12/12, total 12/16 cells correct (75%)

ANSWER KEY (correct table):

| Region           | Sales (₹) | Q3 2026 - July | Q3 2026 - August |
|------------------|-----------|----------------|------------------|
| Bengaluru Office | 48,213    | 15,400         | 16,050           |
| Mumbai Office    | 39,870    | 12,900         | 13,300           |
| Delhi Office     | 27,645    | 9,100          | 9,200            |

TOOL OUTPUT (same layout, [X] = wrong cell):

| [X] (empty)      | [X] (empty) | [X] (empty) | [X] (empty) |
|------------------|-------------|-------------|-------------|
| Bengaluru Office | 48,213      | 15,400      | 16,050      |
| Mumbai Office    | 39,870      | 12,900      | 13,300      |
| Delhi Office     | 27,645      | 9,100       | 9,200       |

WRONG CELLS:
  - header, column 1: expected 'Region', got ''
  - header, column 2: expected 'Sales (₹)', got ''
  - header, column 3: expected 'Q3 2026 - July', got ''
  - header, column 4: expected 'Q3 2026 - August', got ''

EXTRA ROWS in the tool's table (not in the original table):
  - Region | Sales (₹) | Q3 2026 | 
  - July | August
