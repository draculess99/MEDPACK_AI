# Committee Freeze Fix v2

This patch was applied after the Stage 2 committee button still appeared to hang.

## Root cause

The main Streamlit committee button could still enter the remote/streaming committee path when Remote LLM Mode was selected. That path can wait on external LLM/network calls before falling back, so the UI may look frozen.

## What changed

- The main **Run MedPack Committee Decision** button now uses the local zero-token committee path directly.
- The frontend no longer calls `/api/run-medpack-committee-stream` from the main button.
- The frontend sends `force_local_committee=true` with the committee request.
- The backend now honors `force_local_committee=true` and also defaults to `MEDPACK_FORCE_LOCAL_COMMITTEE=true`.
- Remote LLM committee mode is effectively bypassed for the main demo button unless you intentionally disable the force-local safety setting later.

## Expected behavior

- Prediction button works as before.
- Committee button should return quickly with a local deterministic committee decision.
- The committee still uses Stage 2 usable-stock logic.
- No LLM/API tokens are used by the main committee button.

## Optional advanced setting

Only if you later want to re-enable remote LLM committee testing:

```env
MEDPACK_FORCE_LOCAL_COMMITTEE=false
USE_LLM_AGENTS=true
GROQ_API_KEY=your_key
```

For the portfolio/demo version, keep the force-local default enabled.
