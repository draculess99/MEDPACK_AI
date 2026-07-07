# Stage 6 Changed Files

## Added

- `backend/stage6_whatif_simulator.py`
- `database/scenario_playbooks.json`
- `CHANGELOG_STAGE6_WHATIF_SIMULATOR.md`
- `STAGE6_CHANGED_FILES.md`

## Modified

- `backend/server.py`
  - added Stage 6 imports
  - added `GET /api/stage6-scenarios`
  - added `POST /api/stage6-whatif-simulator`
  - added Stage 6 flag to `/health`

- `frontend/dashboard.py`
  - added `🌪️ Stage 6 What-If Surge Simulator`
  - added compare-all scenario mode
  - added optional custom shock controls
  - added `🌪️ Stage 6 Scenarios` reference tab
  - added Stage 6 health flag in runtime panel

- `README.md`
  - added Stage 6 summary section
