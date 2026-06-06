import os, json, re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SAMPLE_LOG = """
2024-01-15 09:12 INFO  Starting macOS 14.4 upgrade
2024-01-15 09:35 ERROR Download failed: disk full
2024-01-15 09:35 ERROR Upgrade aborted: insufficient space
2024-01-15 09:36 WARN  Rolling back to previous state
2024-01-15 09:37 INFO  Rollback complete
"""

response = client.chat.completions.create(
    model="openrouter/auto",
    messages=[
        {"role": "system", "content": (
            "You are an IT log analyst. "
            "Use ONLY what is in the log. Do not guess. "
            "Reply ONLY in JSON with no markdown, no code blocks, no extra text: "
            '{"root_cause":"...","severity":"LOW|MEDIUM|HIGH|CRITICAL","recommendation":"..."}'
        )},
        {"role": "user", "content": f"Analyse this log:\n{SAMPLE_LOG}"}
    ],
    temperature=0,
)

# Safe parser — handles markdown code blocks and empty responses
raw = response.choices[0].message.content
print(f"Raw response: {raw}\n")

# Strip markdown code fences if present
clean = re.sub(r"```(?:json)?", "", raw).strip()

if not clean:
    print("Empty response received — model did not return content")
else:
    result = json.loads(clean)
    print(json.dumps(result, indent=2))
    print(f"\nTokens used: {response.usage.total_tokens}")