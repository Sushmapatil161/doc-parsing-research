"""Write the expected (correct) tables as CSV answer keys in data/expected_tables/.

Every value is checked against the generator script that created the document,
so the answer key comes from the source, not from any tool's output.
Usage: python scripts/make_expected_tables.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "expected_tables"
GEN = ROOT / "scripts" / "make_test_docs"
R = "\u20b9"  # rupee sign

TABLES = {
    "02_table.csv": [
        ["Region", f"Sales ({R})", "Q3 2026 - July", "Q3 2026 - August"],
        ["Bengaluru Office", "48,213", "15,400", "16,050"],
        ["Mumbai Office", "39,870", "12,900", "13,300"],
        ["Delhi Office", "27,645", "9,100", "9,200"],
    ],
    "04_slides.csv": [
        ["Plan", "Price", "Users"],
        ["Basic", f"{R}499", "5"],
        ["Pro", f"{R}1,299", "25"],
        ["Enterprise", f"{R}4,999", "200"],
    ],
    "05_sheet_Invoices.csv": [
        ["Invoice", "Customer", "Amount"],
        ["INV-5582", "Sparrow Traders", "12,400"],
        ["INV-5583", "Lotus Foods", "8,750"],
        ["INV-5584", "Banyan Tech", "15,300"],
        ["Total", "", "36,450"],
    ],
    "05_sheet_Staff.csv": [
        ["Name", "Department"],
        ["Kavya Iyer", "Finance"],
        ["Rahul Bose", "Sales"],
        ["Anita Kulkarni", "HR"],
    ],
}

SOURCE = {
    "02_table.csv": GEN / "make_docs.js",
    "04_slides.csv": GEN / "make_slides.js",
    "05_sheet_Invoices.csv": GEN / "make_sheet.py",
    "05_sheet_Staff.csv": GEN / "make_sheet.py",
}


def check():
    problems = []
    for name, rows in TABLES.items():
        text = SOURCE[name].read_text(encoding="utf-8")
        for row in rows:
            for cell in row:
                if not cell:
                    continue
                if name.startswith("05_sheet"):
                    cell = cell.replace(",", "")  # sheet stores 12400, Excel shows 12,400
                    if cell == "36450":
                        cell = "SUM(C2:C4)"  # total is a formula in the generator
                parts = cell.split(" - ") if name == "02_table.csv" else [cell]
                for part in parts:
                    if part not in text:
                        problems.append(f"{name}: '{part}' not found in {SOURCE[name].name}")
    return problems


def main():
    problems = check()
    if problems:
        print("STOPPED, nothing saved. Check these values:")
        for p in problems:
            print("  ", p)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in TABLES.items():
        with open(OUT / name, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(rows)
        print(f"saved data/expected_tables/{name}  ({len(rows) - 1} body rows x {len(rows[0])} columns)")
    print("All values verified against the generator scripts.")


if __name__ == "__main__":
    main()