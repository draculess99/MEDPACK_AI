# Committee Freeze Fix v3 - Hard Bypass

This patch changes the MedPack Committee button to use a new fast local endpoint:

`POST /api/run-medpack-committee-fast`

The fast endpoint deliberately avoids remote LLM calls, streaming, joblib/XGBoost model loading, and memory-event writes. It still returns a committee-style decision using Stage 2 usable-stock logic and a deterministic local forecast formula.

## Why this was needed
Your `.env` still had `USE_LLM_AGENTS=true` and API keys. Any missed route could drift into remote LLM behavior and make Streamlit appear frozen. v3 makes the main button bypass those routes entirely.

## Changed files
- `backend/fast_committee.py`
- `backend/server.py`
- `frontend/dashboard.py`
- `app.py`
- `.env.example`

## Behavior
- Main committee button: no Groq, no Gemini, no streaming, no heavy model load.
- Old `/api/run-medpack-committee` route delegates to the fast endpoint by default.
- Old streaming route is disabled by default.
- `app.py` forces committee safety environment variables at startup, even if `.env` has `USE_LLM_AGENTS=true`.
