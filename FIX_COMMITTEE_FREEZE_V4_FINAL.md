# Committee Freeze Fix v4 - Final hard bypass

The `Run MedPack Committee Decision` button was still hanging after the previous backend/LLM fixes.

This version changes the behavior more aggressively:

## What changed

1. The committee button no longer calls Flask at all.
2. The committee button no longer calls `/api/run-medpack-committee-fast`.
3. The committee button no longer calls Groq, Gemini, streaming, XGBoost/joblib, or memory writes.
4. The committee result is calculated directly inside `frontend/dashboard.py` using the current sidebar values.
5. After rendering the committee result, Streamlit calls `st.stop()` so the lower live API panels do not refresh during the committee click.
6. `app.py` now forces subprocess environment values:
   - `USE_LLM_AGENTS=false`
   - `DEFAULT_AGENT_MODE=local`
   - `MEDPACK_FORCE_LOCAL_COMMITTEE=true`
   - `MEDPACK_ALLOW_FULL_COMMITTEE_ROUTE=false`
   - `MEDPACK_ALLOW_COMMITTEE_STREAM=false`
7. `app.py` no longer captures backend/frontend stdout pipes, avoiding subprocess pipe-buffer stalls.
8. `frontend/dashboard.py` now reads either `MEDPACK_LOCAL_API_BASE_URL` or `MEDPACK_API_BASE_URL`.

## Expected behavior

- Predict button: uses backend/Stage 2 app logic as before.
- Run MedPack Committee Decision: returns immediately using `streamlit_v4_no_backend_no_llm` mode.
- Tokens used: 0.
- The committee button should not hang even if `.env` contains API keys or `USE_LLM_AGENTS=true`.

## Main file changed

- `frontend/dashboard.py`
- `app.py`
