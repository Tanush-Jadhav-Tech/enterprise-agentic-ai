# Day 09 — Define Enterprise Requirements

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Write a proper MVP specification for the Automation Support Agent

---

## Study Resources

- OpenAI Agents Guide — Guardrails:
  https://openai.github.io/openai-agents-python/guardrails/
- OpenAI Agents Guide — Running Agents:
  https://openai.github.io/openai-agents-python/running_agents/

---

## Core Concepts

| Concept | Definition |
|---|---|
| MVP | Minimum Viable Product — smallest version that proves the concept and is safe to demo |
| Safe tools | Read-only diagnostics — auto-run allowed, no risk |
| Risky tools | Delete/cleanup/reinstall — requires human approval always |
| Structured output | Always return JSON with fixed fields — machine-readable and testable |
| Issue categories | Define routing logic — classifier sends each ticket to the right tool |

---

## Step-by-Step Instructions

### Step 1 — Open projects/automation_support_agent/requirements.md

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
code projects/automation_support_agent/requirements.md
```

Paste the full requirements content below into this file.
This is your MVP specification document — written before any code.

---

### Step 2 — Define 5 Issue Categories with Examples

These are the categories your classifier will use to route every ticket.
Based directly on your 20 years of Oracle EE support experience.

```markdown
## Issue Categories

| Category    | Examples from Oracle EE Experience |
|---|---|
| DISK        | Low disk space, storage full, cannot save files, upgrade needs space |
| UPGRADE     | macOS upgrade stuck/failed, version mismatch, update loop |
| PACKAGING   | pkg install failure, notarization error, code signing issue, Gatekeeper block |
| APPLICATION | App crash, won't launch, license error, Citrix/Zoom/Slack issues |
| NETWORK     | VPN not connecting, intermittent drops, DNS issues, proxy errors |
| UNKNOWN     | Cannot classify with confidence — route to human review |
```

---

### Step 3 — List All Tools — Mark Each as SAFE or RISKY

**Rule:**
- SAFE = read-only, no system change, auto-run allowed
- RISKY = modifies or deletes something, always needs approval

```markdown
## Tools — SAFE vs RISKY

### SAFE Tools (auto-run — no approval needed)

| Tool | Function | Returns |
|---|---|---|
| check_disk_space() | Check free space, Caches, Trash sizes | dict: volume, total_gb, free_gb, critical |
| check_os_version() | Current macOS version, pending updates | dict: version, build, pending_update |
| check_running_processes() | Top CPU consumers | dict: top_processes, total_cpu_pct |
| read_sample_log(path) | Last 20 lines, error count | dict: total_lines, error_count, errors |

### RISKY Tools (approval required — always)

| Tool | Function | Risk |
|---|---|---|
| clear_cache() | Deletes ~/Library/Caches/* | Permanent deletion |
| reinstall_package(name) | Reinstalls a named package | System modification |
| force_reboot() | Schedules system restart | User session interrupted |
| run_cleanup_script() | Runs clear_cache_mac.sh | Permanent deletion |
```

**Routing Registry — connects category to tool:**

```python
TOOL_REGISTRY = {
    "DISK":        check_disk_space,
    "UPGRADE":     check_os_version,
    "PACKAGING":   check_os_version,
    "APPLICATION": check_running_processes,
    "NETWORK":     check_running_processes,
    "UNKNOWN":     None   # no tool — route to human review
}

SAFE_TOOLS  = ["check_disk_space", "check_os_version",
               "check_running_processes", "read_sample_log"]

RISKY_TOOLS = ["clear_cache", "reinstall_package",
               "force_reboot", "run_cleanup_script"]
```

---

### Step 4 — Define the Output Schema

Every agent run must return this exact JSON structure.
Fixed fields make the output machine-readable and testable.

```markdown
## Output Schema (JSON — fixed fields, always produced)

```json
{
  "issue_category":    "DISK",
  "confidence_score":  0.95,
  "tools_invoked":     ["check_disk_space"],
  "findings":          "2-3 sentences describing what was found",
  "root_cause":        "one sentence root cause or Inconclusive",
  "recommendation":    "specific next step for the engineer",
  "approval_required": false,
  "approval_reason":   null,
  "summary":           "one sentence executive summary"
}
```

### Field Rules
- issue_category: always one of DISK, UPGRADE, PACKAGING, APPLICATION, NETWORK, UNKNOWN
- confidence_score: 0.0 to 1.0 — always include
- tools_invoked: list of tool names called — empty list if none
- findings: ONLY from tool evidence — never hallucinated or guessed
- root_cause: one sentence or exactly the word "Inconclusive"
- recommendation: specific and actionable — never vague
- approval_required: true if ANY risky tool was or will be called
- approval_reason: why approval is needed, or null if not required
- summary: suitable for ticket system update — under 20 words
```

---

### Step 5 — Write Acceptance Criteria

How will you know the MVP is working?
These are your pass/fail tests — you will run them on Day 17.

```markdown
## Acceptance Criteria

The MVP is complete when ALL of these pass:

### Classification
- [ ] DISK ticket → DISK category with confidence >= 0.85
- [ ] APPLICATION ticket → APPLICATION with confidence >= 0.80
- [ ] UPGRADE ticket → UPGRADE with confidence >= 0.90
- [ ] Vague ticket ("my laptop is slow") → confidence < 0.75
- [ ] Nonsense ticket ("error code 11001") → UNKNOWN

### Tool Routing
- [ ] DISK → check_disk_space() called automatically
- [ ] APPLICATION → check_running_processes() called automatically
- [ ] UNKNOWN → no tool called, human review message returned
- [ ] Low confidence (< 0.60) → no auto-action, flagged for review

### Safety
- [ ] SAFE tools run without any prompt
- [ ] RISKY tools always show approval gate before executing
- [ ] Agent never deletes files without explicit human yes
- [ ] Agent never crashes on unexpected or empty input

### Output
- [ ] All outputs are valid JSON matching schema above
- [ ] findings field never contains invented information
- [ ] summary field is under 20 words
- [ ] approval_required is true whenever a risky tool is involved

### Evaluation Target (Day 17)
- [ ] 8 out of 10 eval cases pass
- [ ] All 3 tricky edge cases handled gracefully
- [ ] Pass rate documented in eval_cases.md
```

---

## Complete requirements.md File — Paste This Into Your Project

Below is the full file to paste into
`projects/automation_support_agent/requirements.md`:

```markdown
# Automation Support Agent — MVP Requirements
> Oracle Enterprise Engineering | Agentic AI Portfolio Project
> Version 1.0 | Written Day 09

---

## Problem Statement

Oracle EE support engineers handle hundreds of tickets daily.
Many follow predictable diagnostic patterns:
- Check disk → recommend cleanup
- Check processes → identify hung application
- Check OS version → confirm upgrade eligibility
- Read log → identify root cause

This agent automates the diagnostic layer, freeing engineers
for complex escalations and reducing mean time to resolution.

---

## Step 2 — Issue Categories

| Category    | Examples from Oracle EE Experience |
|---|---|
| DISK        | Low disk space, storage full, cannot save files, upgrade needs space |
| UPGRADE     | macOS upgrade stuck/failed, version mismatch, update loop |
| PACKAGING   | pkg install failure, notarization error, code signing issue |
| APPLICATION | App crash, won't launch, license error, Citrix/Zoom/Slack issues |
| NETWORK     | VPN not connecting, intermittent drops, DNS issues |
| UNKNOWN     | Cannot classify with confidence — route to human review |

---

## Step 3 — Tools — SAFE vs RISKY

### SAFE Tools (auto-run — no approval needed)

| Tool | Function | Returns |
|---|---|---|
| check_disk_space() | Check free space, Caches, Trash | dict: volume, free_gb, critical |
| check_os_version() | macOS version, pending updates | dict: version, pending_update |
| check_running_processes() | Top CPU consumers | dict: top_processes, cpu_pct |
| read_sample_log(path) | Last 20 lines, error count | dict: error_count, errors |

### RISKY Tools (approval required — always)

| Tool | Function | Risk |
|---|---|---|
| clear_cache() | Deletes ~/Library/Caches/* | Permanent deletion |
| reinstall_package(name) | Reinstalls named package | System modification |
| force_reboot() | Schedules restart | Session interrupted |
| run_cleanup_script() | Runs clear_cache_mac.sh | Permanent deletion |

### Routing Registry

```python
TOOL_REGISTRY = {
    "DISK":        check_disk_space,
    "UPGRADE":     check_os_version,
    "PACKAGING":   check_os_version,
    "APPLICATION": check_running_processes,
    "NETWORK":     check_running_processes,
    "UNKNOWN":     None
}
SAFE_TOOLS  = ["check_disk_space", "check_os_version",
               "check_running_processes", "read_sample_log"]
RISKY_TOOLS = ["clear_cache", "reinstall_package",
               "force_reboot", "run_cleanup_script"]
```

### Confidence Thresholds

| Confidence | Action |
|---|---|
| >= 0.75 | Auto-route to tool |
| 0.60 – 0.74 | Route but flag for review |
| < 0.60 | Skip tool — human review |

---

## Step 4 — Output Schema (JSON — fixed fields)

```json
{
  "issue_category":    "DISK",
  "confidence_score":  0.95,
  "tools_invoked":     ["check_disk_space"],
  "findings":          "2-3 sentences from tool evidence only",
  "root_cause":        "one sentence or Inconclusive",
  "recommendation":    "specific actionable next step",
  "approval_required": false,
  "approval_reason":   null,
  "summary":           "one sentence under 20 words"
}
```

Field rules:
- findings: ONLY from tool evidence — never hallucinated
- root_cause: one sentence or exactly "Inconclusive"
- approval_required: true if ANY risky tool is involved
- summary: under 20 words — suitable for ticket system

---

## Step 5 — Acceptance Criteria

### Classification
- [ ] DISK ticket → DISK, confidence >= 0.85
- [ ] APPLICATION ticket → APPLICATION, confidence >= 0.80
- [ ] UPGRADE ticket → UPGRADE, confidence >= 0.90
- [ ] Vague ticket → confidence < 0.75
- [ ] Nonsense input → UNKNOWN

### Tool Routing
- [ ] DISK → check_disk_space() auto-runs
- [ ] APPLICATION → check_running_processes() auto-runs
- [ ] UNKNOWN → no tool, human review message
- [ ] Low confidence → flagged, no auto-action

### Safety
- [ ] SAFE tools run without prompt
- [ ] RISKY tools always show approval gate
- [ ] No file deletion without explicit yes
- [ ] No crash on unexpected input

### Output
- [ ] Valid JSON matching schema every time
- [ ] findings never contains invented information
- [ ] summary under 20 words always
- [ ] approval_required correct every time

### Evaluation (Day 17 target)
- [ ] 8 out of 10 eval cases pass
- [ ] Pass rate documented in eval_cases.md
```

---

## Sample Input → Expected Output

### Input Ticket
```
"My MacBook Pro says the startup disk is almost full.
 I cannot save any new files. Running macOS 14.2.1."
```

### Expected JSON Output
```json
{
  "issue_category":    "DISK",
  "confidence_score":  0.97,
  "tools_invoked":     ["check_disk_space"],
  "findings":          "Primary volume shows 487GB used of 512GB total (95.1%).
                        Critical threshold exceeded. Free space: 25GB remaining.",
  "root_cause":        "Insufficient free disk space preventing file write operations.",
  "recommendation":    "Clear ~/Library/Caches (18GB) with engineer approval.",
  "approval_required": true,
  "approval_reason":   "Cache deletion is destructive — requires confirmation.",
  "summary":           "Disk 95% full — cache cleanup recommended with approval."
}
```

---

## Interview Questions — Day 9

### Q1 — What is the difference between an MVP and a production-ready agent?

An MVP proves the concept works end-to-end with minimum features needed
for a meaningful demo. My Automation Support Agent MVP classifies tickets,
calls mock diagnostic tools, and generates structured JSON reports.
It uses simulated tool data because the goal is to prove the architecture
works — not to ship to production. A production-ready agent replaces mock
tools with real system calls, adds proper logging and monitoring, and
integrates with ticketing systems like ServiceNow or Jira. The MVP gets
you to a working demo in 30 days. Production takes months of hardening.
Knowing this distinction tells an interviewer you understand software
lifecycle, not just code.

### Q2 — How do you decide which agent actions need human approval?

I use a simple two-tier classification. SAFE tools are read-only —
check_disk_space(), check_running_processes(), read_log_file() — auto-run
because the worst case is reading incorrect data. RISKY tools modify
system state — clear_cache(), reinstall_package(), force_reboot() — always
require human approval because they are irreversible or disruptive. The
rule: if undoing the action requires effort or causes data loss, it is
RISKY. I list every tool as SAFE or RISKY in requirements.md before
writing a single line of code — this forces the design decision to be
made consciously rather than discovered during a production incident.

### Q3 — Why is structured JSON output important for enterprise AI agents?

Three reasons. First, machines can parse it — a JSON report can be written
directly to a ticketing system without further processing. Second, it is
testable — I can write eval cases that check whether confidence_score is
above 0.75 or approval_required is correctly set. Third, it enforces
discipline on the LLM — when you specify an exact schema, the model cannot
hide uncertainty in vague prose. In my agent the output schema is fixed in
requirements.md before any code is written — downstream systems depend on
it and it must never change without a version bump.

---

## Git Commit

```bash
git add .
git commit -m "Day 9: MVP requirements — categories, tools, schema, acceptance criteria"
git push
```

---

## Expected Outputs by End of Day 9

- [ ] Step 1: requirements.md opened
- [ ] Step 2: 5 issue categories defined with Oracle EE examples
- [ ] Step 3: all tools listed as SAFE or RISKY with TOOL_REGISTRY
- [ ] Step 4: JSON output schema with field rules defined
- [ ] Step 5: acceptance criteria — 15 checkboxes written
- [ ] Committed and pushed to GitHub

---

*Day 09 complete — requirements written before code.
Day 10 is the first real code — the issue classifier.*
