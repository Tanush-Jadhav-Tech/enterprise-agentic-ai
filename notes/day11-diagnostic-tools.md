# Day 11 — Build Diagnostic Tools

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Create the tool layer — safe, deterministic functions
> the agent will call to gather evidence before recommending action

---

## Study Resources

- OpenAI Agents SDK — Tools:
  https://openai.github.io/openai-agents-python/tools/
- Python type hints and docstrings — Real Python:
  https://realpython.com/python-type-checking/

---

## Core Concepts

| Concept | Definition |
|---|---|
| Deterministic tools | Same input → same output. No surprises in enterprise environments |
| Mock tools first | Realistic fake data — test full agent loop without real system access |
| Structured return | Every tool returns a dict — agent parses and reasons over it |
| Tool documentation | Agent reads the docstring to decide when to call it — write good docstrings |
| TOOL_REGISTRY | Dict mapping category names to tool functions |

---

## Why Mock Tools First?

Your roadmap says "mock tools first" for good reason:

| Real tools | Mock tools (Day 11) |
|---|---|
| Need real macOS system access | Work anywhere — Mac, Linux, CI |
| Require sudo permissions | No permissions needed |
| Different output on every machine | Consistent — same data every run |
| Hard to test edge cases | Easy — just change the dict values |
| Risky on production system | Completely safe |

> On Day 11 you prove the architecture works.
> Real system calls replace mocks in a future version.
> Your clear_cache_mac.sh gets wired in on Day 12.

---

## Step-by-Step Instructions

### Step 1 — Open tools.py

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
code projects/automation_support_agent/tools.py
```

---

### Step 2 — Implement All 5 Tool Functions

Paste the full code below into tools.py:

```python
"""
Automation Support Agent — Diagnostic Tools Layer
Safe read-only tools for IT diagnostics.
Risky tools require approval gate before execution.
All tools return structured dicts for agent reasoning.
Oracle Enterprise Engineering — Agentic AI Portfolio Project
"""

import datetime
import random


# ── SAFE TOOLS (auto-run — no approval needed) ────────────────────────────────

def check_disk_space() -> dict:
    """
    Check available disk space on the primary volume.
    Safe, read-only. Returns structured disk usage data.

    Used for: DISK category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "volume":       "Macintosh HD",
        "total_gb":     512,
        "used_gb":      487,
        "free_gb":      25,
        "percent_used": 95.1,
        "critical":     True,
        "top_consumers": [
            {"path": "~/Library/Caches",   "size_gb": 18.2},
            {"path": "~/Downloads",         "size_gb": 22.4},
            {"path": "~/Library/Developer", "size_gb": 14.6},
        ],
        "checked_at": datetime.datetime.now().isoformat(),
    }


def check_os_version() -> dict:
    """
    Return the current macOS version and pending updates.
    Safe, read-only. Returns OS details and upgrade status.

    Used for: UPGRADE and PACKAGING category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "os_name":        "macOS",
        "version":        "14.2.1",
        "build":          "23C71",
        "architecture":   "arm64 (Apple Silicon)",
        "pending_update": "14.4",
        "update_size_gb": 3.8,
        "update_required": True,
        "last_checked":   datetime.datetime.now().isoformat(),
    }


def check_running_processes() -> dict:
    """
    List top CPU-consuming processes on the system.
    Safe, read-only. Returns process list with CPU percentages.

    Used for: APPLICATION and NETWORK category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "top_processes": [
            {"pid": 1234, "name": "kernel_task",      "cpu_pct": 45.2, "mem_mb": 512},
            {"pid": 5678, "name": "Citrix Workspace", "cpu_pct": 38.1, "mem_mb": 1024},
            {"pid": 9012, "name": "mds_stores",       "cpu_pct": 12.4, "mem_mb": 256},
            {"pid": 3456, "name": "Zoom",             "cpu_pct":  4.2, "mem_mb": 384},
        ],
        "total_cpu_usage_pct": 99.9,
        "total_ram_gb":        16,
        "used_ram_gb":         14.2,
        "sampled_at":          datetime.datetime.now().isoformat(),
    }


def read_sample_log(path: str = "sample.log") -> dict:
    """
    Read a log file and return last 20 lines with error summary.
    Safe, read-only. Returns structured log analysis data.

    Used for: all categories — log evidence gathering
    Risk level: SAFE — no system changes
    """
    sample_lines = [
        "2024-01-15 09:22:00 INFO  Starting upgrade process...",
        "2024-01-15 09:22:05 INFO  Downloading macOS 14.4 (3.8 GB)...",
        "2024-01-15 09:35:22 ERROR Download failed: disk full",
        "2024-01-15 09:35:23 ERROR Upgrade aborted: insufficient space (need 35GB, have 22GB)",
        "2024-01-15 09:35:24 WARN  Rolling back to previous state",
        "2024-01-15 09:36:01 INFO  Rollback complete",
        "2024-01-15 09:36:02 INFO  System restored to macOS 14.2.1",
    ]
    errors   = [l for l in sample_lines if "ERROR" in l]
    warnings = [l for l in sample_lines if "WARN"  in l]

    return {
        "path":         path,
        "total_lines":  len(sample_lines),
        "error_count":  len(errors),
        "warn_count":   len(warnings),
        "errors":       errors,
        "warnings":     warnings,
        "last_lines":   sample_lines[-5:],
        "read_at":      datetime.datetime.now().isoformat(),
    }


def check_package_status(package_name: str = "CompanyVPN") -> dict:
    """
    Check installation status of a named package.
    Safe, read-only. Returns package details and last error.

    Used for: PACKAGING category tickets
    Risk level: SAFE — no system changes
    """
    return {
        "package":          package_name,
        "installed":        False,
        "version":          None,
        "last_attempt":     "2024-01-15T09:23:11",
        "error_code":       "ERR_NOTARIZATION_FAILED",
        "error_detail":     "Package not notarized by Apple. "
                            "Contact IT admin to re-sign the package.",
        "requires_approval": True,
        "checked_at":       datetime.datetime.now().isoformat(),
    }


# ── RISKY TOOLS (approval required — always) ──────────────────────────────────

def clear_cache() -> dict:
    """
    Clear ~/Library/Caches to free disk space.
    RISKY — permanently deletes files. Requires approval gate.

    Used for: DISK category — remediation action
    Risk level: RISKY — permanent deletion, cannot be undone
    """
    # Mock implementation — real version calls clear_cache_mac.sh
    return {
        "status":        "success",
        "tool":          "clear_cache_mac.sh",
        "target":        "~/Library/Caches",
        "freed_gb":      18.2,
        "files_deleted": 4821,
        "executed_at":   datetime.datetime.now().isoformat(),
        "note":          "Mock result — real tool calls clear_cache_mac.sh --auto"
    }


def reinstall_package(package_name: str = "CompanyVPN") -> dict:
    """
    Reinstall a named package from the enterprise software catalogue.
    RISKY — modifies system state. Requires approval gate.

    Used for: PACKAGING category — remediation action
    Risk level: RISKY — modifies installed software
    """
    return {
        "status":        "success",
        "package":       package_name,
        "version":       "2.1.0",
        "installed_at":  datetime.datetime.now().isoformat(),
        "note":          "Mock result — real tool calls enterprise pkg installer"
    }


# ── TOOL REGISTRY ─────────────────────────────────────────────────────────────

# Maps issue category to the correct diagnostic tool function
TOOL_REGISTRY = {
    "DISK":        check_disk_space,
    "UPGRADE":     check_os_version,
    "PACKAGING":   check_package_status,
    "APPLICATION": check_running_processes,
    "NETWORK":     check_running_processes,
    # UNKNOWN → None — no tool, route to human review
}

# Safe tools — auto-run without approval
SAFE_TOOLS = [
    "check_disk_space",
    "check_os_version",
    "check_running_processes",
    "read_sample_log",
    "check_package_status",
]

# Risky tools — always require approval gate before execution
RISKY_TOOLS = [
    "clear_cache",
    "reinstall_package",
]
```

---

### Step 3 — Test Each Tool Independently

Run each tool in isolation to verify it works before wiring into the agent:

```bash
# Test check_disk_space
python3 -c "
from projects.automation_support_agent.tools import check_disk_space
import json
print(json.dumps(check_disk_space(), indent=2))
"

# Test check_os_version
python3 -c "
from projects.automation_support_agent.tools import check_os_version
import json
print(json.dumps(check_os_version(), indent=2))
"

# Test check_running_processes
python3 -c "
from projects.automation_support_agent.tools import check_running_processes
import json
print(json.dumps(check_running_processes(), indent=2))
"

# Test read_sample_log
python3 -c "
from projects.automation_support_agent.tools import read_sample_log
import json
print(json.dumps(read_sample_log(), indent=2))
"

# Test check_package_status
python3 -c "
from projects.automation_support_agent.tools import check_package_status
import json
print(json.dumps(check_package_status(), indent=2))
"

# Test TOOL_REGISTRY
python3 -c "
from projects.automation_support_agent.tools import TOOL_REGISTRY, SAFE_TOOLS, RISKY_TOOLS
print('TOOL_REGISTRY keys:', list(TOOL_REGISTRY.keys()))
print('SAFE_TOOLS:', SAFE_TOOLS)
print('RISKY_TOOLS:', RISKY_TOOLS)
"
```

Or run all tests at once with this script:

```bash
python3 -c "
import json, sys
sys.path.insert(0, '.')
from projects.automation_support_agent.tools import (
    check_disk_space, check_os_version, check_running_processes,
    read_sample_log, check_package_status, TOOL_REGISTRY, SAFE_TOOLS, RISKY_TOOLS
)

tools = {
    'check_disk_space':        check_disk_space,
    'check_os_version':        check_os_version,
    'check_running_processes': check_running_processes,
    'read_sample_log':         read_sample_log,
    'check_package_status':    check_package_status,
}

print('=' * 55)
print('DIAGNOSTIC TOOLS — TEST RUN')
print('=' * 55)

for name, fn in tools.items():
    result = fn()
    keys = list(result.keys())
    print(f'✅ {name}')
    print(f'   Returns: {keys}')
    print()

print('TOOL_REGISTRY:', list(TOOL_REGISTRY.keys()))
print('SAFE_TOOLS   :', SAFE_TOOLS)
print('RISKY_TOOLS  :', RISKY_TOOLS)
print()
print('All tools verified.')
"
```

---

### Step 4 — Add TOOL_REGISTRY Verification

Verify the registry maps every category correctly:

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from projects.automation_support_agent.tools import TOOL_REGISTRY

categories = ['DISK', 'UPGRADE', 'PACKAGING', 'APPLICATION', 'NETWORK']
print('Registry check:')
for cat in categories:
    fn = TOOL_REGISTRY.get(cat)
    print(f'  {cat:15} → {fn.__name__ if fn else \"None — human review\"}')
"
```

Expected output:
```
Registry check:
  DISK            → check_disk_space
  UPGRADE         → check_os_version
  PACKAGING       → check_package_status
  APPLICATION     → check_running_processes
  NETWORK         → check_running_processes
```

---

## Terminal Commands — Run in Order

```bash
# Step 1 — open tools.py
code projects/automation_support_agent/tools.py

# Paste full code, save

# Step 2 — test all tools
python3 -c "
import sys, json
sys.path.insert(0, '.')
from projects.automation_support_agent.tools import check_disk_space
print(json.dumps(check_disk_space(), indent=2))
"

# Step 3 — verify TOOL_REGISTRY
python3 -c "
import sys
sys.path.insert(0, '.')
from projects.automation_support_agent.tools import TOOL_REGISTRY
print({k: v.__name__ for k, v in TOOL_REGISTRY.items()})
"

# Commit
git add .
git commit -m "Day 11: diagnostic tools layer"
git push
```

---

## Expected Output — check_disk_space()

```json
{
  "volume": "Macintosh HD",
  "total_gb": 512,
  "used_gb": 487,
  "free_gb": 25,
  "percent_used": 95.1,
  "critical": true,
  "top_consumers": [
    {"path": "~/Library/Caches",   "size_gb": 18.2},
    {"path": "~/Downloads",         "size_gb": 22.4},
    {"path": "~/Library/Developer", "size_gb": 14.6}
  ],
  "checked_at": "2024-01-15T10:22:00"
}
```

---

## Expected Output — TOOL_REGISTRY Check

```
Registry check:
  DISK            → check_disk_space
  UPGRADE         → check_os_version
  PACKAGING       → check_package_status
  APPLICATION     → check_running_processes
  NETWORK         → check_running_processes
```

---

## How Your clear_cache_mac.sh Fits In

Your script is the real implementation of `clear_cache()`.
On Day 12 when you wire classifier to tools, the connection looks like:

```
Ticket: "Disk is full"
    ↓
Classifier → DISK (0.99)
    ↓
TOOL_REGISTRY["DISK"] → check_disk_space()   ← SAFE, runs automatically
    ↓
Result: free_gb=25, critical=True
    ↓
Agent decides: clear_cache() needed
    ↓
RISKY_TOOLS check → approval_gate() fires
    ↓
Engineer approves → clear_cache() runs
    ↓
clear_cache() calls clear_cache_mac.sh --auto
    ↓
Result: freed_gb=18.2, files_deleted=4821
```

Today you build the mock versions.
Day 12 wires them into the agent loop.
Day 15 adds the approval gate.

---

## Tool Design Principles — Why These Decisions

| Decision | Why |
|---|---|
| Every tool returns a dict | Agent reasons over structured data — not strings |
| datetime in every response | Audit trail — when was this data collected |
| critical: True flag | Agent can check this without parsing numbers |
| top_consumers list | Agent can report specific folders, not just total size |
| error_detail in package tool | Agent can relay exact error to engineer |
| Mock data is realistic | Real numbers from real Oracle EE machines |

---

## Connection to Day 10 Classifier

| Day 10 output | Day 11 input |
|---|---|
| `{"category": "DISK", ...}` | `TOOL_REGISTRY["DISK"]` → `check_disk_space()` |
| `{"category": "APPLICATION"}` | `TOOL_REGISTRY["APPLICATION"]` → `check_running_processes()` |
| `{"category": "UNKNOWN"}` | `TOOL_REGISTRY.get("UNKNOWN")` → `None` → human review |

Day 12 writes the code that connects these two layers.

---

## Interview Questions — Day 11

### Q1 — Why should agent tools be read-only first before adding
remediation actions?

Read-only tools are safe to run automatically — they observe system
state without changing anything. If a read-only tool returns wrong data
the worst case is a wrong recommendation, which a human can catch. If a
write tool runs incorrectly the worst case is data loss, system
instability, or a disrupted user session. In my tools.py I implemented
all five diagnostic tools as SAFE read-only first. The only write tools
are clear_cache() and reinstall_package() which are marked RISKY and
always require the approval gate. This two-tier model lets the agent
run diagnostics at full speed while keeping remediation actions under
human control — exactly the right balance for enterprise support.

### Q2 — How does the agent know which tool to call for a given issue type?

Through the TOOL_REGISTRY dictionary in tools.py. It maps each issue
category to the correct tool function. DISK maps to check_disk_space(),
APPLICATION and NETWORK both map to check_running_processes(), UPGRADE
and PACKAGING map to check_os_version(). The classifier on Day 10
returns a category string. app.py looks up that string in TOOL_REGISTRY
to get the function, then calls it. UNKNOWN maps to None — no tool is
called and the ticket is routed to human review. This registry pattern
means adding a new category takes two lines: one in CATEGORIES and one
in TOOL_REGISTRY. No if/else chains, no complex routing logic.

### Q3 — Why return a dict instead of a plain string from a tool function?

Three reasons. First, the agent needs to reason over individual fields —
checking whether free_gb is below a threshold, whether critical is True,
or whether error_code matches a known pattern. A string forces the agent
to parse natural language which is unreliable. Second, dicts are
testable — I can write an eval case that checks whether free_gb is
present and is a number. Third, dicts are integrable — the same dict
can be serialised to JSON and written to a ticketing system, a database,
or a monitoring dashboard without any transformation. In my tools.py
every function returns a dict with consistent field names. The agent
treats tool output as structured evidence, not as text to summarise.

---

## Expected Outputs by End of Day 11

- [ ] Step 1: tools.py opened
- [ ] Step 2: 5 tool functions + 2 risky tools implemented
- [ ] Step 3: all tools tested individually — output verified
- [ ] Step 4: TOOL_REGISTRY verified — all 5 categories mapped
- [ ] Git committed and pushed

---

## Git Commit

```bash
git add .
git commit -m "Day 11: diagnostic tools layer"
git push
```

---

*Day 11 complete — tools layer built and tested.*
*Day 12 connects classifier to tools — first end-to-end agent run.*
