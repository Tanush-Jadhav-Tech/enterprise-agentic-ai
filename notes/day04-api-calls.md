# Day 04 — First LLM API Calls

## Environment
- SDK: openai==1.51.0 via OpenRouter
- Model: meta-llama/llama-3.3-70b-instruct:free + openrouter/auto fallback
- Base URL: https://openrouter.ai/api/v1

## Scripts completed
1. simple_completion.py — basic API call, tokens logged
2. classify_issue.py — 5 test cases, confidence scores, temperature=0
3. summarize_log.py — log → structured JSON, safe parser added

## Key learnings
- response.choices[0].message.content — where the answer lives
- temperature=0 for classification, 0.1 for general responses
- Always log usage.total_tokens for cost tracking
- Free models sometimes wrap JSON in markdown — always strip it
- openrouter/auto handles rate limiting automatically

## Tokens per call (approx)
- simple_completion: ~1687 tokens
- classify_issue: ~150 tokens per call
- summarize_log: 217 tokens

## Issues faced and fixed
- pip not found → activate .venv first
- httpx proxies error → downgrade to httpx==0.27.2
- openai quota error → switched to OpenRouter free tier
- JSON decode error → added re.sub to strip markdown fences
