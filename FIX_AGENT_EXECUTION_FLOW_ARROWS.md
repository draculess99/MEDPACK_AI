# Agent Execution Flow Arrow UI Fix

This patch updates the MedPack AI Agentic Committee tracker from a plain card grid into a cleaner command-center execution flow.

## What changed

- Replaced the simple wrapped card grid with a directional flow map.
- Added subtle arrows between agents in each row.
- Added row handoff indicators between Step 3 → Step 4 and Step 6 → Step 7.
- Added a small legend for Complete / Running / Queued.
- Preserved active-step highlighting.
- Kept the layout responsive so it stays inside the page width.
- Did not change Groq, token metering, prediction, Stage 1-6 logic, or backend endpoints.

## Updated file

- `frontend/dashboard.py`

## Expected display

The agent tracker should now read like this:

```text
Step 1 → Step 2 → Step 3
       Step 3 → Step 4 ↓
Step 4 → Step 5 → Step 6
       Step 6 → Step 7 ↓
Step 7 → Step 8 → Step 9
```

The tracker should look more like a control-tower flow instead of disconnected green boxes.
