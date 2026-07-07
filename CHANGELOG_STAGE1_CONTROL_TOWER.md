# Stage 1 Control Tower Upgrade

Added the first operational-control layer on top of the existing MedPack AI forecast/risk/packing pipeline.

## New backend modules

- `backend/traceability.py` — enriches every inventory row with lot number, UDI, barcode, expiration date, PAR level, max stock, location, vendor, recall status, storage type, and last scan state.
- `backend/compliance_rules.py` — detects below-PAR items, expired stock, lots expiring within 30 days, recalled lots, and temperature-sensitive stock.
- `backend/scan_events.py` — simulates barcode/UDI scan events and updates current stock.
- `backend/par_recommendation.py` — recommends dynamic PAR and max-stock levels from forecast, supplier delay, criticality, and supplier reliability.
- `backend/task_manager.py` — creates and updates packing tasks through statuses like NEW, ASSIGNED, PICKING, PACKED, DELIVERED, ESCALATED, and CANCELLED.

## New API endpoints

- `GET/POST /api/compliance-alerts`
- `POST /api/scan-event`
- `GET /api/scan-events`
- `POST /api/par-recommendation`
- `GET/POST/PATCH /api/packing-tasks`

## New dashboard area

A new **Stage 1 Control Tower Upgrade** section appears under the Top 5 packing queue with five tabs:

1. Traceability
2. Compliance Alerts
3. Scan Simulator
4. Dynamic PAR
5. Packing Tasks

## Data changes

`database/inventory_state.json` is now enriched with operational fields such as:

```text
lot_number, udi_code, barcode, expiration_date, location, par_level, max_stock,
vendor_id, vendor_name, last_scan_at, last_scan_event, recall_status,
storage_type, temperature_sensitive
```

The original ML fields are preserved.
