# Groq Token Meter v4 Persistent Fix

This patch makes the Groq token meter harder to lose during Streamlit reruns.

## What changed

- The frontend now writes the latest LLM usage metadata to `database/llm_usage_state.json`.
- The sidebar meter reloads that file if Streamlit session state gets reset or rerendered.
- The sidebar now shows whether `GROQ_API_KEY` is visible to the Streamlit process.
- Failed Groq attempts are recorded with a failure status instead of silently looking like a broken zero-token meter.
- Successful Groq responses record prompt, completion, total tokens, provider, model, and source.

## Important behavior

If Groq fails before returning a response, there are no usage tokens to report. The meter correctly stays at 0, but the sidebar will now show the failure status.

If Groq returns a response but JSON parsing fails, tokens are still preserved because usage is recorded before parsing.
