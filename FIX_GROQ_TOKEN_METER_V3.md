# Groq Token Meter v3 Fix

This patch applies the Groq token-meter fix directly to the latest uploaded app.

## What changed

- The Streamlit frontend now loads `.env` itself when started directly with `streamlit run frontend/dashboard.py`.
- Groq token usage is recorded immediately after the Groq HTTP response arrives, before JSON parsing or validation.
- If Groq returns text but the JSON parse fails, the app still preserves the Groq token usage and updates the sidebar meter.
- The sidebar meter reads from `st.session_state["last_llm_usage"]` and `st.session_state["current_tokens"]`.
- Session totals are updated at the moment of the Groq response and are not added a second time during the final render.

## Expected behavior

When Remote LLM Mode + Groq is selected and Groq returns a response, the sidebar should show non-zero tokens, such as:

```text
Last LLM call: 1,234 tokens
Session total: 1,234
```

The committee note should also show:

```text
Groq LLM mode used. Tokens reported: ...
Prompt: ... · Completion: ... · Source: groq_usage
```

If it still shows zero, then the Groq call did not reach a successful HTTP response. In that case, check that `GROQ_API_KEY` is in your `.env` and that you restarted the app after editing `.env`.
