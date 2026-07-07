# Stage 4 Changed Files

## Added

- `backend/stage4_roi.py`
- `database/cost_assumptions.json`
- `CHANGELOG_STAGE4_COST_ROI.md`
- `STAGE4_CHANGED_FILES.md`

## Modified

- `backend/server.py`
  - Added Stage 4 health flag.
  - Added Stage 4 reference endpoint.
  - Added Stage 4 ROI analysis endpoint.
  - Added Stage 4 payload into the full committee response path.

- `backend/fast_committee.py`
  - Added Stage 4 ROI analysis to the guaranteed-fast local committee payload.
  - Added `stage4_financial_impact_agent`.

- `frontend/dashboard.py`
  - Added sidebar estimated unit-cost input.
  - Added Stage 4 executive metrics and breakdown panel.
  - Added Stage 4 standalone API panel.
  - Added Stage 4 financial assumptions tab.
  - Added Stage 4 committee expander.
  - Added Stage 4 context into the Groq LLM-like rewrite prompt.
