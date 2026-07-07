# Stage 2 Changed Files

## Added

- `backend/usable_stock.py`
- `CHANGELOG_STAGE2_USABLE_STOCK.md`
- `STAGE2_CHANGED_FILES.md`

## Modified

- `backend/server.py`
  - Added `/api/usable-stock-analysis`
  - Updated prediction and committee flows to calculate usable stock
  - Added Stage 2 health flag

- `backend/packing_queue.py`
  - Top 5 queue now uses usable-stock shortage risk
  - Adds true shortage gap, unsafe stock, reserved stock, and transfer stock columns

- `backend/agents/adk_agents.py`
  - Inventory Risk Agent now talks about usable stock vs total stock
  - Fixed the stream-mode local committee helper call signature

- `frontend/dashboard.py`
  - Adds Stage 2 Forecast vs Usable Stock panel
  - Adds standalone usable-stock check panel
  - Updates Top 5 queue display columns
  - Updates architecture section

## Not modified

- The XGBoost model file was not retrained.
- The core Streamlit + Flask architecture was preserved.
- Stage 1 traceability, scan, PAR, and task features remain in place.
- `.env` is not included in the returned zip for safety.
