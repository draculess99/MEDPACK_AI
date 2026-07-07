# Stage 2 Committee Freeze Fix

This patch fixes the issue where the **Run MedPack Committee Decision** button could appear to freeze.

## Root cause

The prediction endpoint was working, but the committee path could wait on remote/streaming agent calls without a clean UI-side timeout or fallback. If Remote LLM Mode was selected, if `USE_LLM_AGENTS=true`, or if an API/model setting was slow or invalid, Streamlit could sit waiting and look frozen.

## What changed

### `backend/agents/adk_agents.py`

- Rebuilt the committee runner with guaranteed local fallback.
- Added short remote LLM timeouts using `REMOTE_LLM_TIMEOUT_SECONDS` with an 8-second default.
- Added Groq model normalization so old decommissioned defaults such as `llama3-8b-8192` are replaced with `llama-3.3-70b-versatile`.
- Updated streaming committee mode so it always emits a final local committee result if remote mode fails or times out.
- Preserved the same response keys used by the dashboard:
  - `demand_forecast_agent`
  - `inventory_risk_agent`
  - `packing_priority_agent`
  - `clinical_safety_agent`
  - `final_recommendation_agent`
  - `committee_summary`
  - `tokens_used`
  - `mode_note`

### `frontend/dashboard.py`

- Added explicit timeouts to committee requests.
- Added a Streamlit spinner so the user sees what is happening.
- Added fallback logic: if the remote/streaming committee does not return a final payload, the UI automatically calls the local zero-token committee.
- Added a caption under the committee panel explaining that the Stage 2 freeze guard is active.

## Expected behavior now

- **Predict 24-Hour Supply Demand** should continue to work.
- **Run MedPack Committee Decision** should no longer freeze.
- If remote mode has a problem, the app should display a warning and return the local deterministic committee decision.
- Local mode should use zero tokens and return quickly.

## Files changed

- `backend/agents/adk_agents.py`
- `frontend/dashboard.py`
- `FIX_COMMITTEE_FREEZE_STAGE2.md`
