# Stage 1 Changed Files

## New files

- `backend/traceability.py`
- `backend/compliance_rules.py`
- `backend/scan_events.py`
- `backend/par_recommendation.py`
- `backend/task_manager.py`
- `CHANGELOG_STAGE1_CONTROL_TOWER.md`
- `STAGE1_CHANGED_FILES.md`

## Modified files

- `backend/server.py`
  - Added `/api/compliance-alerts`
  - Added `/api/scan-event`
  - Added `/api/scan-events`
  - Added `/api/par-recommendation`
  - Added `/api/packing-tasks`
  - Updated `/api/inventory` and `/api/packing-queue` to return enriched traceability records.

- `frontend/dashboard.py`
  - Added the new **Stage 1 Control Tower Upgrade** dashboard section.
  - Added five tabs: Traceability, Compliance Alerts, Scan Simulator, Dynamic PAR, Packing Tasks.

- `backend/data_loader.py`
  - Inventory generation now adds traceability fields when a new inventory snapshot is created.

- `app.py`
  - Startup now ensures Stage 1 traceability fields exist before the dashboard opens.

- `README.md`
  - Updated architecture, features, and API endpoint table.

- `database/inventory_state.json`
  - Existing 98 inventory records now include lot/UDI/barcode/expiration/PAR/vendor/location/recall/storage fields.

## What to look for when running

After running:

```bash
python app.py
```

Open the dashboard and scroll below **Top 5 Supplies to Pack First**. You should see:

```text
🏥 Stage 1 Control Tower Upgrade
```

That section contains the new operational features.
