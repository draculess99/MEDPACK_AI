# MedPack AI Patch Notes

## Completed updates

- Fixed shortage-risk explanations so Critical/High/Medium reasoning accurately reports which threshold was crossed.
- Added `backend/packing_queue.py` so the Top 5 packing queue uses the real ML forecast, shortage rules, and packing optimizer instead of mock dashboard scoring.
- Added `/api/packing-queue` backend endpoint.
- Updated Streamlit dashboard to call `/api/packing-queue` for the Top 5 Supplies to Pack First table.
- Improved mobile/dark-theme readability with `.streamlit/config.toml` and stronger dashboard CSS.
- Changed Flask backend deployment binding from `127.0.0.1` to `0.0.0.0` and added `PORT` support.
- Added Railway/Render-style deployment helper scripts:
  - `start_backend.sh`
  - `start_frontend.sh`
  - `Procfile`
  - `railway.json`
  - `DEPLOYMENT.md`
- Added `gunicorn` to requirements for production backend hosting.
- Added `pytest.ini` so tests can import project modules reliably.
- Added tests for the new packing queue.
- Reduced model training overhead for faster repeatable local tests while keeping the XGBoost-first behavior.
- Rewrote README into a stronger portfolio/capstone submission story.

## Validation

- `python -m compileall -q backend frontend tests app.py`
- `pytest -q`
- Result: `8 passed`


## Windows 11 launcher patch

- Replaced the old minimal `RUN_ME.bat` with a clearer Windows 11 launcher.
- Added `RUN_BACKEND.bat` for starting the Flask API locally.
- Added `RUN_FRONTEND.bat` for starting the Streamlit dashboard locally.
- Added `RUN_TESTS.bat` for running the test suite on Windows.
- Added PowerShell alternatives: `RUN_BACKEND.ps1` and `RUN_FRONTEND.ps1`.
- Updated README and deployment docs to make Windows the primary local workflow.
- Kept `.sh` files only for Linux/macOS/cloud deployment use.

## Windows 11 Local/Remote Mode Switch Patch

- Added left-sidebar **Backend target** switch: Local Backend vs Remote Backend.
- Added left-sidebar **Agent execution** switch: Local AI Mode vs Remote LLM Mode.
- Added safe backend gating so remote LLM calls only happen when `USE_LLM_AGENTS=true` and `GEMINI_API_KEY` is present.
- Added `/health` metadata showing remote LLM readiness and safe default mode.
- Added `.env.example` documenting zero-token defaults and optional remote settings.
- Added tests proving Local Mode uses zero tokens and Remote Mode falls back safely when not configured.
