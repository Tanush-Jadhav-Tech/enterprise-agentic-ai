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
