# Day 05 — The Agent Loop: Understand & Map

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Based on: HuggingFace Agents Course Unit 1 — Tools

---

## Study Resource Completed

- HuggingFace Agents Course Unit 1: Tools
  https://huggingface.co/learn/agents-course/en/unit1/tools
- HuggingFace Agents Course Unit 1: Agent Loop
  https://huggingface.co/learn/agents-course/en/unit1/agent-steps-and-structure

---

## 1. Agent vs Script — Key Difference

| | Script | Agent |
|---|---|---|
| Path | Fixed — same steps every time | Dynamic — decided by observations |
| Example | clear_cache_mac.sh always shows menu | Agent picks tool based on ticket category |
| Intelligence | None — executes regardless of findings | Reasons over each result before next step |
| Use case | Simple repeatable tasks | Diagnosis and decision-making |

> My clear_cache_mac.sh is a workflow — it always checks Caches,
> always shows the menu, always clears what you pick.
> My agent will use that script as a TOOL — calling it only when
> the classifier returns DISK and only after the approval gate confirms.

---

## 2. ReAct-Style Trace — High CPU Usage on MacBook

**Scenario:** User reports high CPU usage on their MacBook

```
# INPUT
Ticket: "My MacBook is extremely slow. Fan is loud. Cannot work."

# THOUGHT 1 — agent reasons before acting
Thought: User reports high CPU and fan noise. This could be APPLICATION
or DISK. I need to check which process is consuming CPU before making
any recommendation. I should call check_running_processes() first.

# ACTION 1 — agent calls a safe tool
Action: check_running_processes()

# OBSERVATION 1 — agent reads the result
Observation: {
  "top_processes": [
    {"pid": 5678, "name": "Citrix Workspace", "cpu_pct": 88.1},
    {"pid": 1234, "name": "kernel_task",      "cpu_pct": 8.2},
    {"pid": 9012, "name": "mds_stores",       "cpu_pct": 4.1}
  ],
  "total_cpu_usage_pct": 96.3,
  "sampled_at": "2024-01-15T10:22:00"
}

# THOUGHT 2 — agent reasons over the observation
Thought: Citrix Workspace is consuming 88.1% CPU. This is an APPLICATION
issue — not DISK. Root cause is likely a Citrix process hang or memory
leak. The safe first step is to check for a Citrix update. Force-quitting
a process is a risky action and requires human approval before execution.

# ACTION 2 — agent requests approval before risky action
Action: approval_gate(
  action="force_quit_citrix",
  details="Citrix Workspace PID 5678 using 88.1% CPU. Propose force quit
           and relaunch. User will lose any unsaved Citrix session data."
)

# OBSERVATION 2 — human engineer responds
Observation: {"approved": true, "approved_by": "engineer@oracle.com"}

# ACTION 3 — agent executes approved risky action
Action: force_quit_process(pid=5678)

# OBSERVATION 3 — result confirmed
Observation: {
  "status": "success",
  "pid_terminated": 5678,
  "cpu_after": 12.4,
  "duration_seconds": 2
}

# THOUGHT 3 — agent confirms resolution
Thought: CPU dropped from 96.3% to 12.4% after force-quitting Citrix.
Issue is resolved. I can now generate the structured support summary.

# FINAL OUTPUT — structured report
Final: {
  "category": "APPLICATION",
  "confidence": 0.95,
  "root_cause": "Citrix Workspace process hang — PID 5678",
  "tools_invoked": ["check_running_processes", "approval_gate",
                    "force_quit_process"],
  "action_taken": "Force quit PID 5678 with engineer approval",
  "cpu_before": 96.3,
  "cpu_after": 12.4,
  "approval_required": true,
  "approved_by": "engineer@oracle.com",
  "resolution": "RESOLVED",
  "summary": "Citrix Workspace process hang causing 96% CPU resolved
              by approved force quit. CPU restored to 12.4%."
}
```

---

## 3. Agent Flow Diagram

```
                    ┌─────────────────────┐
                    │       INPUT         │
                    │  Support ticket     │
                    │  "High CPU on Mac"  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     CLASSIFIER      │
                    │  classify_issue()   │
                    │  → APPLICATION 0.95 │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     TOOL CALL       │
                    │ check_running_      │
                    │ processes()         │
                    │ [SAFE — auto-run]   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    TOOL RESULT      │
                    │ Citrix: 88.1% CPU   │
                    │ kernel_task: 8.2%   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   APPROVAL GATE     │◄── Engineer confirms
                    │ force_quit_citrix   │
                    │ [RISKY — approval]  │
                    └──────────┬──────────┘
                               │ approved
                               ▼
                    ┌─────────────────────┐
                    │    SUMMARISER       │
                    │  generate_report()  │
                    │  LLM interprets     │
                    │  evidence → JSON    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      OUTPUT         │
                    │  Structured JSON    │
                    │  report → ticket    │
                    │  system update      │
                    └─────────────────────┘
```

---

## 4. Five Tools for Automation Support Agent

| # | Tool | Type | What it does |
|---|---|---|---|
| 1 | `check_disk_space()` | SAFE | Reads Caches, Trash, free space — wraps clear_cache_mac.sh in read-only mode |
| 2 | `check_running_processes()` | SAFE | Lists top CPU consumers from Activity Monitor |
| 3 | `check_os_version()` | SAFE | Returns current macOS version and pending updates |
| 4 | `read_log_file(path)` | SAFE | Reads last N lines of a log, returns error count and patterns |
| 5 | `clear_cache()` | RISKY | Calls clear_cache_mac.sh --auto — deletes files, needs approval gate |

**Routing registry:**
```python
TOOL_REGISTRY = {
    "DISK":        check_disk_space,
    "APPLICATION": check_running_processes,
    "UPGRADE":     check_os_version,
    "PACKAGING":   check_os_version,
    "NETWORK":     check_running_processes,
}

SAFE_TOOLS  = ["check_disk_space", "check_running_processes",
               "check_os_version", "read_log_file"]

RISKY_TOOLS = ["clear_cache", "force_quit_process",
               "reinstall_package", "run_cleanup_script"]
```

---

## 5. Why an Enterprise AI Agent Must Never Run a Cleanup Script Without Approval

An enterprise AI agent must never run a cleanup script, delete files,
force-quit processes, reinstall packages, or trigger any system-modifying
action without explicit human confirmation. The reason is simple: automated
systems operating at scale can cause irreversible damage if they act on
incorrect classifications or incomplete observations. A false positive —
the agent misclassifying an APPLICATION issue as DISK — could result in
cached data for a running application being deleted mid-session, causing
data loss or corruption. In a large enterprise like Oracle EE with thousands
of managed endpoints, even a 1% misclassification rate at scale means dozens
of unintended deletions per day. The approval gate is not a limitation on
the agent's capability — it is the architectural feature that makes the agent
safe to deploy in a production environment. Every risky action in my
Automation Support Agent is gated behind a confirmation prompt that shows
the engineer exactly what will be executed, on which machine, and why —
before a single command runs. Safe read-only tools like check_disk_space()
and read_log_file() run automatically. Only destructive write actions
require the gate. This two-tier model delivers the speed of automation
for diagnostics and the safety of human oversight for remediation.

---

## Interview Questions — Day 5

### Q1 — What is the ReAct pattern and why is it useful?

ReAct stands for Reason + Act. Before taking any action the agent writes
out its reasoning — what it found, what it thinks the cause is, and what
it plans to do next. This is useful for two reasons. First it makes the
agent's behaviour explainable — you can read the thought trace and see
exactly why it called a particular tool. Second it improves accuracy —
forcing the model to articulate its reasoning before acting reduces
hallucination and prevents premature actions. In my high CPU trace, the
agent wrote "Citrix Workspace is consuming 88% CPU — approval required
before force quit" before calling the approval gate. That reasoning step
is what caught the need for approval rather than acting immediately.

### Q2 — What is the difference between an agent and a workflow?

A workflow follows a fixed sequence of steps regardless of what is found.
My clear_cache_mac.sh is a workflow — it always checks Caches, always
shows the menu. An agent decides its next step based on what it observed.
A DISK ticket calls the disk tool. An APPLICATION ticket calls the process
tool. An UNKNOWN ticket routes to human review. The path is dynamic, not
fixed. In enterprise support you want both — workflows for simple
repeatable tasks, agents for tasks requiring diagnosis and decision-making.

### Q3 — Why do enterprise AI agents need human approval gates?

Because agents can be wrong, and some actions are irreversible. A classifier
returning 0.70 confidence means 30% uncertainty — too high to auto-delete
files. An approval gate pauses the agent before any destructive action,
shows the engineer exactly what will be executed and why, and waits for an
explicit yes before proceeding. In my agent, SAFE tools run automatically.
RISKY tools — clear_cache, force_quit, reinstall_package — always go through
the approval gate. An enterprise agent without approval gates is not
production-ready. It is a liability.

---

## Terminal Commands Run

```bash
touch notes/day05-agent-loop.md
code notes/day05-agent-loop.md
```

---

## Key Concepts Summary

| Concept | Definition |
|---|---|
| ReAct | Reason + Act — agent thinks before every action |
| Tool | External function agent calls to get real data |
| Approval gate | Human confirmation required before risky action |
| Stopping condition | Goal met / user quits / max iterations hit |
| SAFE tool | Read-only — auto-run allowed |
| RISKY tool | Modifies system state — always needs approval |

---

*Day 05 complete — ReAct trace, flow diagram, tool list, approval gate documented.*
