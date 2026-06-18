# Day 14 — Create Realistic Sample Cases

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Build a library of realistic sample inputs based on your
> 20 years of IT experience. These make the project credible in interviews.

---

## Study Resources

- Writing good test cases — Google Testing Blog:
  https://testing.googleblog.com/

---

## Core Concepts

| Concept | Definition |
|---|---|
| Sanitised real data | Use patterns from real incidents — remove all personal/company-specific details |
| Diverse samples | Cover all 5 categories, varying severity, edge cases |
| Why it matters | Good sample data separates a portfolio project from a toy demo |
| Interview readiness | Interviewers test with unexpected inputs — prepare for that today |

---

## Why This Day Matters for Your Portfolio

```
Day 10-13   →  Built the pipeline with SIMPLE one-line tickets
                "My MacBook disk is almost full"

Day 14      →  Test with REALISTIC multi-line tickets/logs
                — the kind that actually arrive at Oracle EE
```

A simple one-liner proves the pipeline *works*.
A realistic multi-paragraph ticket with timestamps, error codes,
and context proves the pipeline is *production-grade*.
Interviewers will ask: "what does real input look like?" —
today you build the answer.

---

## Step-by-Step Instructions

### Step 1 — Create 4 Sample Files in sample_data/

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
code projects/automation_support_agent/sample_data/disk_issue.txt
code projects/automation_support_agent/sample_data/upgrade_failure.log
code projects/automation_support_agent/sample_data/package_install.log
code projects/automation_support_agent/sample_data/citrix_issue.log
```

---

### File 1 — disk_issue.txt

```
User reports: MacBook Pro 16-inch (2021, M1 Max) running macOS 14.2.1

Error: "Your disk is almost full" notification appeared during Zoom call.
Cannot save files. Applications running slowly.

Last cleanup was 6 months ago. No recent large downloads known.

Additional context from user:
- Issue started 2 days ago
- Outlook keeps showing "cannot save attachment" error
- Time Machine backup failed last night with "not enough free space"
- User has not restarted machine in 3 weeks
```

---

### File 2 — upgrade_failure.log

```
2024-01-15 08:00:01 INFO  Starting macOS 14.4 upgrade
2024-01-15 08:00:15 INFO  Checking system requirements...
2024-01-15 08:00:18 INFO  Requirements check passed
2024-01-15 08:00:20 INFO  Beginning download (3.8 GB)
2024-01-15 08:45:32 INFO  Download complete (12.4 GB cached + delta)
2024-01-15 08:45:35 INFO  Verifying package integrity...
2024-01-15 08:45:40 INFO  Package verified
2024-01-15 08:46:00 INFO  Preparing installation...
2024-01-15 09:12:18 ERROR Preparation failed: not enough space on Macintosh HD
2024-01-15 09:12:19 ERROR Required: 35 GB, Available: 22 GB
2024-01-15 09:12:20 WARN  Upgrade cancelled. System restored.
2024-01-15 09:12:45 INFO  Rollback complete — system at macOS 14.2.1
2024-01-15 09:13:00 INFO  Recommend: free at least 15 GB before retry
```

---

### File 3 — package_install.log

```
2024-01-15 09:23:00 INFO  Starting CompanyVPN package installation
2024-01-15 09:23:01 INFO  Package: CompanyVPN-2.1.0.pkg
2024-01-15 09:23:02 INFO  Source: /Volumes/IT_Tools/CompanyVPN-2.1.0.pkg
2024-01-15 09:23:03 INFO  Verifying package signature...
2024-01-15 09:23:05 ERROR Gatekeeper: package not notarized
2024-01-15 09:23:05 ERROR Code: ERR_NOTARIZATION_FAILED
2024-01-15 09:23:06 ERROR Apple notarization service returned: rejected
2024-01-15 09:23:06 WARN  Installation aborted
2024-01-15 09:23:07 INFO  Suggested action: contact IT admin to re-sign
                          package with valid Developer ID certificate
2024-01-15 09:23:08 INFO  Reference ticket: re-notarization request
                          must go through Apple Developer Program
```

---

### File 4 — citrix_issue.log

```
2024-01-15 10:15:00 INFO  Citrix Workspace 23.9.0 starting...
2024-01-15 10:15:01 INFO  Loading user profile: jsmith@oracle.com
2024-01-15 10:15:02 INFO  Connecting to StoreFront: storefront.oracle.com
2024-01-15 10:15:04 INFO  Authentication successful
2024-01-15 10:15:05 INFO  Fetching published applications...
2024-01-15 10:15:08 ERROR Application launch failed: ICA file corrupted
2024-01-15 10:15:08 ERROR Exit code: -1073741819 (0xC0000005)
2024-01-15 10:15:09 WARN  Crash signature: EXC_BAD_ACCESS
2024-01-15 10:15:10 INFO  Citrix Workspace closed unexpectedly
2024-01-15 10:15:11 INFO  Crash log saved: ~/Library/Logs/CrashReporter/
                          CitrixWorkspace_2024-01-15-101510.ips

Additional context from user:
- Worked fine yesterday
- No Citrix or macOS update since last working session
- Other users on same network report same issue
- Restarting Mac did not resolve
```

---

### Step 2 — Run the Full Pipeline Against Each Sample File

Add this test block. Create a new file:

```bash
touch projects/automation_support_agent/test_samples.py
code projects/automation_support_agent/test_samples.py
```

```python
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
```

---

### Step 3 — Note Failures or Weak Outputs

After running, note any issues here — these become Day 17 eval cases.

```bash
code notes/day14-sample-test.md
```

Template:

```markdown
# Day 14 — Sample Test Results

## disk_issue.txt
- Expected category: DISK
- Actual category: ___
- Notes: ___

## upgrade_failure.log
- Expected category: UPGRADE
- Actual category: ___
- Notes: ___

## package_install.log
- Expected category: PACKAGING
- Actual category: ___
- Notes: ___

## citrix_issue.log
- Expected category: APPLICATION
- Actual category: ___
- Notes: ___

## Issues Found
1. ___
2. ___

## What to add to Day 17 eval cases
1. ___
2. ___
```

---

### Step 4 — Create 5 More Edge-Case Tickets

These test robustness — vague, multi-issue, non-English, etc.

```bash
code projects/automation_support_agent/sample_data/edge_cases.md
```

```markdown
# Edge Case Tickets — Day 14

## Edge Case 1 — Multi-issue ticket
"My laptop disk is full AND Citrix keeps crashing AND the VPN
won't connect. Everything started after the macOS update yesterday."

Expected: Agent should pick the MOST LIKELY primary category
(probably UPGRADE since "started after macOS update" is the
common thread), with confidence reflecting the complexity.

## Edge Case 2 — Non-English ticket (Hindi + English mix)
"Mera mac bahut slow ho gaya hai, disk space bhi kam hai aur
Citrix open nahi ho raha"

Expected: Model should still extract "disk space" and "Citrix"
keywords and classify reasonably — tests multilingual handling.

## Edge Case 3 — Extremely short ticket
"Help"

Expected: UNKNOWN, very low confidence, route to human review.

## Edge Case 4 — Ticket with only an error code, no context
"Getting -36 error on file copy"

Expected: UNKNOWN or DISK (macOS -36 is often disk-related),
low-medium confidence — tests if model knows macOS error codes.

## Edge Case 5 — Ticket describing a RESOLVED issue (past tense)
"Yesterday my disk was full but I already cleared 30GB and
it's fine now. Just wanted to report what happened."

Expected: Agent should recognise this is informational, not
actionable — ideally low approval_required, recommendation
should NOT suggest clearing cache again.
```

---

## Terminal Commands — Run in Order

```bash
# Step 1 — create 4 sample files
code projects/automation_support_agent/sample_data/disk_issue.txt
code projects/automation_support_agent/sample_data/upgrade_failure.log
code projects/automation_support_agent/sample_data/package_install.log
code projects/automation_support_agent/sample_data/citrix_issue.log

# Step 2 — create and run test_samples.py
touch projects/automation_support_agent/test_samples.py
code projects/automation_support_agent/test_samples.py
python3 projects/automation_support_agent/test_samples.py

# Step 3 — document results
code notes/day14-sample-test.md

# Step 4 — edge cases
code projects/automation_support_agent/sample_data/edge_cases.md

# Commit
git add .
git commit -m "Day 14: realistic sample cases added"
git push
```

---

## Expected Output

```
============================================================
DAY 14 — REALISTIC SAMPLE CASE TESTING
============================================================

############################################################
# FILE: disk_issue.txt
############################################################
Content preview: User reports: MacBook Pro 16-inch (2021, M1 Max)
running macOS 14.2.1...

────────────────────────────────────────────────────────────
PROCESSING TICKET
────────────────────────────────────────────────────────────
...
Classification:
  Category   : DISK
  Confidence : 0.97
  Reason     : Multiple disk-related symptoms — full disk notification,
                Time Machine failure due to space, save errors

Routing: DISK → check_disk_space() [SAFE]
...
Structured Report:
{
  "issue_category": "DISK",
  "severity": "HIGH",
  "findings": "User reports disk almost full with Time Machine backup
                failure and save errors across multiple apps...",
  ...
}

############################################################
# FILE: upgrade_failure.log
############################################################
...
Classification:
  Category   : UPGRADE
  Confidence : 0.99
  Reason     : Log clearly shows upgrade preparation failed due to
                insufficient disk space

============================================================
DAY 14 SUMMARY — ALL SAMPLE FILES
============================================================

disk_issue.txt
  Category : DISK (0.97)
  Severity : HIGH
  Approval : True
  Summary  : Disk 95% full causing Time Machine and save failures —
              cleanup needed with approval.

upgrade_failure.log
  Category : UPGRADE (0.99)
  Severity : HIGH
  Approval : True
  Summary  : macOS 14.4 upgrade failed due to insufficient space —
              free 15GB and retry.

package_install.log
  Category : PACKAGING (0.95)
  Severity : MEDIUM
  Approval : True
  Summary  : CompanyVPN install blocked by notarization failure —
              IT must re-sign package.

citrix_issue.log
  Category : APPLICATION (0.92)
  Severity : HIGH
  Approval : False
  Summary  : Citrix Workspace crashing with corrupted ICA file —
              affects multiple users.
```

---

## Why Multi-Line Input Is Harder Than Day 10's One-Liners

| Day 10 input | Day 14 input |
|---|---|
| "My Mac says disk is almost full" | 8-line log with timestamps, error codes, multiple symptoms |
| Single signal | Multiple signals — some conflicting |
| Easy to classify | Model must weigh evidence and pick primary issue |
| ~20 tokens | ~150-300 tokens |

If your classifier handles these 4 realistic files correctly, it
proves the prompt from Day 3 and Day 10 generalises beyond toy examples
— this is exactly what an interviewer means by "production-ready."

---

## What "Sanitised Real Data" Means — Your Responsibility

These 4 sample files use **patterns** from real Oracle EE incidents —
generic error codes (`ERR_NOTARIZATION_FAILED`), realistic log formats,
typical hardware (MacBook Pro M1 Max), typical software (Citrix,
CompanyVPN) — but contain:

- NO real employee names (jsmith@oracle.com is a placeholder)
- NO real internal hostnames or IP addresses
- NO real ticket numbers from actual Oracle systems
- NO proprietary internal tool names beyond generic "CompanyVPN"

When you talk about this in interviews: "I based these on patterns
I've seen over 20 years, but everything is genericised — no real
company data."

---

## Interview Questions — Day 14

### Q1 — Why does realistic sample data matter for a portfolio project?

A one-line ticket like "disk is full" proves the happy path works but
tells an interviewer nothing about robustness. Real support tickets
are messy — multi-paragraph descriptions, log excerpts with timestamps
and error codes, sometimes multiple symptoms mixed together, sometimes
written in a hurry with typos. My Day 14 sample files are based on
patterns from 20 years of Oracle EE tickets — an 8-line upgrade failure
log with specific error codes, a Citrix crash log with exit codes and
crash signatures, a disk issue described across multiple paragraphs with
secondary symptoms like Time Machine failures. When my classifier
correctly identifies UPGRADE from a log with no explicit mention of the
word "upgrade" in the first line — it proves the prompt generalises.
That is the difference between a toy demo and something I would be
comfortable explaining to a hiring manager as "production-tested."

### Q2 — How did you sanitise real Oracle incident data for this project?

I did not copy any real ticket text, hostnames, employee names, or
internal tool names. Instead I extracted the *patterns* — the structure
of how a macOS upgrade failure log looks, the typical error codes for
notarization failures, the kind of secondary symptoms a user mentions
when their disk is full (Time Machine failures, save errors in Outlook).
I rebuilt these patterns from scratch using generic placeholders —
"CompanyVPN" instead of the real internal VPN client name, generic
email formats, fictional but realistic timestamps. The result is data
that exercises the same classification challenges as real tickets —
multiple symptoms, technical jargon, error codes — without exposing any
information specific to Oracle's actual environment or any real person.

### Q3 — What edge cases did your agent struggle with and how did you
address them?

[Personalise this after running Step 4 edge cases — template below]

I tested five edge cases beyond the four main samples. The multi-issue
ticket — disk full AND Citrix crashing AND VPN down, all starting after
an OS update — is the hardest, because real incidents often have a
root cause that manifests as multiple symptoms. My classifier [describe
what it actually returned]. The short ticket "Help" correctly returned
UNKNOWN with low confidence — exactly the human-review path I built on
Day 12. [Add your actual findings for the error-code-only ticket and
the past-tense resolved-issue ticket]. Where the agent struggled, I
documented these as candidates for Day 16 prompt hardening — for
example, [your specific finding] suggests the prompt needs an explicit
instruction for handling already-resolved issues differently from
active issues.

---

## What Gets Carried Forward to Day 17

Everything documented in `notes/day14-sample-test.md` and
`sample_data/edge_cases.md` becomes raw material for your 15 eval
cases on Day 17. You are not starting from zero on Day 17 — you are
formalising what you discovered today.

---

## Expected Outputs by End of Day 14

- [ ] Step 1: 4 sample data files created with realistic content
- [ ] Step 2: test_samples.py created and run against all 4 files
- [ ] Step 3: notes/day14-sample-test.md — results and failures noted
- [ ] Step 4: 5 edge case tickets documented in edge_cases.md
- [ ] Committed and pushed

---

## Git Commit

```bash
git add .
git commit -m "Day 14: realistic sample cases added"
git push
```

---

*Day 14 complete — your agent has been tested against realistic,
multi-line, Oracle-EE-style support tickets, not just one-liners.
Day 15 adds the approval gate — the safety mechanism that makes
this agent enterprise-deployable.*
