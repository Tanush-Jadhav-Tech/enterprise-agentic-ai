# Day 06 — Interview Framing + Build Your First Chatbot

> Agentic AI Learning Roadmap | Oracle EE IT Support context
> First hands-on project — working CLI chatbot

---

## Study Resources

- OpenAI Python SDK Quickstart — https://platform.openai.com/docs/libraries
- OpenAI Chat Completions API — https://platform.openai.com/docs/guides/text-generation

---

## Core Concepts

| Concept | Definition |
|---|---|
| Chatbot vs Agent | Chatbot has no tools, no loop, no decision-making — it just chats |
| Conversation history | Full message list must be passed on every API call — model has no memory |
| System prompt | Defines chatbot personality and constraints for the whole session |
| Foundation | This chatbot is the base — Day 8 onwards you extend it into a real agent |

---

## Chatbot vs Agent — Critical Difference

| | Chatbot (today) | Agent (Day 8+) |
|---|---|---|
| Tools | None | check_disk_space, clear_cache etc. |
| Memory | You pass history manually | Maintained across tool calls |
| Decision | Only responds | Decides which tool to call |
| Loop | Single turn | Observe → Think → Act → repeat |
| Use | Conversation | Autonomous task resolution |

> A chatbot is NOT an agent. It has no tools, no loop, no decision-making.
> It is the foundation — Day 8 you will add tools and turn it into an agent.

---

## chatbot.py — Full Working Code

```python
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
```

---

## How Conversation History Works

This is the most important concept today. The model has NO memory between calls.
You must pass the full history every time:

```
Turn 1:  messages = [system, user_1]
Turn 2:  messages = [system, user_1, assistant_1, user_2]
Turn 3:  messages = [system, user_1, assistant_1, user_2, assistant_2, user_3]
```

Every turn the list grows by 2 messages (user + assistant).
This is why tokens accumulate and why long conversations cost more.

---

## Terminal Commands

```bash
mkdir -p projects/chatbot
touch projects/chatbot/chatbot.py
code projects/chatbot/chatbot.py
python3 projects/chatbot/chatbot.py
```

---

## 5 Test Prompts — Use These from Your Day 3 Prompt File

Test the chatbot with these real Oracle EE scenarios:

```
1. "My MacBook disk is showing 95% full and I can't save files."
2. "Citrix Workspace crashes immediately when I launch it."
3. "The macOS Sonoma upgrade is stuck at 75% for 2 hours."
4. "I can't install the company VPN, says notarization failed."
5. "My laptop fan is loud and everything is slow."
```

After each response observe:
- Does it ask for OS version before diagnosing?
- Does it stay under 150 words?
- Does it follow Issue / Probable Cause / Next Step format?
- Does the token count grow with each turn?

---

## Session Transcript — Save This in Notes

After testing, save one full session here:

```
You: [your question]
Assistant: [response]
Tokens: [count]

You: [follow-up]
Assistant: [response]
Tokens: [higher count — history is growing]
```

---

## 5 Interview Answers — Practise Aloud

### Q1 — Tell me about yourself and why you are moving into Agentic AI

I am a Senior IT Support Engineer with 20 years of enterprise experience at
Oracle Enterprise Engineering in Pune. Over those 20 years I have built
automation tools that already follow the agent loop without me consciously
knowing it — my Mac Health Check Script detects problems, diagnoses them,
and generates structured HTML reports. My cache cleaning script observes
disk state, asks for approval, acts, and logs the result. I recognised that
what I had been doing manually and in shell scripts could be done by AI
agents at scale, with better reasoning and faster response times. That
realisation led me to start this structured 30-day Agentic AI Engineering
program. I am not switching careers away from IT — I am moving IT support
automation to the next level, combining 20 years of domain expertise with
modern AI engineering skills.

---

### Q2 — What is the difference between a chatbot and an agent?

A chatbot takes a message, calls an LLM, returns a response. It has no
tools, no loop, no decision-making capability. My Day 6 chatbot is a
perfect example — it is a while loop that appends messages and calls the
API. It cannot check your disk, it cannot read a log file, it cannot take
any action in the real world.

An agent is different in three ways. First it has tools — functions it can
call to get real data or take real actions. Second it has a loop — it
observes the result of each tool call and decides the next step. Third it
has stopping conditions — it knows when the task is done. My Automation
Support Agent classifies a ticket, calls the right diagnostic tool, reads
the result, and generates a structured report. The chatbot only talks.
The agent acts.

---

### Q3 — How do you maintain conversation history with the OpenAI API?

The LLM has no memory between API calls. Every call is stateless. To
maintain a conversation you must pass the complete message history on every
request — system prompt, then every user and assistant message in order.

In my chatbot I maintain a Python list called conversation. Every time the
user sends a message I append it as a user role dict. Every time the model
responds I append the reply as an assistant role dict. On the next turn I
pass the entire list. This means token count grows with every turn —
by turn 10 I am sending all previous exchanges plus the new message.
In production agents I would add a context window management strategy —
summarising older turns once the history exceeds a token limit.

---

### Q4 — Why is a system prompt important in an enterprise AI application?

The system prompt is the agent's standing instructions — equivalent to
your SOP document. Without it the LLM behaves like a general assistant
and will suggest anything, including deleting system files, resetting
passwords without verification, or giving advice outside its scope.

In my Oracle EE chatbot the system prompt does four things:
defines the role (Oracle EE IT support), scopes the domains (macOS,
networking, applications, packages), sets safety constraints (never
suggest deleting system files), and specifies the output format
(Issue / Probable Cause / Next Step under 150 words). Every enterprise
AI application needs a system prompt that defines what the agent is,
what it can do, and critically what it must never do.

---

### Q5 — What did you build in your first week of learning?

In Week 1 I built the foundation for my entire portfolio. Day 1 set up
the Python 3.11 environment, Git, and Docker. Day 2 and 3 grounded all
AI concepts in my own Oracle EE tools — I mapped the agent loop to my
clear_cache_mac.sh script and built 10 production-safe prompt pairs from
real support scenarios. Day 4 made three working LLM API scripts — a
completion call, an issue classifier with confidence scoring, and a log
summariser that returns structured JSON. Day 5 produced a full ReAct
trace for a high CPU scenario and documented the five tools my agent will
need. Day 6 built a working CLI chatbot that maintains conversation
history across turns and handles rate limiting with model fallback.
Everything from Week 1 feeds directly into the Automation Support Agent
I start building on Day 8.

---

## What to Observe and Note During Testing

Write answers to these in your session transcript:

| Question | Your observation |
|---|---|
| Does history grow? | Token count should increase each turn |
| Does the model stay in scope? | Should not answer non-IT questions |
| Does it follow the format? | Issue / Probable Cause / Next Step |
| What breaks? | Note any confusing or wrong responses |
| What confuses the model? | Vague inputs, multi-issue tickets |

---

## Expected Outputs by End of Day

- [ ] projects/chatbot/chatbot.py — working CLI chatbot
- [ ] 5 test prompts run and responses observed
- [ ] Session transcript saved in notes/day06-chatbot-test.md
- [ ] 5 interview answers practised aloud (record yourself)
- [ ] Git commit: "Day 6: working CLI chatbot with conversation history"

---

## Git Commit

```bash
cd ~/Documents/work/learning/enterprise-agentic-ai
git add .
git commit -m "Day 6: working CLI chatbot with conversation history and model fallback"
git push
```

---

*Day 06 complete — first working project, conversation history understood,
5 interview answers ready. Day 7 is Week 1 review and first GitHub push.*
