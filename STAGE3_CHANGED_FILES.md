# Stage 3 Changed Files

## Added

- `backend/transfer_optimizer.py`
- `backend/supplier_risk.py`
- `backend/substitution_engine.py`
- `backend/stage3_action_plan.py`
- `database/vendor_state.json`
- `database/substitution_rules.json`
- `CHANGELOG_STAGE3_SUPPLIER_TRANSFER.md`
- `STAGE3_CHANGED_FILES.md`

## Modified

- `backend/server.py`
  - Added Stage 3 API imports and endpoints.
  - Health check now reports Stage 3 availability.

- `backend/fast_committee.py`
  - Fast no-freeze committee now includes a Stage 3 action-plan result.

- `frontend/dashboard.py`
  - Added Stage 3 dashboard panel.
  - Added transfer/supplier/substitute tables.
  - Added Stage 3 data tab.
  - Groq LLM-style rewrite context now includes Stage 3 facts.
  - Committee output now includes a Supplier & Transfer Agent section.

- `.env.example`
  - Added `MEDPACK_STAGE3_ENABLED=true` documentation flag.
