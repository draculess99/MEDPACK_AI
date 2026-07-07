# Agent Tracker Presentable UI Fix

This patch replaces the oversized native Streamlit success/info blocks with a compact, polished, responsive execution tracker.

## What changed

- Replaced the large 3-column Streamlit alert-card layout.
- Added a compact responsive card grid that wraps automatically.
- Added a custom progress bar inside the tracker panel.
- Kept the running/queued/complete light-up behavior.
- Prevented horizontal overflow across the screen.
- Rendered the tracker with `st.markdown(..., unsafe_allow_html=True)` so it displays as UI instead of raw HTML text.

## Updated file

- `frontend/dashboard.py`

## Expected result

The committee execution tracker should now look like a compact command-center timeline rather than huge green blocks.
