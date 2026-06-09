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