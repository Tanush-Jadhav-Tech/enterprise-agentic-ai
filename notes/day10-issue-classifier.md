# Day 10 — Build the Issue Classifier

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Implement the first real component — the issue classifier

---

## Study Resources

- OpenAI Prompt Engineering — Classification tasks:
  https://platform.openai.com/docs/guides/prompt-engineering
- OpenAI Structured Outputs:
  https://platform.openai.com/docs/guides/structured-outputs

---

## Core Concepts

| Concept | Definition |
|---|---|
| Classification | Entry point of every agent — understands what type of problem it is |
| Confidence score | Always return 0.0–1.0 indicating how sure the model is |
| Edge cases | Ambiguous tickets, multiple issues — handle with UNKNOWN |
| Routing | Classifier output feeds routing logic — determines which tool runs next |
| Logging | Always log what the model returns — debug and audit trail |

---

## Step-by-Step Instructions

### Step 1 — Open app.py

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
code projects/automation_support_agent/app.py
```

---

### Step 2 — Implement classify_issue() in app.py

This function takes a free-text ticket description and returns a dict
with category + confidence. This is the brain of your agent.

```python
"""
Automation Support Agent — Orchestration Layer
Classifies IT support tickets, routes to diagnostic tools,
generates structured support reports with human approval gate.
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

CATEGORIES = ["DISK", "UPGRADE", "PACKAGING", "APPLICATION", "NETWORK", "UNKNOWN"]

MODELS = [
    "openrouter/auto",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

def safe_parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    # Step 1: strip markdown fences
    clean = re.sub(r"```(?:json)?", "", text).strip()
    clean = clean.strip("`").strip()

    # Step 2: try direct parse
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Step 3: extract JSON object using regex
    match = re.search(r'\{.*?\}', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Step 4: manually extract fields as last resort
    cat_match  = re.search(r'"category"\s*:\s*"([^"]+)"', clean)
    conf_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', clean)
    reas_match = re.search(r'"reason"\s*:\s*"([^"]+)"', clean)

    if cat_match:
        return {
            "category":   cat_match.group(1),
            "confidence": float(conf_match.group(1)) if conf_match else 0.5,
            "reason":     reas_match.group(1) if reas_match else "extracted from partial response"
        }

    log.error(f"JSON parse failed completely | raw: [{text}]")
    return {"category": "UNKNOWN", "confidence": 0.0, "reason": "JSON parse error"}

def call_llm(messages: list, temperature: float = 0) -> str:
    """Call LLM with model fallback on rate limit."""
    for model in MODELS:
        try:
            log.info(f"Calling model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=500,
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

def classify_issue(description: str) -> dict:
    """
    Classify a support ticket into one of the defined categories.
    Args:
        description: Free-text ticket description
    Returns:
        dict with keys: category, confidence, reason
    """
    prompt = f"""You are an IT support classifier for Oracle Enterprise Engineering.

Classify the following support ticket into exactly one category.

Categories: {', '.join(CATEGORIES)}

Rules:
- Reply ONLY with valid JSON — no explanation, no markdown
- Use UNKNOWN if the ticket is too vague or ambiguous
- confidence must be between 0.0 and 1.0
- reason must be one sentence

Format:
{{"category": "DISK", "confidence": 0.95, "reason": "one line explanation"}}

Ticket: {description}"""

    raw = call_llm([{"role": "user", "content": prompt}], temperature=0)
    result = safe_parse_json(raw)

    if result.get("category") not in CATEGORIES:
        log.warning(f"Invalid category: {result.get('category')} — defaulting to UNKNOWN")
        result["category"] = "UNKNOWN"
        result["confidence"] = 0.0

    log.info(f"Classified: {result['category']} ({result['confidence']})")
    return result

if __name__ == "__main__":

    test_cases = [
        "My Mac says the startup disk is almost full",
        "Citrix Workspace crashes immediately on launch",
        "The macOS Sonoma upgrade is stuck at 75%",
        "Company VPN package fails — notarization error",
        "Cannot connect to corporate VPN from home network",
        "clear_cache_mac.sh fails with permission denied on Trash",
        "My laptop is slow",
        "My computer is hot",
        "Error code 11001",
        "Everything is broken",
    ]

    print("\n" + "="*60)
    print("ISSUE CLASSIFIER — TEST RUN")
    print("="*60)

    results = []
    for i, tc in enumerate(test_cases, 1):
        print(f"\n[{i:02d}] Ticket    : {tc}")
        result = classify_issue(tc)
        print(f"     Category  : {result['category']}")
        print(f"     Confidence: {result['confidence']}")
        print(f"     Reason    : {result['reason']}")
        results.append({"ticket": tc, **result})
        time.sleep(2)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in results:
        flag = "⚠️ " if r['confidence'] < 0.75 else "✅"
        print(f"{flag} {r['category']:15} ({r['confidence']}) — {r['ticket'][:45]}")


---

### Step 3 — Test with 10 Sample Inputs

Add this test block at the bottom of app.py:

```python
# ── Step 3: Test classify_issue() with 10 samples ────────────────────────────
if __name__ == "__main__":

    test_cases = [
        # Clear cases — should classify with high confidence
        "My Mac says the startup disk is almost full",
        "Citrix Workspace crashes immediately on launch",
        "The macOS Sonoma upgrade is stuck at 75%",
        "Company VPN package fails — notarization error",
        "Cannot connect to corporate VPN from home network",

        # Your own script scenario
        "clear_cache_mac.sh fails with permission denied on Trash",

        # Edge cases — ambiguous or vague
        "My laptop is slow",           # ambiguous — could be DISK or APPLICATION
        "My computer is hot",          # ambiguous — could be APPLICATION or DISK
        "Error code 11001",            # no context — should return UNKNOWN
        "Everything is broken",        # vague — should escalate to UNKNOWN
    ]

    print("\n" + "="*60)
    print("ISSUE CLASSIFIER — TEST RUN")
    print("="*60)

    results = []
    for i, tc in enumerate(test_cases, 1):
        print(f"\n[{i:02d}] Ticket  : {tc}")
        result = classify_issue(tc)
        print(f"     Category: {result['category']}")
        print(f"     Confidence: {result['confidence']}")
        print(f"     Reason  : {result['reason']}")
        results.append({"ticket": tc, **result})
        time.sleep(2)  # avoid rate limiting on free tier

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for r in results:
        flag = "⚠️ " if r['confidence'] < 0.75 else "✅"
        print(f"{flag} {r['category']:15} ({r['confidence']}) — {r['ticket'][:50]}")
```

---

### Step 4 — Add Logging

Logging is already included in the code above using Python's built-in
`logging` module. Every call logs:
- Which model was used
- How many tokens were consumed
- What category was returned
- Any rate limit warnings or JSON errors

This is your audit trail — same discipline as your Oracle EE script logs.

---

### Step 5 — Write Failing Test Cases in eval_cases.md

Open eval_cases.md and add Actual Category + Pass/Fail after running:

```bash
code projects/automation_support_agent/eval_cases.md
```

Fill in the Actual Category column after running the test:

```markdown
| # | Ticket | Expected | Actual | Confidence | Pass? | Notes |
|---|---|---|---|---|---|---|
| 1  | startup disk almost full       | DISK        | ?  | ? | - | |
| 2  | Citrix crashes on launch        | APPLICATION | ?  | ? | - | |
| 3  | macOS upgrade stuck at 75%      | UPGRADE     | ?  | ? | - | |
| 4  | VPN notarization failed         | PACKAGING   | ?  | ? | - | |
| 5  | Cannot connect to VPN           | NETWORK     | ?  | ? | - | |
| 6  | clear_cache_mac.sh perm denied  | APPLICATION | ?  | ? | - | |
| 7  | My laptop is slow               | DISK        | ?  | ? | - | Low conf expected |
| 8  | My computer is hot              | UNKNOWN     | ?  | ? | - | Ambiguous |
| 9  | Error code 11001                | UNKNOWN     | ?  | ? | - | No context |
| 10 | Everything is broken            | UNKNOWN     | ?  | ? | - | Vague |
```

---

## Terminal Commands — Run in Order

```bash
# Open app.py
code projects/automation_support_agent/app.py

# Run the classifier
python3 projects/automation_support_agent/app.py

# Commit working classifier
git add .
git commit -m "Day 10: issue classifier working"
git push
```

---

## Expected Output When You Run

```
============================================================
ISSUE CLASSIFIER — TEST RUN
============================================================

[01] Ticket  : My Mac says the startup disk is almost full
     Category: DISK
     Confidence: 0.99
     Reason  : User explicitly reports startup disk is almost full

[02] Ticket  : Citrix Workspace crashes immediately on launch
     Category: APPLICATION
     Confidence: 0.95
     Reason  : Citrix Workspace is an application crashing on launch

[03] Ticket  : The macOS Sonoma upgrade is stuck at 75%
     Category: UPGRADE
     Confidence: 0.99
     Reason  : User explicitly mentions macOS upgrade being stuck

...

[09] Ticket  : Error code 11001
     Category: UNKNOWN
     Confidence: 0.30
     Reason  : No context to classify this error code

[10] Ticket  : Everything is broken
     Category: UNKNOWN
     Confidence: 0.20
     Reason  : Too vague to classify with confidence

============================================================
SUMMARY
============================================================
✅ DISK            (0.99) — My Mac says the startup disk is almost full
✅ APPLICATION     (0.95) — Citrix Workspace crashes immediately on launch
✅ UPGRADE         (0.99) — The macOS Sonoma upgrade is stuck at 75%
✅ PACKAGING       (0.90) — Company VPN package fails — notarization error
✅ NETWORK         (0.88) — Cannot connect to corporate VPN from home
✅ APPLICATION     (0.85) — clear_cache_mac.sh fails with permission denied
⚠️  DISK           (0.70) — My laptop is slow
⚠️  UNKNOWN        (0.40) — My computer is hot
⚠️  UNKNOWN        (0.30) — Error code 11001
⚠️  UNKNOWN        (0.20) — Everything is broken
```

---

## What the Summary Tells You

| Symbol | Meaning | Action on Day 12 |
|---|---|---|
| ✅ | Confidence >= 0.75 — auto-route to tool | Route automatically |
| ⚠️  | Confidence < 0.75 — low confidence | Route to human review |

---

## Interview Questions — Day 10

### Q1 — How does your classifier handle ambiguous or multi-issue tickets?

My classifier handles ambiguity in two ways. First, the prompt explicitly
includes UNKNOWN as a valid category with the instruction to use it when
the ticket is too vague or ambiguous. Second, every response includes a
confidence score — a number between 0 and 1 indicating certainty. Tickets
like "my laptop is slow" return lower confidence (around 0.70) even when
a category is assigned, because the model correctly identifies that multiple
causes are possible. In my routing logic on Day 12, any ticket with
confidence below 0.60 is automatically sent to human review rather than
auto-running a diagnostic tool. This prevents the agent from taking action
on uncertain classifications — which is especially important in enterprise
environments where wrong actions can cause disruption.

### Q2 — Why do you return a confidence score alongside the category?

Because classification is never binary in real IT support. A ticket saying
"my Mac is slow" could be DISK, APPLICATION, or NETWORK depending on
context. The confidence score tells the routing logic how certain the model
is. High confidence (>= 0.75) means auto-route to the tool. Medium
confidence (0.60–0.74) means route but flag for human review. Low
confidence (< 0.60) means skip the tool and escalate to a human. Without
the confidence score I would have to treat every classification as certain,
which would lead to wrong tool calls on ambiguous tickets. In my Day 4
testing I saw "my laptop is slow" return 0.70 confidence — that is exactly
right. The model is saying "probably DISK but I am not sure" — and my
routing logic respects that uncertainty.

### Q3 — What happens if the model returns malformed JSON?

I have a safe_parse_json() function in app.py that handles this. It strips
markdown code fences first — free models often wrap JSON in triple backticks.
Then it attempts to parse. If parsing fails it logs the error with the raw
response for debugging and returns a safe default: category UNKNOWN,
confidence 0.0, reason "JSON parse error". This means the agent never
crashes on a bad model response — it degrades gracefully to human review.
I learned on Day 4 that free models frequently wrap output in markdown
fences so stripping them is not optional — it is a production requirement.

---

## Key Patterns Introduced Today

| Pattern | Where | Why |
|---|---|---|
| safe_parse_json() | app.py | Free models wrap JSON in markdown — always strip |
| call_llm() with fallback | app.py | Rate limits on free tier — try next model |
| temperature=0 | classifier | Deterministic — same ticket always same category |
| logging | every function | Audit trail — same as your Oracle EE script logs |
| time.sleep(2) | test loop | Respect free tier rate limits |

---

## Expected Outputs by End of Day 10

- [ ] Step 1: app.py opened
- [ ] Step 2: classify_issue() implemented with safe_parse_json() and call_llm()
- [ ] Step 3: 10 test cases run — results printed to terminal
- [ ] Step 4: logging confirmed — timestamps and token counts visible
- [ ] Step 5: eval_cases.md updated with actual results
- [ ] Git committed and pushed

---

## Git Commit

```bash
git add .
git commit -m "Day 10: issue classifier working"
git push
```

---

*Day 10 complete — classifier is the brain of your agent.
Day 11 builds the tools the brain will call.*
