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
from tools import TOOL_REGISTRY, SAFE_TOOLS, RISKY_TOOLS
from report import generate_report

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

    Your task: classify the support ticket below into exactly ONE category.

    Categories and when to use them:
    - DISK: storage full, cannot save files, low disk space warnings
    - UPGRADE: macOS upgrade stuck, failed, or cancelled for any reason
            (even if the reason was disk space — the PRIMARY issue is upgrade)
    - PACKAGING: pkg install failure, notarization error, code signing issue
    - APPLICATION: app crash, won't launch, application error, ICA failure
    - NETWORK: VPN issues, connectivity problems, network errors
    - UNKNOWN: genuinely cannot determine — use sparingly

    Rules:
    - Output ONLY a JSON object — no explanation, no reasoning, no preamble
    - Do NOT write any text before or after the JSON
    - Do NOT explain your thinking
    - If log shows upgrade failed due to disk: category is UPGRADE (not DISK)
    - If log shows app crash: category is APPLICATION (not UNKNOWN)
    - confidence must be 0.0 to 1.0
    - reason must be one sentence maximum

    Output format — EXACTLY this, nothing else:
    {{"category": "DISK", "confidence": 0.95, "reason": "one sentence"}}

    Ticket or log to classify:
    {description}"""

    raw = call_llm([{"role": "user", "content": prompt}], temperature=0)
    result = safe_parse_json(raw)

    if result.get("category") not in CATEGORIES:
        log.warning(f"Invalid category: {result.get('category')} — defaulting to UNKNOWN")
        result["category"] = "UNKNOWN"
        result["confidence"] = 0.0

    log.info(f"Classified: {result['category']} ({result['confidence']})")
    return result

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
    # Step 4: Generate structured report
    print(f"\nGenerating Report...")
    report = generate_report(description, classification, tool_result)

    print(f"\nStructured Report:")
    print(json.dumps(report, indent=2))
    print(f"{'─'*60}\n")

    return {
        "ticket":         description,
        "classification": classification,
        "tool_result":    tool_result,
        "report":         report,          # ← new field
    }

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

    