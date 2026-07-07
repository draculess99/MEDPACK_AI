# Stage 2 Upgrade — Forecast + Usable Stock Integration

Stage 2 connects the Stage 1 traceability layer directly into the forecast and packing decision logic.

## What changed

### 1. New usable-stock intelligence module

Added:

- `backend/usable_stock.py`

This calculates:

- total stock
- usable stock
- expired stock
- recalled stock
- expiring-soon stock
- active task-reserved stock
- wrong-location stock
- transferable stock from other departments
- true shortage gap
- post-transfer shortage gap

The key Stage 2 equation is:

```text
total stock
- expired/recalled unsafe stock
- active task-reserved stock
= usable stock
```

The app now compares the forecast against usable stock instead of blindly comparing against total stock.

### 2. New API endpoint

Added:

```text
POST /api/usable-stock-analysis
```

This returns a full Stage 2 analysis for the selected item and department.

### 3. Forecast pipeline updated

Updated:

- `/api/predict-supply-demand`
- `/api/shortage-risk`
- `/api/run-medpack-committee`
- `/api/run-medpack-committee-stream`
- `/api/packing-queue`

The main committee pipeline now uses `shortage_risk_using_usable_stock` as the shortage result.

### 4. Top 5 queue upgraded

The Top 5 queue now shows:

- total stock
- usable stock
- unsafe stock
- task-reserved stock
- transferable stock
- true shortage gap
- post-transfer gap

This makes the queue more honest: an item may look safe by total stock but still be risky after unsafe and reserved stock are removed.

### 5. Dashboard upgraded

Added visible Stage 2 panels:

- `🧮 Stage 2: Forecast vs Usable Stock` in the live prediction output
- `🧮 Stage 2 Standalone Usable-Stock Check` in the Control Tower section

These panels show the difference between total stock and usable stock.

### 6. Agent committee upgraded

The Inventory Risk Agent now explains risk using usable stock instead of raw current stock.

## Why this matters

Before Stage 2:

```text
Forecasted Demand - Current Stock = Shortage Gap
```

After Stage 2:

```text
Forecasted Demand - Usable Stock = True Shortage Gap
```

That means MedPack AI can now detect the dangerous case where total stock looks fine, but usable stock is actually low because some units are expired, recalled, already assigned, or in the wrong location.
