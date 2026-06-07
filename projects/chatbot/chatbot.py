import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = (
    "You are an expert IT support assistant for Oracle Enterprise Engineering. "
    "You help diagnose issues with macOS, networking, applications, and packages. "
    "Always ask for the OS version and affected application before diagnosing. "
    "Never suggest deleting system files. Keep responses under 150 words. "
    "Always respond in structured format: Issue, Probable Cause, Next Step."
)

conversation = [{"role": "system", "content": SYSTEM_PROMPT}]

MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/auto",
]

def call_with_fallback(messages):
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=300,
            )
            return response
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limited on {model}, trying next...")
                time.sleep(5)
                continue
            else:
                raise e
    raise Exception("All models rate limited. Wait 5 minutes and retry.")

print("=" * 50)
print("Oracle EE IT Support Chatbot")
print("Type 'quit' to exit | 'history' to see conversation")
print("=" * 50)
print()

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("quit", "exit"):
        print("Session ended. Goodbye.")
        break

    if user_input.lower() == "history":
        print("\n--- Conversation History ---")
        for msg in conversation:
            if msg["role"] != "system":
                print(f"{msg['role'].upper()}: {msg['content'][:100]}...")
        print("---\n")
        continue

    conversation.append({"role": "user", "content": user_input})

    try:
        response = call_with_fallback(conversation)
        reply = response.choices[0].message.content
        conversation.append({"role": "assistant", "content": reply})

        print(f"\nAssistant: {reply}")
        print(f"[Tokens: {response.usage.total_tokens}]")
        print()

    except Exception as e:
        print(f"Error: {e}")
        conversation.pop()