# Day 12 — Connect Classifier to Tools: First End-to-End Run

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Wire classifier output to tool layer. Run first complete
> support ticket through the system end-to-end.

---

## Study Resources

- OpenAI Agents SDK — Running Agents:
  https://openai.github.io/openai-agents-python/running_agents/

---

## Core Concepts

| Concept | Definition |
|---|---|
| Routing logic | Use classifier category as key to look up TOOL_REGISTRY |
| Error handling | Classifier might return UNKNOWN or invalid JSON — handle both |
| End-to-end trace | Print each step so you can see the agent "thinking" |
| Most important day | Getting end-to-end flow right is the foundation for everything after |

---

## Why Today Matters Most

```
Day 10  →  Classifier (brain)        — works alone
Day 11  →  Tools (hands)             — work alone
Day 12  →  Brain + Hands connected   — first real agent
```

Until today you had two separate working pieces.
Today they become one system. This is the moment your
project becomes an actual agent rather than two scripts.

---

## Step-by-Step Instructions

### Step 1 — Open app.py

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
code projects/automation_support_agent/app.py
```

---

### Step 2 — Add process_ticket() Function

Add this import at the top of app.py (after existing imports):

```python
from tools import TOOL_REGISTRY, SAFE_TOOLS, RISKY_TOOLS
```

> Note: if tools.py is in the same folder, this relative import works
> when running from inside projects/automation_support_agent/.
> If running from project root, use:
> from projects.automation_support_agent.tools import TOOL_REGISTRY, SAFE_TOOLS, RISKY_TOOLS

Add this function after `classify_issue()`:

```python
# ── Step 2: process_ticket() — connects classifier to tools ──────────────────

CONFIDENCE_THRESHOLD = 0.60

def process_ticket(description: str) -> dict:
    """
    Process a support ticket end-to-end:
    classify → route → call tool → return combined result.

    Args:
        description: Free-text ticket description

    Returns:
        dict with keys: ticket, classification, tool_result
    """
    print(f"\n{'─'*60}")
    print(f"PROCESSING TICKET")
    print(f"{'─'*60}")
    print(f"Input: {description}")

    # Step 1: Classify
    classification = classify_issue(description)
    category   = classification.get("category", "UNKNOWN")
    confidence = classification.get("confidence", 0.0)

    print(f"\nClassification:")
    print(f"  Category   : {category}")
    print(f"  Confidence : {confidence}")
    print(f"  Reason     : {classification.get('reason', 'N/A')}")

    # Step 2: Route to tool based on category + confidence
    if category == "UNKNOWN":
        print(f"\nRouting: UNKNOWN category — no tool called")
        tool_result = {
            "status": "needs_human_review",
            "reason": "Category could not be determined. Ticket requires manual triage."
        }

    elif confidence < CONFIDENCE_THRESHOLD:
        print(f"\nRouting: confidence {confidence} below threshold {CONFIDENCE_THRESHOLD}")
        tool_result = {
            "status": "needs_human_review",
            "reason": f"Confidence {confidence} too low for automated routing. "
                      f"Classified as {category} but flagged for review."
        }

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

    print(f"{'─'*60}\n")

    return {
        "ticket":         description,
        "classification": classification,
        "tool_result":    tool_result,
    }
```

---

### Step 3 — Test with 5 Different Ticket Types

Replace the existing `if __name__ == "__main__":` block with this:

```python
if __name__ == "__main__":

    tickets = [
        # DISK — clear classification, SAFE tool
        "My MacBook Pro says the startup disk is almost full",

        # APPLICATION — clear classification, SAFE tool
        "Citrix Workspace crashes immediately on launch",

        # UPGRADE — clear classification, SAFE tool
        "macOS Sonoma upgrade is stuck at 75%",

        # PACKAGING — clear classification, SAFE tool
        "VPN package installation fails with notarization error",

        # UNKNOWN — low confidence, human review
        "My computer feels slow today",
    ]

    print("\n" + "="*60)
    print("AUTOMATION SUPPORT AGENT — END-TO-END TEST")
    print("="*60)

    all_results = []
    for ticket in tickets:
        result = process_ticket(ticket)
        all_results.append(result)
        time.sleep(2)  # respect free tier rate limits

    print("\n" + "="*60)
    print("END-TO-END SUMMARY")
    print("="*60)
    for r in all_results:
        cat    = r["classification"]["category"]
        conf   = r["classification"]["confidence"]
        status = r["tool_result"].get("status", "completed")
        print(f"  {cat:12} ({conf:.2f}) → {status:20} | {r['ticket'][:40]}")

    print(f"\nFinal result keys: {list(all_results[0].keys())}")
```

---

### Step 4 — Handle UNKNOWN Category Gracefully

This is already built into `process_ticket()` above. The function has
**three distinct paths**:

```
                    ┌─────────────────┐
                    │  Classification  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        category ==    confidence <    category in
        "UNKNOWN"      THRESHOLD       TOOL_REGISTRY
              │              │              │
              ▼              ▼              ▼
        no tool call   no tool call    tool_fn()
        human review   human review    called
```

No path crashes. No path calls a tool on uncertain data.

---

### Step 5 — Commit Working End-to-End Flow

```bash
git add .
git commit -m "Day 12: end-to-end classifier-to-tool flow"
git push
```

---

## Terminal Commands — Run in Order

```bash
code projects/automation_support_agent/app.py

# paste process_ticket() + updated __main__ block, save

python3 projects/automation_support_agent/app.py

git add .
git commit -m "Day 12: end-to-end classifier-to-tool flow"
git push
```

---

## Expected Output

```
============================================================
AUTOMATION SUPPORT AGENT — END-TO-END TEST
============================================================

────────────────────────────────────────────────────────────
PROCESSING TICKET
────────────────────────────────────────────────────────────
Input: My MacBook Pro says the startup disk is almost full

Classification:
  Category   : DISK
  Confidence : 0.99
  Reason     : User explicitly reports startup disk is almost full

Routing: DISK → check_disk_space() [SAFE]

Tool Result:
  volume: Macintosh HD
  total_gb: 512
  used_gb: 487
  free_gb: 25
  percent_used: 95.1
  critical: True
  top_consumers: [...]
  checked_at: 2026-06-12T...
────────────────────────────────────────────────────────────


────────────────────────────────────────────────────────────
PROCESSING TICKET
────────────────────────────────────────────────────────────
Input: My computer feels slow today

Classification:
  Category   : UNKNOWN
  Confidence : 0.4
  Reason     : Too vague to classify with confidence

Routing: UNKNOWN category — no tool called
────────────────────────────────────────────────────────────


============================================================
END-TO-END SUMMARY
============================================================
  DISK         (0.99) → completed            | My MacBook Pro says the startup disk
  APPLICATION  (0.95) → completed            | Citrix Workspace crashes immediately
  UPGRADE      (0.98) → completed            | macOS Sonoma upgrade is stuck at 75%
  PACKAGING    (0.90) → completed            | VPN package installation fails with
  UNKNOWN      (0.40) → needs_human_review   | My computer feels slow today

Final result keys: ['ticket', 'classification', 'tool_result']
```

---

## The Three Routing Paths — Decision Table

| Condition | Path | Tool Called? | Output status |
|---|---|---|---|
| `category == "UNKNOWN"` | Path A | No | `needs_human_review` |
| `confidence < 0.60` | Path B | No | `needs_human_review` |
| `category` valid + `confidence >= 0.60` | Path C | Yes | tool's own status |

This decision table is your routing logic — the same logic you wrote
into requirements.md on Day 9, Step 5 acceptance criteria. Today you
implemented exactly what you specified.

---

## How This Maps to the ReAct Trace from Day 5

Compare today's output to your Day 5 ReAct trace:

| Day 5 ReAct concept | Day 12 implementation |
|---|---|
| Thought: "I need to check X before acting" | `classify_issue()` runs first |
| Action: tool call | `tool_fn()` called via TOOL_REGISTRY |
| Observation: tool result | `tool_result` dict printed |
| Thought: "confidence too low, escalate" | confidence < 0.60 → human review path |

You designed this flow conceptually on Day 5. Today you implemented it.

---

## What If You Get an Import Error?

If `from tools import TOOL_REGISTRY` fails with `ModuleNotFoundError`:

**Option 1 — run from inside the project folder:**
```bash
cd projects/automation_support_agent
python3 app.py
cd ../..
```

**Option 2 — use absolute import with sys.path:**
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools import TOOL_REGISTRY, SAFE_TOOLS, RISKY_TOOLS
```

Add this near the top of app.py, before the tools import.

---

## Interview Questions — Day 12

### Q1 — Walk me through what happens when a ticket enters your
Automation Support Agent.

A ticket enters process_ticket() as a free-text string. First it goes
to classify_issue() which calls the LLM with temperature=0 and returns
a category, confidence score, and reason — using my safe_parse_json()
4-layer defensive parser from Day 10. Then process_ticket() checks two
conditions in order. If the category is UNKNOWN, no tool is called and
the ticket goes to human review. If confidence is below 0.60, same thing
— even if a category was assigned, low confidence means the agent does
not trust its own classification enough to act. If both checks pass,
TOOL_REGISTRY looks up the category and calls the matching diagnostic
tool — for example DISK maps to check_disk_space(). The tool returns a
structured dict which becomes evidence for the report generator I build
on Day 13. Every step prints to console so the entire decision trail is
visible — this is the ReAct pattern from Day 5 made real in code.

### Q2 — How do you handle low-confidence classifications?

I set a CONFIDENCE_THRESHOLD constant at 0.60. In process_ticket(), after
classification, I check if confidence is below this threshold before
calling any tool. If it is, the ticket is routed to needs_human_review
with a reason explaining why — including what category the model guessed
and what the actual confidence was. This is important because a low
confidence classification calling the wrong tool wastes a tool call and
could even retrieve misleading evidence. For example if "my laptop is
slow" gets classified as DISK with confidence 0.55, I would rather a
human engineer look at it than have the agent confidently check disk
space when the real issue might be a runaway process. The threshold of
0.60 is configurable — in production I would tune this based on real
eval data from Day 17.

### Q3 — What would you change if you needed to support 20 issue
categories instead of 5?

The architecture already scales to this with minimal changes. TOOL_REGISTRY
is a dictionary — adding a new category means adding one new key-value
pair, not rewriting routing logic. The CATEGORIES list in the classifier
prompt would grow to 20 items — I would need to verify the classifier
still distinguishes between similar categories accurately, which means
more eval cases on Day 17. I would also consider whether some categories
share the same diagnostic tool — for example NETWORK and APPLICATION
both currently map to check_running_processes(), so adding categories
like NETWORK_VPN and NETWORK_WIFI might still share a tool but with
different parameters. The one thing that would need real engineering
work is the confidence threshold — with 20 categories, some pairs may be
harder to distinguish, so I might need per-category thresholds rather
than one global 0.60 value. The core process_ticket() flow — classify,
check confidence, route, call tool, return — does not change.

---

## Expected Outputs by End of Day 12

- [ ] Step 1: app.py opened
- [ ] Step 2: process_ticket() implemented with TOOL_REGISTRY import
- [ ] Step 3: 5 tickets tested — all paths exercised (DISK, APPLICATION,
      UPGRADE, PACKAGING, UNKNOWN)
- [ ] Step 4: UNKNOWN handled gracefully — confirmed in output
- [ ] Step 5: committed and pushed

---

## Git Commit

```bash
git add .
git commit -m "Day 12: end-to-end classifier-to-tool flow"
git push
```

---

*Day 12 complete — your agent is now a real agent. Classifier (brain)
and tools (hands) are connected. Day 13 adds the report generator —
the LLM interprets tool evidence into a structured support summary.*
