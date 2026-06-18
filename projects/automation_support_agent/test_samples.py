"""
Day 14 — Test the full pipeline against realistic sample files.
Reads each sample file and runs it through process_ticket().
"""

import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import process_ticket

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")

SAMPLE_FILES = [
    "disk_issue.txt",
    "upgrade_failure.log",
    "package_install.log",
    "citrix_issue.log",
]


def load_sample(filename: str) -> str:
    """Read a sample file and return its content as a string."""
    path = os.path.join(SAMPLE_DIR, filename)
    with open(path, "r") as f:
        return f.read().strip()


if __name__ == "__main__":

    print("\n" + "="*60)
    print("DAY 14 — REALISTIC SAMPLE CASE TESTING")
    print("="*60)

    results = []

    for filename in SAMPLE_FILES:
        content = load_sample(filename)

        # For multi-line files, use full content as the "ticket"
        # The classifier needs to handle realistic, messy, multi-line input
        print(f"\n{'#'*60}")
        print(f"# FILE: {filename}")
        print(f"{'#'*60}")
        print(f"Content preview: {content[:100]}...")

        result = process_ticket(content)
        results.append({"file": filename, "result": result})

        time.sleep(2)

    print("\n" + "="*60)
    print("DAY 14 SUMMARY — ALL SAMPLE FILES")
    print("="*60)

    for r in results:
        cat  = r["result"]["classification"]["category"]
        conf = r["result"]["classification"]["confidence"]
        sev  = r["result"]["report"].get("severity", "N/A")
        appr = r["result"]["report"].get("approval_required", "N/A")
        print(f"\n{r['file']}")
        print(f"  Category : {cat} ({conf})")
        print(f"  Severity : {sev}")
        print(f"  Approval : {appr}")
        print(f"  Summary  : {r['result']['report'].get('summary', 'N/A')}")