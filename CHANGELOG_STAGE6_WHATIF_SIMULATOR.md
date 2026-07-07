# Stage 6 - What-If Surge Simulator

This patch adds the missing what-if simulator layer on top of the existing Stage 1-5 MedPack AI Control Tower.

## What Stage 6 adds

- Scenario playbooks for:
  - ED Surge +40%
  - ICU Respiratory Spike
  - Flu Season Demand
  - Supplier Delay +5 Days
  - Mass Casualty Mode
  - Weekend Staffing Constraint
  - Surgery Schedule Spike
- A standalone dashboard simulator section:
  - `🌪️ Stage 6 What-If Surge Simulator`
- A reference tab:
  - `🌪️ Stage 6 Scenarios`
- Optional custom shock controls:
  - demand multiplier
  - added supplier delay days
  - stock loss units
  - acuity delta
  - pack-time multiplier
- Compare-all mode to rank all scenarios by risk.
- Scenario output pushed through:
  - Stage 2 usable-stock logic
  - Stage 3 supplier/transfer/substitute action plan
  - Stage 4 cost/waste/ROI analysis
  - Stage 5 command-center priority/action cards

## New backend files

- `backend/stage6_whatif_simulator.py`

## New data files

- `database/scenario_playbooks.json`

## New API endpoints

- `GET /api/stage6-scenarios`
- `POST /api/stage6-whatif-simulator`

## Updated files

- `backend/server.py`
- `frontend/dashboard.py`
- `README.md`

## Demo flow

1. Select an item and department in the sidebar.
2. Open `🌪️ Stage 6 What-If Surge Simulator`.
3. Choose a scenario such as `Mass Casualty Mode` or `Supplier Delay +5 Days`.
4. Click `🌪️ Run What-If Simulator`.
5. Review:
   - baseline vs scenario demand
   - baseline vs scenario true shortage gap
   - priority shift
   - net value delta
   - scenario Stage 5 action cards

## Safety

Stage 6 is deterministic/local. It does not call Groq, Gemini, streaming routes, or remote LLM APIs. It uses the existing Stage 2-5 logic to compute the scenario impact.
