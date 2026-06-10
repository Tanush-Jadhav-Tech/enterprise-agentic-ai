# Day 08 — Choose Framework & Create Project Skeleton

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> Goal: Compare frameworks, choose OpenAI Agents SDK, create full project structure

---

## Study Resources

- OpenAI Agents SDK Overview — https://openai.github.io/openai-agents-python/
- OpenAI Agents SDK Quickstart — https://openai.github.io/openai-agents-python/quickstart/
- smolagents Documentation — https://huggingface.co/docs/smolagents/index

---

## Core Concepts

| Concept | Definition |
|---|---|
| OpenAI Agents SDK | Purpose-built for OpenAI models, clean Python API, built-in tracing, approval gates |
| smolagents | Model-agnostic, lightweight, good for learning — less enterprise-ready |
| Project structure | app.py (orchestration), tools.py (tools), prompts.py (prompts), report.py (output) |
| Why structure matters | Separates concerns — each file has one job, each part is testable independently |

---

## Framework Comparison — OpenAI Agents SDK vs smolagents

| Feature | OpenAI Agents SDK | smolagents |
|---|---|---|
| Model support | OpenAI models optimised | Any model — model-agnostic |
| Guardrails | Built-in approval gates | Manual implementation |
| Tool definition | Clean decorator pattern | Simple function wrapping |
| Tracing | Built-in debug tracing | Limited |
| Enterprise-ready | Yes | Learning/prototype only |
| Our use | Main framework | Reference only |

> Why OpenAI Agents SDK for this project: better guardrails support,
> cleaner tool definition, production-closer. smolagents is great for
> learning concepts but lacks the enterprise safety features we need.

---

## Terminal Commands — Run in Order

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
source .venv/bin/activate

# Install framework
pip install openai-agents
pip freeze > requirements.txt

# Create full project skeleton
mkdir -p projects/automation_support_agent/sample_data

touch projects/automation_support_agent/app.py
touch projects/automation_support_agent/tools.py
touch projects/automation_support_agent/prompts.py
touch projects/automation_support_agent/report.py
touch projects/automation_support_agent/requirements.md
touch projects/automation_support_agent/README.md
touch projects/automation_support_agent/eval_cases.md

# Commit skeleton
git add .
git commit -m "Day 8: project skeleton for Automation Support Agent"
git push
```

---

## Project Skeleton — File Structure

```
enterprise-agentic-ai/
├── projects/
│   ├── automation_support_agent/
│   │   ├── app.py              ← orchestration — main agent loop
│   │   ├── tools.py            ← all tool functions
│   │   ├── prompts.py          ← all prompt strings
│   │   ├── report.py           ← structured JSON report generation
│   │   ├── requirements.md     ← MVP specification
│   │   ├── README.md           ← project documentation
│   │   ├── eval_cases.md       ← test cases with expected outputs
│   │   └── sample_data/        ← realistic IT support sample files
│   ├── chatbot/
│   │   └── chatbot.py
│   └── playground/
│       ├── simple_completion.py
│       ├── classify_issue.py
│       └── summarize_log.py
├── notes/
│   ├── day01-foundations.md
│   ├── day02-agent-concepts.md
│   ├── day03-prompts.md
│   ├── day04-api-calls.md
│   ├── day04-interview-answers.md
│   ├── day05-agent-loop.md
│   ├── day06-chatbot.md
│   └── week1-review.md
├── .env                        ← never committed
├── .gitignore
├── requirements.txt
└── README.md
```

---

## First Line of Each File — Add These Docstrings

### app.py
```python
"""
Automation Support Agent — Orchestration Layer
Classifies IT support tickets, routes to diagnostic tools,
generates structured support reports with human approval gate.
Oracle Enterprise Engineering — Agentic AI Portfolio Project
"""
```

### tools.py
```python
"""
Automation Support Agent — Diagnostic Tools Layer
Safe read-only tools for IT diagnostics.
Risky tools require approval gate before execution.
All tools return structured dicts for agent reasoning.
"""
```

### prompts.py
```python
"""
Automation Support Agent — Prompt Library
All LLM prompts centralised here.
Version each prompt with a comment when changed.
Never hardcode prompts inside app.py or tools.py.
"""
```

### report.py
```python
"""
Automation Support Agent — Report Generation Layer
Transforms raw tool output into structured JSON support summaries.
LLM interprets evidence — never guesses beyond provided data.
Output schema is fixed for integration with ticketing systems.
"""
```

### README.md
```markdown
# Automation Support Agent

> Enterprise IT support automation using Agentic AI
> Built during 30-day Agentic AI Engineering roadmap

## Problem
Oracle EE support engineers handle hundreds of tickets daily.
Many follow predictable diagnostic patterns — check disk,
check processes, check OS version. This agent automates the
diagnostic layer, freeing engineers for complex escalations.

## Architecture
```
Ticket → Classifier → Tool Router → Diagnostic Tool
       → Approval Gate (risky only) → Report Generator
       → Structured JSON → Ticket System Update
```

## Tech Stack
- Python 3.11
- OpenAI Agents SDK
- OpenRouter (LLM provider)
- Model: meta-llama/llama-3.3-70b-instruct

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API key
python3 app.py
```

## Issue Categories
- DISK — low disk space, storage full
- UPGRADE — macOS upgrade stuck or failed
- PACKAGING — pkg install failure, notarization error
- APPLICATION — app crash, won't launch
- NETWORK — VPN, connectivity issues
- UNKNOWN — cannot classify with confidence

## Author
Senior IT Support Engineer — 20 years Oracle EE experience
Transitioning into Agentic AI Engineering
```

### requirements.md
```markdown
# Automation Support Agent — MVP Requirements

## Issue Categories
| Category | Examples |
|---|---|
| DISK | Low disk space, storage full, large file warnings |
| UPGRADE | macOS upgrade stuck/failed, version mismatch |
| PACKAGING | pkg install failure, notarization error, code signing |
| APPLICATION | App crash, won't launch, license error (Citrix, Zoom) |
| NETWORK | VPN not connecting, intermittent drops, DNS issues |
| UNKNOWN | Cannot classify with confidence |

## Tools — SAFE vs RISKY
| Tool | Type | Auto-run? |
|---|---|---|
| check_disk_space() | SAFE | Yes |
| check_os_version() | SAFE | Yes |
| check_running_processes() | SAFE | Yes |
| read_sample_log() | SAFE | Yes |
| clear_cache() | RISKY | Approval required |
| reinstall_package() | RISKY | Approval required |
| force_reboot() | RISKY | Approval required |

## Output Schema (JSON)
```json
{
  "issue_category": "DISK",
  "confidence_score": 0.95,
  "tools_invoked": ["check_disk_space"],
  "findings": "2-3 sentences describing what was found",
  "root_cause": "one sentence root cause",
  "recommendation": "specific next step for engineer",
  "approval_required": false,
  "approval_reason": null,
  "summary": "one sentence executive summary"
}
```

## Acceptance Criteria
- [ ] Classifier correctly categorises 8/10 test tickets
- [ ] SAFE tools run automatically without prompting
- [ ] RISKY tools always trigger approval gate
- [ ] Output is valid JSON matching the schema above
- [ ] UNKNOWN category handled gracefully — no tool called
- [ ] Low confidence (<0.6) routes to human review
```

---

## eval_cases.md — Start Your Test Cases

```markdown
# Evaluation Cases — Automation Support Agent

| # | Ticket | Expected Category | Expected Tool | Pass? |
|---|---|---|---|---|
| 1 | My Mac says startup disk almost full | DISK | check_disk_space | - |
| 2 | Citrix crashes immediately on launch | APPLICATION | check_running_processes | - |
| 3 | macOS upgrade stuck at 75% | UPGRADE | check_os_version | - |
| 4 | VPN package notarization failed | PACKAGING | check_os_version | - |
| 5 | My laptop is slow | DISK | check_disk_space | - |
| 6 | Cannot connect to VPN from home | NETWORK | check_running_processes | - |
| 7 | Error code 11001 | UNKNOWN | none — human review | - |
| 8 | Everything is broken | UNKNOWN | none — human review | - |
| 9 | My computer is hot | UNKNOWN/APPLICATION | check_running_processes | - |
| 10 | Zoom crashes only on video calls | APPLICATION | check_running_processes | - |
```

---

## Notes for Day 8

### Why separate files matter

```
app.py    → if classifier logic changes, only app.py changes
tools.py  → if you add a new tool, only tools.py changes
prompts.py → if you tune a prompt, only prompts.py changes
report.py  → if output schema changes, only report.py changes
```

This is the same principle as your Oracle EE Health Check Script v2.0
modular structure — separate modules for each function. You already
know this pattern. You are applying it to AI engineering.

### OpenAI Agents SDK — key import to know

```python
from agents import Agent, Runner, Tool
```

You will use this from Day 10 onwards. Today just install it and
verify it imports cleanly:

```python
python3 -c "from agents import Agent; print('SDK ready')"
```

If you see `SDK ready` — Day 8 install is complete.

---

## Verify Everything is in Place

```bash
# Check folder structure
find projects/automation_support_agent -type f

# Check SDK installed
python3 -c "from agents import Agent; print('OpenAI Agents SDK ready')"

# Check requirements.txt updated
cat requirements.txt | grep agents
```

Expected output from find:
```
projects/automation_support_agent/app.py
projects/automation_support_agent/tools.py
projects/automation_support_agent/prompts.py
projects/automation_support_agent/report.py
projects/automation_support_agent/requirements.md
projects/automation_support_agent/README.md
projects/automation_support_agent/eval_cases.md
```

---

## Git Commit

```bash
git add .
git commit -m "Day 8: project skeleton for Automation Support Agent"
git push
```

---

## Interview Questions — Day 8

### Q1 — Why did you choose OpenAI Agents SDK over LangChain or smolagents?

I chose OpenAI Agents SDK for three reasons. First, it has built-in
guardrails and approval gate support — critical for enterprise support
automation where agents must never take destructive actions without human
confirmation. Second, the tool definition pattern is clean and explicit —
each tool is a typed Python function with a docstring the agent reads to
decide when to call it. Third, it is production-closer than smolagents —
smolagents is excellent for learning and prototyping but lacks the
enterprise safety features I need. LangChain is powerful but adds
significant abstraction complexity that would slow down a beginner.
For a 30-day portfolio project targeting enterprise roles, OpenAI Agents
SDK gives the best balance of capability, safety, and clarity.

### Q2 — What does each file in your project skeleton do?

My project has four core files each with one responsibility.
app.py is the orchestration layer — it runs the main agent loop,
calls the classifier, routes to tools, and calls the report generator.
tools.py contains all diagnostic tool functions — each returns a
structured dict the agent reasons over. prompts.py holds every LLM
prompt string — centralised so I can version and tune them without
touching logic files. report.py takes the classifier output and tool
results, calls the LLM to interpret the evidence, and returns a
structured JSON report matching a fixed schema. Separating these files
means I can change any one part without touching the others — the same
modular design I used in my Oracle EE Health Check Script v2.0.

### Q3 — What is the difference between a tool and a prompt?

A prompt is an instruction to the LLM — it tells the model what role
to play, what to do, and how to format its output. A tool is a Python
function the agent calls to interact with the real world — reading disk
usage, checking processes, running a cleanup script. Prompts live in
the model's context window. Tools live in the Python runtime and return
real data. In my agent the classifier prompt tells the LLM how to
categorise a ticket. The check_disk_space tool actually reads the disk
and returns real numbers. The LLM reads the tool result and interprets
it — that combination of real data plus LLM reasoning is what makes an
agent more powerful than a chatbot or a script alone.

---

## Expected Outputs by End of Day

- [ ] `pip install openai-agents` successful
- [ ] `requirements.txt` updated
- [ ] 7 files created in `projects/automation_support_agent/`
- [ ] Docstring written in each file
- [ ] `python3 -c "from agents import Agent; print('SDK ready')"` passes
- [ ] `notes/day08-framework-choice.md` written
- [ ] Git committed and pushed

---

*Day 08 complete — skeleton ready, framework chosen, structure in place.
Day 9 is writing the MVP requirements document. Day 10 is the first
real code — the issue classifier.*
