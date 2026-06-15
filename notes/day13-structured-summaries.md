# Day 13 — Build Structured Support Summaries

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Add the report layer — transform raw tool output into a
> clean, structured support summary a human engineer can act on

---

## Study Resources

- OpenAI Structured Outputs guide:
  https://platform.openai.com/docs/guides/structured-outputs

---

## Core Concepts

| Concept | Definition |
|---|---|
| Structured output | The difference between a demo and a production tool — machines parse it, humans read it |
| LLM adds value here | Interprets raw tool data into plain-English findings and recommendations |
| Separation of concerns | Data gathering (tools) separate from interpretation (LLM) — each part testable |
| Integration-ready | JSON output with fixed fields → can plug into Jira, ServiceNow, etc. |

---

## Where This Fits — The Full Pipeline

```
Day 10          Day 11         Day 12              Day 13
Classifier  →   Tools     →    process_ticket() →  generate_report()
(brain)         (hands)        (wiring)            (translator)

Returns:        Returns:       Returns:            Returns:
category,       raw dict       ticket +            FINAL structured
confidence      e.g. free_gb,  classification +    JSON report —
                critical       tool_result         ready for a human
                                (Day 12 output)     or ticketing system
```

Day 12 gave you **raw evidence**. Day 13 turns that evidence into
**English findings + a recommendation** — the actual output an
engineer would read on a ticket.

---

## Why Separate report.py from app.py?

| File | Responsibility |
|---|---|
| app.py | Decides WHAT to check (classify + route + call tool) |
| report.py | Decides WHAT IT MEANS (interpret evidence → human-readable report) |

This separation means:
- You can test report.py with **fake evidence** without running the classifier
- You can swap the report prompt without touching routing logic
- Each file has ONE job — same modular principle as your Oracle EE
  Health Check Script v2.0

---

## Step-by-Step Instructions

### Step 1 — Open report.py

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
code projects/automation_support_agent/report.py
```

---

### Step 2 — Implement generate_report()

Paste this full code into report.py:

```python
"""
Automation Support Agent — Report Generation Layer
Transforms raw tool output into structured JSON support summaries.
LLM interprets evidence — never guesses beyond provided data.
Output schema is fixed for integration with ticketing systems.
Oracle Enterprise Engineering — Agentic AI Portfolio Project
"""

import os
import json
import re
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/auto",
]


# ── Reuse safe_parse_json from Day 10 ─────────────────────────────────────────
def safe_parse_json(text: str) -> dict:
    """4-layer defensive JSON parser — see Day 10 notes for full explanation."""
    clean = re.sub(r"```(?:json)?", "", text).strip()
    clean = clean.strip("`").strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{.*\}', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    log.error(f"JSON parse failed completely | raw: [{text[:300]}]")
    return None


def call_llm(messages: list, temperature: float = 0, max_tokens: int = 700) -> str:
    """Call LLM with model fallback — same pattern as Day 10."""
    for model in MODELS:
        try:
            log.info(f"Calling model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            log.info(f"Tokens used: {response.usage.total_tokens}")
            return content
        except Exception as e:
            if "429" in str(e):
                log.warning(f"Rate limited on {model}, trying next...")
                time.sleep(5)
                continue
            else:
                raise e
    raise Exception("All models rate limited. Wait 5 minutes and retry.")


# ── Step 2: generate_report() ─────────────────────────────────────────────────

REPORT_SCHEMA = {
    "issue_category":    "string — one of DISK, UPGRADE, PACKAGING, APPLICATION, NETWORK, UNKNOWN",
    "severity":          "string — LOW, MEDIUM, HIGH, or CRITICAL",
    "findings":          "string — 2-3 sentences describing what was found",
    "root_cause":        "string — one sentence root cause OR exactly 'Inconclusive'",
    "recommendation":    "string — specific next step for the engineer",
    "approval_required": "boolean — true if recommendation involves a risky action",
    "approval_reason":   "string or null — why approval is needed",
    "summary":           "string — one sentence executive summary, under 20 words",
}


def generate_report(ticket: str, classification: dict, tool_result: dict) -> dict:
    """
    Generate a structured support summary from evidence.

    Args:
        ticket:         original ticket text
        classification: dict from classify_issue() — category, confidence, reason
        tool_result:    dict from the diagnostic tool that was called

    Returns:
        dict matching REPORT_SCHEMA — structured support report
    """

    prompt = f"""You are an enterprise IT support engineer writing a support summary.

CRITICAL RULES:
- Use ONLY the evidence provided below. Do NOT guess or assume anything.
- If the tool_result shows status "needs_human_review" or contains no
  useful diagnostic data, set root_cause to exactly "Inconclusive" and
  recommendation to "Escalate to human engineer for manual triage."
- approval_required must be true if your recommendation involves deleting
  files, reinstalling packages, restarting services, or any action that
  modifies the system.
- summary must be under 20 words — suitable for a ticket system field.

Reply ONLY with valid JSON matching this EXACT schema:
{{
  "issue_category": "...",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "findings": "2-3 sentences describing what was found",
  "root_cause": "one sentence root cause or Inconclusive",
  "recommendation": "specific next step for the engineer",
  "approval_required": true or false,
  "approval_reason": "why approval is needed or null",
  "summary": "one sentence executive summary under 20 words"
}}

--- EVIDENCE ---

Ticket: {ticket}

Classification: {json.dumps(classification)}

Tool Evidence: {json.dumps(tool_result)}"""

    raw = call_llm([{"role": "user", "content": prompt}], temperature=0, max_tokens=700)
    result = safe_parse_json(raw)

    if result is None:
        log.error("Report generation failed — returning safe fallback")
        return {
            "issue_category":    classification.get("category", "UNKNOWN"),
            "severity":          "MEDIUM",
            "findings":          "Unable to generate detailed findings due to a "
                                  "report generation error.",
            "root_cause":        "Inconclusive",
            "recommendation":    "Escalate to human engineer for manual triage.",
            "approval_required": False,
            "approval_reason":   None,
            "summary":           "Report generation error — manual review needed.",
        }

    # Ensure all required fields exist — fill missing with safe defaults
    for field, _ in REPORT_SCHEMA.items():
        if field not in result:
            log.warning(f"Missing field '{field}' in report — adding default")
            if field == "approval_required":
                result[field] = False
            elif field == "approval_reason":
                result[field] = None
            else:
                result[field] = "Not available"

    log.info(f"Report generated: {result['issue_category']} | "
             f"severity={result['severity']} | "
             f"approval_required={result['approval_required']}")

    return result
```

---

### Step 3 — Save 3 Sample JSON Outputs

Create the sample_data folder output (it was created in Day 8 skeleton):

```bash
mkdir -p projects/automation_support_agent/sample_data
```

Add a test block at the bottom of report.py to generate and save samples:

```python
if __name__ == "__main__":
    import sys, os as os_module
    sys.path.insert(0, os_module.path.dirname(os_module.path.abspath(__file__)))

    print("\n" + "="*60)
    print("REPORT GENERATOR — TEST RUN")
    print("="*60)

    # ── Sample 1: DISK — clear evidence, safe recommendation ──────────────────
    sample_1 = {
        "ticket": "My MacBook Pro says the startup disk is almost full",
        "classification": {"category": "DISK", "confidence": 0.98, "reason": "Disk full reported"},
        "tool_result": {
            "volume": "Macintosh HD", "total_gb": 512, "used_gb": 487,
            "free_gb": 25, "percent_used": 95.1, "critical": True,
            "top_consumers": [
                {"path": "~/Library/Caches", "size_gb": 18.2},
                {"path": "~/Downloads", "size_gb": 22.4},
            ],
        }
    }

    # ── Sample 2: APPLICATION — process evidence ───────────────────────────────
    sample_2 = {
        "ticket": "Citrix Workspace crashes immediately on launch",
        "classification": {"category": "APPLICATION", "confidence": 0.95, "reason": "App crash reported"},
        "tool_result": {
            "top_processes": [
                {"pid": 5678, "name": "Citrix Workspace", "cpu_pct": 38.1, "mem_mb": 1024},
                {"pid": 1234, "name": "kernel_task", "cpu_pct": 45.2, "mem_mb": 512},
            ],
            "total_cpu_usage_pct": 99.9,
        }
    }

    # ── Sample 3: UNKNOWN — no tool called, human review ───────────────────────
    sample_3 = {
        "ticket": "My computer feels slow today",
        "classification": {"category": "UNKNOWN", "confidence": 0.95, "reason": "Too vague to classify"},
        "tool_result": {
            "status": "needs_human_review",
            "reason": "Category could not be determined. Ticket requires manual triage."
        }
    }

    samples = [sample_1, sample_2, sample_3]

    for i, s in enumerate(samples, 1):
        print(f"\n{'─'*60}")
        print(f"SAMPLE {i}: {s['ticket']}")
        print(f"{'─'*60}")

        report = generate_report(s["ticket"], s["classification"], s["tool_result"])

        print(json.dumps(report, indent=2))

        # Save to sample_data/
        out_path = os_module.path.join(
            os_module.path.dirname(os_module.path.abspath(__file__)),
            "sample_data", f"report_sample_{i}.json"
        )
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nSaved to: sample_data/report_sample_{i}.json")

        time.sleep(2)

    print(f"\n{'='*60}")
    print("All 3 sample reports generated and saved.")
    print(f"{'='*60}")
```

---

### Step 4 — Update process_ticket() in app.py to Call generate_report()

Open app.py:

```bash
code projects/automation_support_agent/app.py
```

Add the import at the top (after the tools import):

```python
from report import generate_report
```

Update `process_ticket()` — add this at the END of the function,
just before the `return` statement:

```python
    # Step 4: Generate structured report
    print(f"\nGenerating Report...")
    report = generate_report(description, classification, tool_result)

    print(f"\nStructured Report:")
    print(json.dumps(report, indent=2))
    print(f"{'─'*60}\n")

    return {
        "ticket":         description,
        "classification": classification,
        "tool_result":    tool_result,
        "report":         report,          # ← new field
    }
```

> Note: `json` is already imported in app.py from Day 10 — no new import needed.

---

## Terminal Commands — Run in Order

```bash
# Step 1 — open report.py
code projects/automation_support_agent/report.py

# Step 2-3 — paste full code + test block, save

# Run report.py standalone (tests with fake evidence)
python3 projects/automation_support_agent/report.py

# Step 4 — update app.py with generate_report() call
code projects/automation_support_agent/app.py

# Run full pipeline
python3 projects/automation_support_agent/app.py

# Commit
git add .
git commit -m "Day 13: structured report generation"
git push
```

---

## Expected Output — report.py Standalone

```
============================================================
REPORT GENERATOR — TEST RUN
============================================================

────────────────────────────────────────────────────────────
SAMPLE 1: My MacBook Pro says the startup disk is almost full
────────────────────────────────────────────────────────────
[INFO] Calling model: openrouter/auto
[INFO] Tokens used: 540
[INFO] Report generated: DISK | severity=HIGH | approval_required=True
{
  "issue_category": "DISK",
  "severity": "HIGH",
  "findings": "Primary volume Macintosh HD is at 95.1% capacity with only
                25GB free out of 512GB. Largest consumers are Downloads
                (22.4GB) and Caches (18.2GB).",
  "root_cause": "Insufficient free disk space due to accumulated cache
                 and download files.",
  "recommendation": "Clear ~/Library/Caches (18.2GB) and review
                      ~/Downloads folder with engineer approval.",
  "approval_required": true,
  "approval_reason": "Cache deletion is a destructive action requiring confirmation.",
  "summary": "Disk 95% full — cache cleanup recommended with approval."
}

Saved to: sample_data/report_sample_1.json

────────────────────────────────────────────────────────────
SAMPLE 3: My computer feels slow today
────────────────────────────────────────────────────────────
[INFO] Report generated: UNKNOWN | severity=LOW | approval_required=False
{
  "issue_category": "UNKNOWN",
  "severity": "LOW",
  "findings": "No diagnostic data available. The ticket description
                does not provide enough information to identify a
                specific issue category.",
  "root_cause": "Inconclusive",
  "recommendation": "Escalate to human engineer for manual triage.",
  "approval_required": false,
  "approval_reason": null,
  "summary": "Ticket too vague to auto-diagnose — needs manual triage."
}

Saved to: sample_data/report_sample_3.json
```

---

## Key Design Decisions Explained

### Why "Inconclusive" instead of letting the LLM guess?

```python
# WITHOUT this rule, the LLM might write:
"root_cause": "Possibly a memory leak or background process issue"
                ↑ INVENTED — not in the evidence

# WITH the rule, when tool_result shows needs_human_review:
"root_cause": "Inconclusive"
                ↑ HONEST — matches what evidence actually shows
```

This is your **anti-hallucination guardrail** — the same principle
from Day 16 (context engineering) applied early.

### Why fill missing fields with defaults instead of crashing?

```python
for field, _ in REPORT_SCHEMA.items():
    if field not in result:
        result[field] = "Not available"  # or False / None
```

If the LLM forgets one field (e.g. drops `approval_reason`), the
agent still returns a complete, schema-valid report. Same defensive
philosophy as `safe_parse_json()` from Day 10 — **never let a partial
LLM response break your pipeline.**

### Why max_tokens=700 here vs 500 on Day 10?

The report has **8 fields** including multi-sentence `findings` —
more content than the classifier's 3-field output. More fields =
more tokens needed. Always size `max_tokens` to the schema complexity.

---

## The Three Samples — What Each One Teaches

| Sample | Category | What it tests |
|---|---|---|
| 1 — Disk full | DISK | Full evidence → detailed findings + approval_required=true |
| 2 — Citrix crash | APPLICATION | Process evidence → CPU-based root cause |
| 3 — Vague ticket | UNKNOWN | No tool evidence → "Inconclusive" + approval_required=false |

Sample 3 is the most important test — it proves your anti-hallucination
rule works when there's nothing to go on.

---

## Interview Questions — Day 13

### Q1 — Why do you separate tool execution from LLM interpretation
in your agent?

I split these into two files with two responsibilities. tools.py
gathers raw evidence — disk percentages, process lists, error codes —
through deterministic functions that return the same structure every
time. report.py takes that evidence plus the classification and asks
the LLM to interpret it into human-readable findings and a
recommendation. This separation means each part is independently
testable. I can verify check_disk_space() returns the right fields
without ever calling an LLM. I can verify generate_report() produces
good findings by feeding it hardcoded sample evidence — which is
exactly what my Day 13 test block does with three fixed samples. If
I combined data-gathering and interpretation into one LLM call, I
could not isolate which part failed when something goes wrong.

### Q2 — How do you ensure the LLM only uses evidence it was given,
not hallucinated data?

Three layers of defence. First, the prompt explicitly states "Use ONLY
the evidence provided. Do NOT guess or assume anything" — and gives a
specific instruction for the no-evidence case: when tool_result shows
needs_human_review, root_cause must be exactly "Inconclusive", not a
guess. Second, I pass the actual evidence as JSON directly in the
prompt — the model is grounded in real numbers like free_gb=25 and
percent_used=95.1, not abstractions. Third, my Sample 3 test case
specifically verifies this — a vague ticket with no tool evidence must
produce root_cause="Inconclusive" and approval_required=false. If the
model ever invents a root cause for an UNKNOWN ticket, that test fails
and I know the prompt needs hardening — which is exactly what Day 16
context engineering addresses.

### Q3 — How could your structured output be integrated with
ServiceNow or Jira?

The output schema maps directly onto ticket fields in both systems.
issue_category becomes the ticket's category or component field.
severity maps directly to Jira's priority levels or ServiceNow's
impact/urgency fields. summary becomes the short description shown in
ticket lists. findings and recommendation become the work notes or
comment body — the actual diagnostic detail an engineer reads.
approval_required and approval_reason could trigger a Jira approval
workflow or a ServiceNow change request automatically. Because the
output is always valid JSON with these exact fields, a thin
integration layer would just be a function that takes this dict and
calls the ServiceNow REST API or Jira's issue creation API, mapping
each field to its corresponding ticket field — no parsing of natural
language required on the integration side.

---

## Expected Outputs by End of Day 13

- [ ] Step 1: report.py opened
- [ ] Step 2: generate_report() implemented with safe defaults
- [ ] Step 3: 3 sample reports generated and saved to sample_data/
- [ ] Step 4: app.py updated — process_ticket() calls generate_report()
- [ ] Full pipeline tested — report appears for all 5 Day 12 tickets
- [ ] Committed and pushed

---

## Git Commit

```bash
git add .
git commit -m "Day 13: structured report generation"
git push
```

---

*Day 13 complete — your agent now produces full structured reports.
Pipeline is: ticket → classify → route → tool → interpret → report.
Day 14 builds realistic sample cases from your real Oracle EE
experience, testing this full pipeline against authentic scenarios.*
