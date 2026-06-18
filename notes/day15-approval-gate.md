# Day 15 — Add Approval Gate (Human-in-the-Loop)

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Implement the safety model — human approval before any
> risky action. This is non-negotiable in enterprise automation.

---

## Study Resources

- OpenAI Agents SDK — Guardrails & Human Review:
  https://openai.github.io/openai-agents-python/guardrails/
- OpenAI: Safety in building agents:
  https://developers.openai.com/api/docs/guides/agents

---

## Core Concepts

| Concept | Definition |
|---|---|
| HITL | Human-in-the-Loop — agent pauses and asks human before proceeding |
| Safe actions | Reading logs, checking disk, listing processes — no risk, auto-run |
| Risky actions | Deleting files, reinstalling packages, running remediation scripts |
| Approval gate | The code that pauses the agent and waits for human yes/no |
| Production requirement | This is the difference between a demo agent and a production agent |

---

## Why This Is Your Strongest Interview Talking Point

Most AI agent demos show an agent that just runs and does things.
Your agent STOPS and asks before doing anything destructive.

```
Demo agent:    ticket → classify → tool → DELETE FILES → done
Your agent:    ticket → classify → tool → READ evidence → PAUSE
                                          → show engineer what will happen
                                          → wait for YES
                                          → only then act
```

In 20 years of IT support at Oracle you never ran a cleanup script
without confirming with the user first. Your agent does the same thing.
That is domain expertise applied to AI safety design.

---

## Step-by-Step Instructions

### Step 1 — Add SAFE_TOOLS and RISKY_TOOLS to tools.py

Open tools.py — these lists already exist from Day 11.
Verify they are there:

```bash
grep -A 10 "SAFE_TOOLS" projects/automation_support_agent/tools.py
```

If missing, add at the bottom of tools.py:

```python
# These already exist from Day 11 — verify before adding
SAFE_TOOLS = [
    "check_disk_space",
    "check_os_version",
    "check_running_processes",
    "read_sample_log",
    "check_package_status",
]

RISKY_TOOLS = [
    "clear_cache",
    "reinstall_package",
    "force_reboot",
    "run_cleanup_script",
]
```

---

### Step 2 — Add approval_gate() to app.py

Open app.py:

```bash
code projects/automation_support_agent/app.py
```

Add this function after `classify_issue()` and before `process_ticket()`:

```python
# ── Step 2: approval_gate() ───────────────────────────────────────────────────

SAFE_ACTIONS  = ["check_disk_space", "check_os_version",
                 "check_running_processes", "read_sample_log",
                 "check_package_status"]

RISKY_ACTIONS = ["clear_cache", "reinstall_package",
                 "force_reboot", "run_cleanup_script"]


def approval_gate(action_name: str, details: str) -> bool:
    """
    Pause and ask human for approval before a risky action.

    This is the Human-in-the-Loop (HITL) pattern.
    Called ONLY for RISKY_ACTIONS — never for SAFE_ACTIONS.

    Args:
        action_name: name of the risky action being proposed
        details:     what will happen if approved — shown to engineer

    Returns:
        True if approved, False if declined
    """
    print(f"\n{'='*60}")
    print(f"[APPROVAL REQUIRED]")
    print(f"{'='*60}")
    print(f"Action  : {action_name}")
    print(f"Details : {details}")
    print(f"{'='*60}")
    print(f"⚠️  This action cannot be undone.")
    print()

    while True:
        answer = input("Approve this action? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            log.info(f"Approval GRANTED for action: {action_name}")
            return True
        elif answer in ("no", "n"):
            log.info(f"Approval DECLINED for action: {action_name}")
            return False
        else:
            print("Please type 'yes' or 'no'")


def is_risky(tool_name: str) -> bool:
    """Check if a tool name is in the RISKY_ACTIONS list."""
    return tool_name in RISKY_ACTIONS
```

---

### Step 3 — Update process_ticket() to Check Risk Level

Update the tool routing section inside `process_ticket()`.
Find this block:

```python
        else:
            tool_fn = TOOL_REGISTRY.get(category)

            if tool_fn is None:
                print(f"\nRouting: no tool registered for {category}")
                tool_result = {
                    "status": "no_tool_available",
                    "reason": f"No diagnostic tool registered for category {category}."
                }
            else:
                tool_name = tool_fn.__name__
                risk = "RISKY" if tool_name in RISKY_TOOLS else "SAFE"
                print(f"\nRouting: {category} → {tool_name}() [{risk}]")

                try:
                    tool_result = tool_fn()
                    print(f"\nTool Result:")
                    for key, val in tool_result.items():
                        print(f"  {key}: {val}")
                except Exception as e:
                    log.error(f"Tool execution failed: {e}")
                    tool_result = {
                        "status": "tool_error",
                        "reason": str(e)
                    }
```

Replace it with this updated version that includes the approval gate:

```python
        else:
            tool_fn = TOOL_REGISTRY.get(category)

            if tool_fn is None:
                print(f"\nRouting: no tool registered for {category}")
                tool_result = {
                    "status": "no_tool_available",
                    "reason": f"No diagnostic tool registered for category {category}."
                }
            else:
                tool_name = tool_fn.__name__
                risk = "RISKY" if is_risky(tool_name) else "SAFE"
                print(f"\nRouting: {category} → {tool_name}() [{risk}]")

                # ── APPROVAL GATE ─────────────────────────────────────────
                if is_risky(tool_name):
                    approved = approval_gate(
                        action_name=tool_name,
                        details=(
                            f"About to run {tool_name}() on this system.\n"
                            f"Ticket: {description[:100]}\n"
                            f"Category: {category} (confidence: {confidence})"
                        )
                    )
                    if not approved:
                        print("\nAction declined. No changes made.")
                        tool_result = {
                            "status":  "declined_by_engineer",
                            "reason":  f"Engineer declined to run {tool_name}(). "
                                       f"No system changes made."
                        }
                        # Skip to report generation — don't call the tool
                        pass
                    else:
                        try:
                            tool_result = tool_fn()
                            print(f"\nTool Result:")
                            for key, val in tool_result.items():
                                print(f"  {key}: {val}")
                        except Exception as e:
                            log.error(f"Tool execution failed: {e}")
                            tool_result = {"status": "tool_error", "reason": str(e)}
                else:
                    # SAFE tool — run automatically, no approval needed
                    try:
                        tool_result = tool_fn()
                        print(f"\nTool Result:")
                        for key, val in tool_result.items():
                            print(f"  {key}: {val}")
                    except Exception as e:
                        log.error(f"Tool execution failed: {e}")
                        tool_result = {"status": "tool_error", "reason": str(e)}
```

---

### Step 4 — Test: Risky Action Should Pause, Safe Action Should Run

Create a test script:

```bash
touch projects/automation_support_agent/test_approval_gate.py
code projects/automation_support_agent/test_approval_gate.py
```

```python
"""
Day 15 — Test the approval gate.
Tests both SAFE (auto-run) and RISKY (approval required) paths.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import approval_gate, is_risky, SAFE_ACTIONS, RISKY_ACTIONS

print("\n" + "="*60)
print("APPROVAL GATE — TEST RUN")
print("="*60)

# Test 1 — is_risky() function
print("\n[TEST 1] is_risky() checks")
for tool in SAFE_ACTIONS:
    result = is_risky(tool)
    status = "❌ WRONG" if result else "✅ SAFE"
    print(f"  {status}: is_risky('{tool}') = {result}")

for tool in RISKY_ACTIONS:
    result = is_risky(tool)
    status = "✅ RISKY" if result else "❌ WRONG"
    print(f"  {status}: is_risky('{tool}') = {result}")

# Test 2 — approval_gate() function
print("\n[TEST 2] Live approval gate test")
print("You will be asked to approve or decline a test action.")
print("Type 'yes' to approve or 'no' to decline.\n")

approved = approval_gate(
    action_name="clear_cache",
    details=(
        "About to delete ~/Library/Caches to free 18.2 GB.\n"
        "Ticket: My MacBook disk is 95% full.\n"
        "Category: DISK (confidence: 0.99)"
    )
)

if approved:
    print("\n✅ Test result: Action APPROVED")
    print("   In production: clear_cache_mac.sh would run now")
else:
    print("\n✅ Test result: Action DECLINED")
    print("   In production: no files would be deleted")

print("\n[TEST 3] Full process_ticket() with approval gate")
print("Running a DISK ticket — check_disk_space() is SAFE")
print("It should run automatically without asking for approval.\n")

from app import process_ticket
result = process_ticket("My MacBook Pro says the startup disk is almost full")
print(f"\nFinal status: {result['tool_result'].get('status', 'completed')}")
```

Run it:

```bash
python3 projects/automation_support_agent/test_approval_gate.py
```

---

### Step 5 — The approval_required Field in Report JSON

The `approval_required` field in your Day 13 report already captures
whether approval was needed. Now it reflects the actual gate result:

```python
# In generate_report() prompt — already written on Day 13:
# approval_required: true if recommendation involves a risky action

# The report now has full context:
{
  "recommendation":    "Clear ~/Library/Caches with engineer approval",
  "approval_required": true,
  "approval_reason":   "Cache deletion is destructive — requires confirmation"
}
```

No changes needed to report.py — Day 13 already handles this correctly.

---

## Terminal Commands — Run in Order

```bash
# Step 1 — verify SAFE/RISKY lists in tools.py
grep -A 10 "SAFE_TOOLS" projects/automation_support_agent/tools.py

# Step 2 — add approval_gate() to app.py
code projects/automation_support_agent/app.py

# Step 3 — update process_ticket() routing block
# (replace the tool routing else block as shown above)

# Step 4 — test approval gate
touch projects/automation_support_agent/test_approval_gate.py
code projects/automation_support_agent/test_approval_gate.py
python3 projects/automation_support_agent/test_approval_gate.py

# Run full pipeline — DISK ticket should NOT trigger approval gate
python3 projects/automation_support_agent/app.py

# Commit
git add .
git commit -m "Day 15: approval gate added — human-in-the-loop"
git push
```

---

## Expected Output — test_approval_gate.py

```
============================================================
APPROVAL GATE — TEST RUN
============================================================

[TEST 1] is_risky() checks
  ✅ SAFE: is_risky('check_disk_space') = False
  ✅ SAFE: is_risky('check_os_version') = False
  ✅ SAFE: is_risky('check_running_processes') = False
  ✅ SAFE: is_risky('read_sample_log') = False
  ✅ SAFE: is_risky('check_package_status') = False
  ✅ RISKY: is_risky('clear_cache') = True
  ✅ RISKY: is_risky('reinstall_package') = True
  ✅ RISKY: is_risky('force_reboot') = True
  ✅ RISKY: is_risky('run_cleanup_script') = True

[TEST 2] Live approval gate test
You will be asked to approve or decline a test action.
Type 'yes' to approve or 'no' to decline.

============================================================
[APPROVAL REQUIRED]
============================================================
Action  : clear_cache
Details : About to delete ~/Library/Caches to free 18.2 GB.
          Ticket: My MacBook disk is 95% full.
          Category: DISK (confidence: 0.99)
============================================================
⚠️  This action cannot be undone.

Approve this action? (yes/no): yes

✅ Test result: Action APPROVED
   In production: clear_cache_mac.sh would run now

[TEST 3] Full process_ticket() with approval gate
Running a DISK ticket — check_disk_space() is SAFE
It should run automatically without asking for approval.

────────────────────────────────────────────────────────────
PROCESSING TICKET
────────────────────────────────────────────────────────────
...
Routing: DISK → check_disk_space() [SAFE]

Tool Result:
  volume: Macintosh HD
  free_gb: 25
  critical: True
  ...
```

Notice: **no approval prompt appeared** for the DISK ticket because
`check_disk_space()` is in SAFE_ACTIONS. The gate only fires for
`clear_cache`, `reinstall_package`, `force_reboot`, `run_cleanup_script`.

---

## How Your clear_cache_mac.sh Connects Here

This is the day your script becomes a real part of the pipeline.
When `clear_cache` is in RISKY_ACTIONS and the approval gate approves:

```python
# In tools.py — the real version (for after Day 15)
import subprocess

def clear_cache() -> dict:
    """
    Clear ~/Library/Caches — calls clear_cache_mac.sh.
    RISKY — approval gate required before calling this.
    """
    script = os.path.expanduser(
        "~/Documents/work/learning/enterprise-agentic-ai/clear_cache_mac.sh"
    )
    result = subprocess.run(
        ["bash", script, "--auto", "--target", "caches"],
        capture_output=True, text=True, timeout=60
    )
    return {
        "status":  "success" if result.returncode == 0 else "failed",
        "tool":    "clear_cache_mac.sh",
        "output":  result.stdout[:300],
    }
```

The approval gate you built today is the safety wrapper that makes
this real script call safe to use in an automated agent.

---

## The Two-Tier Safety Model — Summary

```
SAFE tools  →  run automatically
              check_disk_space()         ← read only, no risk
              check_os_version()         ← read only, no risk
              check_running_processes()  ← read only, no risk
              read_sample_log()          ← read only, no risk
              check_package_status()     ← read only, no risk

RISKY tools →  ALWAYS ask first
              clear_cache()              ← deletes files permanently
              reinstall_package()        ← modifies installed software
              force_reboot()             ← interrupts user session
              run_cleanup_script()       ← calls clear_cache_mac.sh
```

---

## What You Can Say in an Interview Right Now

> "Most AI agent demos I have seen just run tools automatically.
> My agent has a two-tier safety model — safe diagnostic tools run
> automatically because they are read-only, but any tool that modifies
> system state requires an explicit human confirmation before executing.
> I designed this based on 20 years of IT support experience where we
> never ran a cleanup script on a user's machine without confirming
> with them first. The approval gate is not a limitation — it is the
> architectural decision that makes this agent safe to deploy in a
> production enterprise environment."

---

## Interview Questions — Day 15

### Q1 — Why should an AI agent never automatically run remediation
scripts without approval?

An automated agent operating at scale can cause irreversible damage
if it acts on a misclassification or incomplete observation. My
classifier achieves 9 out of 10 on test cases — that remaining 10%
represents real tickets where the model is uncertain. If clear_cache()
runs automatically on a misclassified APPLICATION ticket, the agent
could delete cache files for a running application mid-session, causing
data loss. At Oracle EE scale with thousands of endpoints, even a 1%
error rate means dozens of unintended deletions daily. The approval gate
makes the human the final decision-maker for any destructive action. The
agent provides the diagnosis and recommendation — the engineer approves
the execution. This is exactly how we operated in manual support: I
would diagnose, propose the fix, confirm with the user, then act.
The agent does the same thing, just faster.

### Q2 — How did you implement human-in-the-loop in your Automation
Support Agent?

I implemented it as a function called approval_gate() in app.py. It
takes the action name and a details string describing exactly what will
happen — which folder will be cleared, which ticket triggered it, and
what the confidence score was. It prints all of this clearly to the
engineer and waits for an explicit yes or no. The gate is called inside
process_ticket() only when is_risky() returns True for the tool being
proposed. Safe tools bypass the gate entirely and run automatically.
If the engineer says no, the tool_result is set to declined_by_engineer,
the agent still generates a report documenting what it found and what
it would have done, and no system changes are made. The approval_required
field in the JSON report always correctly reflects whether a risky action
was involved — regardless of whether it was approved or declined.

### Q3 — How would you extend the approval gate to use Slack or
email notifications?

The current approval gate uses Python's input() function — it blocks
and waits for keyboard input. Replacing this with Slack or email is
straightforward architecturally because the gate is isolated in one
function. Instead of input(), I would post a Slack message to an IT
support channel with the action details and two buttons — Approve and
Decline — using Slack's Block Kit API. The function would then poll
for the button click response with a timeout — say 30 minutes. If no
response within the timeout, the gate defaults to declined. For email
I would use a similar pattern with a tokenised approval link. This
would also allow the approval to come from a mobile device, which is
important for on-call engineers. The rest of the agent pipeline —
classification, tool routing, report generation — would not change at
all because the gate is a single isolated function.

---

## Expected Outputs by End of Day 15

- [ ] Step 1: SAFE_TOOLS and RISKY_TOOLS verified in tools.py
- [ ] Step 2: approval_gate() and is_risky() added to app.py
- [ ] Step 3: process_ticket() updated with approval gate check
- [ ] Step 4: test_approval_gate.py run — all is_risky() checks pass
- [ ] Step 4: Live gate tested — approved and declined paths both work
- [ ] Step 4: DISK ticket confirmed — runs WITHOUT triggering gate
- [ ] approval_required field correct in all reports
- [ ] Committed and pushed

---

## Git Commit

```bash
git add .
git commit -m "Day 15: approval gate added — human-in-the-loop"
git push
```

---

*Day 15 complete — your agent is now enterprise-safe.*
*It diagnoses automatically, proposes risky actions, and waits*
*for human confirmation before executing anything destructive.*
*Week 2 is complete. Day 16 starts Week 3 — prompt hardening.*
