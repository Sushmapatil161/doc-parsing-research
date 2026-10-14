=== docling / 02_table.pdf  vs  answer key 02_table.csv  (1 table(s) in output) ===
Score: header 3/4, body 12/12, total 15/16 cells correct (94%)

ANSWER KEY (correct table):

| Region           | Sales (₹) | Q3 2026 - July | Q3 2026 - August |
|------------------|-----------|----------------|------------------|
| Bengaluru Office | 48,213    | 15,400         | 16,050           |
| Mumbai Office    | 39,870    | 12,900         | 13,300           |
| Delhi Office     | 27,645    | 9,100          | 9,200            |

TOOL OUTPUT (same layout, [X] = wrong cell):

| Region           | [X] Sales ( ) ₹ | Q3 2026 - July | Q3 2026 - August |
|------------------|-----------------|----------------|------------------|
| Bengaluru Office | 48,213          | 15,400         | 16,050           |
| Mumbai Office    | 39,870          | 12,900         | 13,300           |
| Delhi Office     | 27,645          | 9,100          | 9,200            |

WRONG CELLS:
  - header, column 2: expected 'Sales (₹)', got 'Sales ( ) ₹'
