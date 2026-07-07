# Groq Token Meter Fix v2

This patch makes the Groq token meter update more reliably in the Streamlit frontend.

## What changed

1. `frontend/dashboard.py` now loads `.env` itself when the dashboard is run directly with:

   ```bash
   streamlit run frontend/dashboard.py
   ```

   Previously, `.env` was only loaded by `app.py`. If Streamlit was started directly, `GROQ_API_KEY` could be missing from the frontend process, causing Groq mode to fall back to local mode and show zero tokens.

2. Groq token usage is captured immediately after a successful Groq HTTP response, before JSON parsing.

   This means the token meter still updates even if Groq returns non-JSON text and the committee falls back to the local wording.

3. The sidebar gauge now recovers recent Groq usage from `st.session_state` if the visible committee result accidentally loses its token fields.

4. Session totals are guarded by a call id so Streamlit reruns should not double-count the same Groq call.

## Expected behavior

When Remote LLM Mode + Groq is selected and the Groq call succeeds, the sidebar should show non-zero tokens and the committee panel should show:

```text
Groq LLM mode used. Tokens reported: <number>
Prompt: <number> · Completion: <number> · Source: groq_usage or estimated
```

If the Groq API key is missing, invalid, or the Groq call fails before a response is received, the app still falls back safely to local mode. In that case the token meter will remain zero because no successful LLM response was received.
