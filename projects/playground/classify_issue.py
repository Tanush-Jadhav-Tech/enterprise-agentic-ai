import os, json, time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

CATEGORIES = ["DISK","UPGRADE","PACKAGING","APPLICATION","NETWORK","UNKNOWN"]

def classify_issue(description: str) -> dict:
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {"role": "system", "content": (
                "You are an IT support classifier for Oracle EE. "
                f"Classify into one of: {', '.join(CATEGORIES)}. "
                "Reply ONLY in JSON: "
                '{"category":"DISK","confidence":0.95,"reason":"one line"}'
            )},
            {"role": "user", "content": description}
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)

test_cases = [
    "My Mac says the startup disk is almost full",
    "Citrix Workspace crashes immediately on launch",
    "The macOS 14 upgrade is stuck at 75%",
    "clear_cache_mac.sh fails — permission denied on Trash",
    "My laptop is slow",
]

for tc in test_cases:
    r = classify_issue(tc)
    print(f"Issue   : {tc}")
    print(f"Category: {r['category']} ({r['confidence']})")
    print(f"Reason  : {r['reason']}\n")
    time.sleep(2)
