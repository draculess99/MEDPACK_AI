# Groq Token Counter Fix

This patch fixes the sidebar token meter when Groq is selected.

## What changed

- The Groq UI call now captures `usage.total_tokens` from the Groq response.
- If Groq returns `prompt_tokens` and `completion_tokens` but not `total_tokens`, the app sums them.
- If Groq/compatible responses omit usage metadata entirely, the app uses a rough token estimate so the meter no longer stays at zero after a real LLM rewrite.
- The sidebar gauge now says **Last LLM Tokens** and dynamically scales above 1,000 tokens.
- The sidebar now also shows **Last LLM call** and **Session total**.
- The committee output now displays prompt/completion/source details when Groq is used.
- Remote mode detection now recognizes `remote_groq_llm_like_frontend_safe` instead of only the exact string `remote`.

## Expected behavior

When Groq successfully rewrites the committee output, the sidebar should show a non-zero token count and the committee panel should show:

```text
Groq LLM mode used. Tokens reported: <number>
Prompt: <number> · Completion: <number> · Source: groq_usage or estimated
```

If Groq fails or no `GROQ_API_KEY` is available, the app still falls back to the local no-freeze committee and reports zero tokens.
