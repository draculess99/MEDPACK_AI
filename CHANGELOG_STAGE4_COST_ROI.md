# Stage 4: Cost, Waste & ROI Executive Dashboard

Stage 4 turns the Stage 3 operational action plan into an executive/business-value view.

## Added

- `backend/stage4_roi.py`
  - Calculates shortage dollars at risk.
  - Calculates waste/expiry/recalled-stock value exposure.
  - Estimates emergency-order premium and transfer labor cost.
  - Estimates nurse/search time and packing-time value.
  - Estimates overstock value and monthly carrying cost.
  - Produces an executive recommendation and ROI-style summary.

- `database/cost_assumptions.json`
  - Transparent demo assumptions for labor rates, stockout multipliers, emergency order fees, carrying cost, and default item-category costs.

## New backend endpoints

- `GET /api/stage4-reference-data`
- `POST /api/stage4-roi-analysis`

## Dashboard changes

- Added `Estimated Unit Cost ($)` to the sidebar so ROI can be tuned interactively.
- Added `💰 Stage 4: Cost, Waste & ROI Executive Dashboard` after the Stage 3 action plan.
- Added `💰 Stage 4 Standalone Cost, Waste & ROI Executive View` below the main Top 5 queue.
- Added `💰 Stage 4 Finance` tab showing transparent financial assumptions.
- Added `Cost / Waste / ROI Agent Insights` to the no-freeze committee output.

## Committee changes

The freeze-safe Streamlit committee now generates a local Stage 4 financial view without calling Groq/Gemini/backend.

When Groq mode is selected, Groq still only rewrites the local facts into a more LLM-like response; the Stage 4 numbers are calculated locally and are not changed by Groq.

## Demo note

Stage 4 values are portfolio/capstone estimates, not audited hospital financial guidance.
