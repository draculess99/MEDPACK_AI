# Sidebar-Responsive Queue Patch

This patch updates the uploaded MedPack AI app so the **Top 5 Supplies to Pack First** table is no longer static.

## What changed

- Streamlit now sends the active sidebar scenario to Flask when loading the Top 5 queue.
- `/api/packing-queue` now supports `POST` JSON payloads as well as basic `GET` checks.
- Department filters the inventory records used for the queue.
- Operational controls now affect queue scoring:
  - Patient Volume
  - Acuity Level
  - Procedure Count
  - Current Stock
  - Recent Usage Rate
  - Supplier Delay
  - Hour of Day
  - Day of Week
  - Season
- The backend adds a local expert-system pressure score by category/department/season/time.
- The queue still runs in local zero-token mode using the existing ML + rules + optimizer pipeline.

## Expected behavior

- Changing **Department** should change which supplies are considered.
- Changing sliders/season should change risk, pack quantity, priority score, pressure score, and sometimes the order of the Top 5 rows.

## Validation

Targeted queue tests passed:

```text
2 passed in 2.95s
```
