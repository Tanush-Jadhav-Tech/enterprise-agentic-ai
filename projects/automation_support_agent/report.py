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
    "openrouter/auto",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
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