import os, time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Try models in order until one works
MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openrouter/auto",
]

def call_with_fallback(messages):
    for model in MODELS:
        try:
            print(f"Trying model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
            )
            print(f"Success with: {model}")
            return response
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limited on {model}, trying next...")
                time.sleep(5)
                continue
            else:
                raise e
    raise Exception("All models rate limited. Wait 5 minutes and retry.")

response = call_with_fallback([
    {"role": "system", "content": "You are an Enterprise IT support assistant. Ptovide answer in 5 sentence in a bullet points"},
    {"role": "user",   "content": "My MacBook disk is showing 95% full. What should I check?"}
])

print("\n--- RESPONSE ---")
print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")