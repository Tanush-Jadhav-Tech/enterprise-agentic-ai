# Day 02 — Agent Concepts
> Agentic AI Learning Roadmap | Based on: clear_cache_mac.sh (Oracle EE Support Tool)

---

## 2. Agent Loop Flowchart

```
┌─────────────────────────────────┐
│         USER RUNS SCRIPT        │
│  "Mac is slow — low disk space" │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│         OBSERVE (Sense)         │
│  du -sh ~/Library/Caches/       │
│  du -sh ~/.Trash/               │
│  → Shows sizes to user          │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│         APPROVAL GATE           │
│  "Do you want to continue y/n?" │
│  ← Human in the loop            │
└────┬───────────────────────┬────┘
     │ YES                   │ NO
     ▼                       ▼
┌──────────┐          ┌─────────────┐
│  SELECT  │          │  LOG + EXIT │
│  MENU    │          │  No files   │
│  (1–4)   │          │  deleted    │
└────┬─────┘          └─────────────┘
     │
     ▼
┌─────────────────────────────────┐
│           ACT (Tool Call)       │
│  1. sudo rm -rf Caches/*        │
│  2. sudo rm -rf .Trash/*        │
│  3. Both                        │
│  4. Quit                        │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       OBSERVE RESULT            │
│  Files deleted → count logged   │
│  Output → CachesDelete.log      │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     REPORT (Telemetry POST)     │
│  post_duration() →              │
│  HTTP POST → Oracle APEX        │
│  HTTP 200 → INFO log            │
│  HTTP ≠ 200 → WARN log          │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       LOOP OR STOP?             │
│  select menu → REPLY=           │
│  loops back to menu             │
│  Quit → osascript close window  │
└─────────────────────────────────┘
```

---

## 3. Agent Loop Steps → Real IT Support Scenario

**Scenario: MacBook running slow, user can't save files (Caches/Trash full)**

| Agent Loop Step | What the Script Does | Your Real-World Experience |
|---|---|---|
| **Receive Input** | Script launched by user after getting ticket | Ticket raised: "Mac is very slow, cannot save files" |
| **Observe (Pre-Action)** | `du -sh` checks Caches and Trash sizes before any action | You remote in, check Finder → About This Mac → Storage |
| **Think / Plan** | Displays sizes, warns user about permanent deletion | You assess: Caches 18GB + Trash 4GB = clear these first before escalating |
| **Approval Gate** | `read -p "Do you want to continue y/n?"` | You say to user: "I'm going to clear temp files — confirm?" |
| **Act (Tool Call)** | `sudo rm -vrf ~/Library/Caches/*` | You run Disk Cleanup or manually clear ~/Library/Caches |
| **Observe Result** | Pipe to `CachesDelete.log`, count of deleted files shown | You check free space again: 18GB recovered, problem resolved |
| **Report Back** | `post_duration()` → REST POST to Oracle APEX | You update the ticket: "Cleared 18GB caches, disk free space restored to 22GB. Resolved." |
| **Loop / Stop** | `select` menu allows another action or Quit | User says "Also clear Trash?" → you do that too before closing |

---

## 4. Three Message Roles — IT Support Context

### System (The Standing Instructions / SOP)
```
You are an Oracle Enterprise Engineering macOS Support Agent.

Before deleting any files, always:
1. Check and display current Caches and Trash folder sizes.
2. Warn the user that deletion is permanent.
3. Require explicit user confirmation before proceeding.

After each action:
- Log with timestamp and level (INFO / WARN).
- POST telemetry to Oracle APEX with script_id, run_status, and duration.
- If HTTP POST fails, log a WARN with the status code.

Never delete files silently. Always show count of files removed.
```

### User (The Ticket / What the End User Says)
```
My MacBook has been really slow since this morning and I keep getting
a popup saying my disk is almost full. I tried to save a file and it
said there was no space. Can you help me fix this?

-- Ticket INC0048821, raised by john.doe@oracle.com
```

### Assistant (What the Agent Replies)
```
Hi John,

I have checked your MacBook storage. Here is what I found:

  Caches folder : 18 GB
  Trash folder  :  4 GB
  Total to free : 22 GB (approx.)

Warning: Files deleted from Caches and Trash cannot be recovered.

Options:
  1. Clear Caches folder only
  2. Clear Trash folder only
  3. Clear both Caches and Trash
  4. Quit without changes

Please confirm your choice and enter your MacBook password when prompted.

Script ID : 461
Log file   : ~/Library/Logs/clear_cache_mac.txt
```

---

## 5. Temperature — Why Low is Right for IT Agents

> **Low temperature (0.0–0.2) is the correct setting for IT support agents because
> every output — file sizes, deletion counts, HTTP status codes, and log entries —
> must be deterministic, factual, and repeatable; not creative, approximate, or varied.**

### Why This Matters for Your Script

| Output Type | High Temp (bad) | Low Temp (correct) |
|---|---|---|
| Caches size | "Looks like maybe 15–20GB" | `18G /Users/john/Library/Caches` |
| Files deleted | "Most files were removed" | `$(wc -l) files deleted` |
| HTTP status | "Should be fine, network seems ok" | `HTTP 200 — Telemetry POST successful` |
| Log entry | Vague narrative | `[2025-05-21 09:14:32] [INFO] Caches folder cleared` |
| Error message | "Something went wrong maybe" | `[WARN] Telemetry POST failed — HTTP 503. Check VPN.` |

---

## Terminal Commands Run

```bash
touch notes/day02-agent-concepts.md
code notes/day02-agent-concepts.md
```

---

## Agentic Concepts in clear_cache_mac.sh

| Concept | Location in Script |
|---|---|
| **Tool use** | `du`, `rm`, `curl` — tools the agent calls |
| **Observation** | `cacheS=$(du -sh ...)` — reads environment state before acting |
| **Approval gate** | `read -p "Do you want to continue y/n?"` — human-in-the-loop |
| **Structured logging** | `log()` with level + timestamp — agent memory |
| **Telemetry / reporting** | `post_duration()` → Oracle APEX REST POST |
| **Error handling** | HTTP status check — agent detects and logs failure |

---

*Day 02 complete — Oracle EE Support macOS Cache Cleaner as a working agent loop example.*
