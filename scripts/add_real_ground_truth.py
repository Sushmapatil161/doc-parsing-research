"""Day 3, Task 3: hand-written ground-truth facts for the real PDFs, in reading order.

Facts were typed from what is visible on the page, not copied from the PDF text layer.
"""
import json
from pathlib import Path

FACTS = {
    "21_irs_w9_p1": [
        "Rev. March 2024",
        "Request for Taxpayer Identification Number and Certification",
        "Give form to the requester. Do not send to the IRS.",
        "Print or type",
        "Exempt payee code (if any)",
        "Taxpayer Identification Number (TIN)",
    ],
    "23_cdc_mmwr_p1-3": [
        "Weekly / Vol. 74 / No. 14",
        "a total of 800 cases have been",
        "coordinating with health care facilities and schools",
        "93.7 million lives",
        "one in an adult aged 75 years",
        "by preventing complications associated with",
        "Atlanta, GA 30329-4027",
    ],
    "24_cdc_table_p1": [
        "Percentage and number of behavioral health treatment facilities",
        "Offers at least one cessation service",
        "Mental Health Treatment Facilities",
        "64.4 (3,403)",
        "39.2 (148)",
        "80.8 (345)",
    ],
}

p = Path(__file__).resolve().parent.parent / "data" / "ground_truth.json"
truth = json.loads(p.read_text(encoding="utf-8"))
for key, facts in FACTS.items():
    if len(facts) < 5:
        print(f"skipped {key}: only {len(facts)} facts (need 5-6)")
        continue
    truth[key] = facts
    print(f"added {key}: {len(facts)} facts")
p.write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")